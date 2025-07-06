from ultralytics import YOLO

# Load YOLOv8s model
model = YOLO("yolov8s.pt")

# Allowed objects you care about
allowed_objects = ["bottle", "fork", "spoon", "knife", "cup", "cell phone", "toothbrush"]
target_confidence = 0.7  # 70% confidence threshold
final_object = None

# Run detection on uploaded image
results = model.predict(source="bottle2.jpg", show=False)

# --- Analyze Detections ---
boxes = results[0].boxes

if boxes is not None and boxes.cls.numel() > 0:
    for i in range(len(boxes.cls)):
        class_id = int(boxes.cls[i])
        confidence = float(boxes.conf[i])
        label = results[0].names[class_id]

        # Only accept if it's in the allowed list
        if label in allowed_objects:
            if confidence >= target_confidence:
                final_object = label
                break  # Stop after first good detection

# --- Print the final detected object ---
if final_object:
    print(f"Final detected object: {final_object}")
else:
    print("No suitable object detected.")

