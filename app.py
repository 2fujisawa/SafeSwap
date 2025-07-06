from flask import Flask, render_template, request, redirect, url_for, jsonify
from ultralytics import YOLO
import sqlite3
import os
import base64
from io import BytesIO
from PIL import Image
from datetime import datetime, timedelta

# --- Setup ---
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Load YOLOv8 model
model = YOLO('yolov8s.pt')

# Allowed detected objects
allowed_objects = ["bottle", "fork", "spoon", "knife", "cup", "cell phone", "toothbrush"]

# --- Helper functions ---

def query_microplastic_data(object_name):
    conn = sqlite3.connect('microplastics.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM microplastic_data WHERE object_name = ?", (object_name,))
    data = cursor.fetchone()
    conn.close()
    return data

def calculate_spoon_percentage(particles_per_use):
    grams_per_particle = 0.0000002  # 200 nanograms
    spoon_grams = 5.0               # average plastic spoon ~5g
    days = 365 * 10                 # 10 years
    accumulated_mass = particles_per_use * grams_per_particle * days
    return round((accumulated_mass / spoon_grams) * 100, 2)

def get_scan_history():
    conn = sqlite3.connect('microplastics.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT object_name, microplastic_count, risk_level, time_scanned FROM scan_history ORDER BY time_scanned DESC")
    history = cursor.fetchall()
    conn.close()
    return history

def format_history(raw_history):
    history = []
    for obj, count, risk, ts in raw_history:
        dt = None
        if ts is None:
            pass
        elif isinstance(ts, bytes):
            ts = ts.decode()
        if isinstance(ts, str):
            try:
                dt = datetime.fromisoformat(ts) - timedelta(hours=7)
            except ValueError:
                try:
                    dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    pass
        elif isinstance(ts, (int, float)):
            dt = datetime.fromtimestamp(ts)
        elif isinstance(ts, datetime):
            dt = ts

        if dt is None:
            dt = datetime.now()

        history.append({
            'object_name': obj,
            'microplastic_count': count,
            'risk_level': risk,
            'time_scanned': dt.strftime('%B %d, %Y — %I:%M %p')
        })
    return history

# --- Routes ---

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    results = model.predict(source=path, show=False)
    os.remove(path)

    final_object = None
    boxes = results[0].boxes
    if boxes and boxes.cls.numel() > 0:
        for i in range(len(boxes.cls)):
            label = results[0].names[int(boxes.cls[i])]
            conf  = float(boxes.conf[i])
            if label in allowed_objects and conf >= 0.75:
                final_object = label
                break

    if final_object:
        return redirect(url_for('refine', detected_object=final_object))
    return jsonify({'success': False, 'message': 'No suitable object detected'})


@app.route('/detect_frame', methods=['POST'])
def detect_frame():
    data = request.get_json()
    if not data or 'image' not in data:
        return jsonify({'success': False}), 400

    img_data = base64.b64decode(data['image'].split(',',1)[1])
    img = Image.open(BytesIO(img_data)).convert('RGB')
    temp_path = os.path.join(UPLOAD_FOLDER, "frame.jpg")
    img.save(temp_path)

    results = model.predict(source=temp_path, show=False)
    os.remove(temp_path)

    final_object = None
    max_conf = 0.0
    detections = []
    boxes = results[0].boxes
    if boxes and boxes.cls.numel() > 0:
        for i in range(len(boxes.cls)):
            label = results[0].names[int(boxes.cls[i])]
            conf = float(boxes.conf[i])
            if label in allowed_objects:
                max_conf = max(max_conf, conf)
                if conf >= 0.75:
                    final_object = label
                # Get box coordinates
                box = boxes.xyxy[i].tolist()
                detections.append({
                    'label': label,
                    'confidence': conf,
                    'box': box
                })

    if final_object:
        return jsonify({
            'success': True, 
            'redirect_url': url_for('refine', detected_object=final_object),
            'detections': detections
        })
    return jsonify({
        'success': False, 
        'confidence': max_conf,
        'detections': detections
    })

@app.route('/refine')
def refine():
    detected_object = request.args.get('detected_object')
    if not detected_object:
        return "No object detected", 400

    if detected_object == 'bottle':
        options = [
            'Small Bottle (~237 mL)',
            'Medium Bottle (~500 mL)',
            'Large Bottle (~1 L)',
            'Very Large Bottle (~1 Gal)'
        ]
    elif detected_object == 'toothbrush':
        options = [
            'New Toothbrush (Bought over 3 months ago)',
            'Old Toothbrush (Bought within 3 months)'
        ]
    elif detected_object == 'cell phone':
        options = [
            'New Plastic Phone Case',
            'Old Plastic Phone Case'
        ]
    else:
        options = [f"Plastic {detected_object.title()}"]

    return render_template('refine.html', options=options, detected_object=detected_object)

@app.route('/result', methods=['POST'])
def result():
    selected_object = request.form.get('selected_object')
    if not selected_object:
        return "No object selected", 400

    data = query_microplastic_data(selected_object)
    if not data:
        return "No data found for selected object", 404

    _, object_name, notes, particles, risk_level, alternative = data
    spoon_pct = calculate_spoon_percentage(particles)

    conn = sqlite3.connect('microplastics.sqlite')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO scan_history (object_name, microplastic_count, risk_level, time_scanned)
        VALUES (?, ?, ?, datetime('now'))
    """, (object_name, particles, risk_level))
    conn.commit()
    conn.close()

    history = format_history(get_scan_history())

    return render_template(
        'result.html',
        object_name=object_name,
        notes=notes,
        microplastic_particles=particles,
        risk_level=risk_level,
        alternative=alternative,
        spoon_percentage=spoon_pct,
        history=history
    )

@app.route('/history')
def history_view():
    history = format_history(get_scan_history())

    # Calculate totals for spoon visualization
    total_microplastics = sum([scan['microplastic_count'] for scan in history])
    total_microplastics_10y = total_microplastics * 10 * 365  # over 10 years of daily use
    grams_per_particle = 0.0000002  # 200 nanograms per particle
    spoon_grams = 5.0               # 5 grams = 1 plastic spoon
    total_mass = total_microplastics_10y * grams_per_particle
    spoon_percentage = min(round((total_mass / spoon_grams) * 100, 2), 100)

    # SVG fill calculations
    handle_height = 90
    bowl_height = 50
    total_height = handle_height + bowl_height
    fill_height = (spoon_percentage / 100.0) * total_height

    if fill_height <= handle_height:
        handle_fill_height = fill_height
        bowl_fill_height = 0
    else:
        handle_fill_height = handle_height
        bowl_fill_height = fill_height - handle_height

    handle_fill_y = 160 - handle_fill_height
    bowl_fill_y = 70 - bowl_fill_height

    return render_template(
        'history.html',
        scans=history,
        spoon_percentage=spoon_percentage,
        total_microplastics=total_microplastics_10y,
        total_mass=total_mass,
        handle_fill_height=handle_fill_height,
        bowl_fill_height=bowl_fill_height,
        handle_fill_y=handle_fill_y,
        bowl_fill_y=bowl_fill_y
    )


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/references')
def references():
    return render_template('references.html')

@app.route('/future-work')
def future_work():
    return render_template('future_work.html')

@app.route('/clear-history', methods=['POST'])
def clear_history():
    conn = sqlite3.connect('microplastics.sqlite')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM scan_history')
    conn.commit()
    conn.close()
    return redirect(url_for('history_view'))

if __name__ == '__main__':
    app.run(debug=True)
