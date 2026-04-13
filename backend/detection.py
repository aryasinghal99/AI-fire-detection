from ultralytics import YOLO
import time


class FireDetector:
    def __init__(self, model_path='best.pt'):
        self.model = YOLO(model_path)
        print(f"Model loaded. Classes: {self.model.names}")

        self.last_detected_time = 0
        self.cooldown = 5  # seconds

    def process_frame(self, frame):
        # 🔥 Lower confidence threshold for better detection
        results = self.model(frame, conf=0.15)

        annotated_frame = results[0].plot()
        detections = []

        fire_detected = False
        max_conf = 0
        detected_class = None

        for result in results:
            for box in result.boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                name = self.model.names[cls]

                print(f"DETECTED: {name} ({conf:.2f})")  # 🔍 DEBUG

                detections.append({
                    "class": name,
                    "confidence": conf,
                    "bbox": box.xyxy[0].tolist()
                })

                # 🔥 FIXED CONDITION (more flexible)
                if "fire" in name.lower() or "smoke" in name.lower():
                    if conf > 0.3:   # lowered from 0.5 → 0.3
                        fire_detected = True
                        max_conf = max(max_conf, conf)
                        detected_class = name

        # ⏱️ cooldown logic
        should_trigger = False
        if fire_detected and (time.time() - self.last_detected_time > self.cooldown):
            self.last_detected_time = time.time()
            should_trigger = True
            print(f"🔥 TRIGGERED: {detected_class} ({max_conf:.2f})")

        return annotated_frame, detections, should_trigger, detected_class, max_conf