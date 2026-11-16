import cv2
from ultralytics import YOLO
import time
import threading

# Load YOLO model
model = YOLO("yolov8l.pt")

# Global flag for stopping detection
running_detection = False

def detect_objects(speak_callback=None):
    global running_detection
    running_detection = True

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Could not open webcam.")
        return
    print("✅ Webcam started")

    last_spoken = time.time()
    spoken_objects = set()

    while running_detection:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to grab frame")
            break

        results = model(frame)
        annotated_frame = results[0].plot()

        current_objects = set()

        for box in results[0].boxes:
            cls = int(box.cls[0])
            obj_name = model.names[cls]

            x1, y1, x2, y2 = box.xyxy[0]
            box_height = y2 - y1
            distance = "near" if box_height > 250 else "far"

            current_objects.add(f"{obj_name} ({distance})")

        print("🎯 Detected:", ", ".join(current_objects) if current_objects else "None")

        # 🔊 Speak new objects
        if current_objects and (time.time() - last_spoken > 5):
            to_speak = current_objects - spoken_objects
            if to_speak and speak_callback:
                sentence = "I see " + ", ".join(to_speak)
                speak_callback(sentence)
                spoken_objects.update(current_objects)
                last_spoken = time.time()

        if time.time() - last_spoken > 30:
            spoken_objects.clear()

        cv2.imshow("AI Smart Stick - Object Detection", annotated_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("🛑 Object detection stopped")

def start_detection_thread(speak_callback=None):
    thread = threading.Thread(target=detect_objects, args=(speak_callback,))
    thread.daemon = True
    thread.start()
