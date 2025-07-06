from ultralytics import YOLO
import cv2

# Load YOLOv8s model
model = YOLO("yolov8s.pt")

# Start webcam
cap = cv2.VideoCapture(0)

# Define allowed objects
allowed_objects = ["bottle", "fork", "spoon", "knife", "cell phone", "cup", "toothbrush"]
target_confidence = 0.8  # 80% confidence threshold
final_object = None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model.predict(source=frame, show=False)
    boxes = results[0].boxes

    if boxes is not None and boxes.cls.numel() > 0:
        for i in range(len(boxes.cls)):
            class_id = int(boxes.cls[i])
            confidence = float(boxes.conf[i])
            label = results[0].names[class_id]

            # Only act if label is in allowed_objects
            if label in allowed_objects:
                if confidence >= target_confidence:
                    final_object = label
                    # print(f"Final Detected object: {final_object} with confidence {confidence:.2f}")
                    break  # Found good object, break out

    # Show annotated frame
    annotated_frame = results[0].plot()
    cv2.imshow("PlasticScope Live", annotated_frame)

    if final_object is not None or cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()

if final_object:
    print(f"Final detected object: {final_object}")
else:
    print("No suitable object detected.")
