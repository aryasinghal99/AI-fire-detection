import cv2
import os
from datetime import datetime
import database
import notification


class Camera:
    def __init__(self, source, name):
        self.source = int(source) if str(source).isdigit() else source
        self.name = name
        self.cap = cv2.VideoCapture(self.source)

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def release(self):
        self.cap.release()


class CameraManager:
    def __init__(self, detector):
        self.detector = detector
        self.cameras = {}
        self.next_id = 0
        self.snapshot_dir = "snapshots"
        os.makedirs(self.snapshot_dir, exist_ok=True)

    # ✅ ADD CAMERA (FIXES YOUR ERROR)
    def add_camera(self, source, name):
        cam = Camera(source, name)
        cam_id = self.next_id
        self.cameras[cam_id] = cam
        self.next_id += 1
        return cam_id

    # ✅ REMOVE CAMERA
    def remove_camera(self, cam_id):
        if cam_id in self.cameras:
            self.cameras[cam_id].release()
            del self.cameras[cam_id]
            return True
        return False

    # ✅ GET FRAME + DETECTION
    def get_frame(self, cam_id):
        if cam_id not in self.cameras:
            return None

        frame = self.cameras[cam_id].get_frame()
        if frame is None:
            return None

        # 🔥 Run detection
        annotated_frame, detections, trigger, cls, conf = self.detector.process_frame(frame)

        if trigger:
            path = self.save_snapshot(frame, cls)

            # 🗄️ Save to DB
            database.add_event(cls.upper(), conf, path)

            # 🔔 Send notification
            notification.trigger_notifications(cls.upper(), conf, path)

            print(f"🔥 FIRE ALERT: {cls} ({conf:.2f})")

        return annotated_frame

    # 📸 SAVE SNAPSHOT
    def save_snapshot(self, frame, label):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"{self.snapshot_dir}/{label}_{timestamp}.jpg"
        cv2.imwrite(path, frame)
        return path