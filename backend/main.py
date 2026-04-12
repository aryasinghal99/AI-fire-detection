from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import os
import cv2

# 🔥 Import your modules
import database
from detection import FireDetector
from camera_manager import CameraManager
import notification

# ==============================
# 🚀 Initialize App
# ==============================
app = FastAPI(title="AI Fire Detection System")

# Initialize database
database.init_db()

# Initialize detector + camera manager
detector = FireDetector()
camera_manager = CameraManager(detector)

# Add default webcam
camera_manager.add_camera(0, "Camera 1")

# ==============================
# 🌐 CORS Configuration
# ==============================
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================
# 📁 Static Folder (Snapshots)
# ==============================
if not os.path.exists("snapshots"):
    os.makedirs("snapshots")

app.mount("/snapshots", StaticFiles(directory="snapshots"), name="snapshots")

# ==============================
# 🏠 Root Endpoint
# ==============================
@app.get("/")
def read_root():
    return {"status": "ok", "message": "Fire Detection API Running"}

# ==============================
# 🎥 Video Streaming
# ==============================
def generate_camera_stream(camera_id):
    while True:
        frame = camera_manager.get_frame(camera_id)

        if frame is not None:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        else:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + b'' + b'\r\n')


@app.get("/video_feed")
def video_feed_default():
    return StreamingResponse(
        generate_camera_stream(0),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@app.get("/video_feed/{camera_id}")
def video_feed(camera_id: int):
    return StreamingResponse(
        generate_camera_stream(camera_id),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

# ==============================
# 📷 Camera APIs
# ==============================
class CameraModel(BaseModel):
    source: str
    name: str


@app.get("/cameras")
def get_cameras():
    cameras = []
    for cam_id, cam in camera_manager.cameras.items():
        cameras.append({
            "id": cam_id,
            "name": cam.name,
            "source": str(cam.source)
        })
    return {"cameras": cameras}


@app.post("/cameras")
def add_camera(cam: CameraModel):
    new_id = camera_manager.add_camera(cam.source, cam.name)
    return {"status": "ok", "id": new_id}


@app.delete("/cameras/{camera_id}")
def delete_camera(camera_id: int):
    if camera_manager.remove_camera(camera_id):
        return {"status": "ok"}
    raise HTTPException(status_code=404, detail="Camera not found")

# ==============================
# 🚨 Alerts APIs
# ==============================
@app.get("/alerts")
def get_alerts():
    events = database.get_recent_events(limit=50)

    formatted = []
    for e in events:
        formatted.append({
            "id": e["id"],
            "timestamp": e["timestamp"],
            "type": e["type"],
            "confidence": e["confidence"],
            "snapshot": e["snapshot_path"]
        })

    return {"alerts": formatted}

# ==============================
# 📊 Stats APIs
# ==============================
@app.get("/stats")
def get_stats():
    return {"stats": database.get_daily_stats()}


@app.get("/history")
def get_history(limit: int = 50, offset: int = 0):
    return {"events": database.get_all_events(limit, offset)}

# ==============================
# ⚙️ Settings APIs
# ==============================
class SettingsModel(BaseModel):
    key: str
    value: str


@app.get("/settings")
def get_settings():
    settings = database.get_all_settings()

    # Mask sensitive data
    for key in ["email_password", "smtp_password"]:
        if key in settings and settings[key]:
            settings[key] = "********"

    return {"settings": settings}


@app.post("/settings")
def save_setting(setting: SettingsModel):
    if setting.value == "********":
        return {"status": "skipped"}

    database.set_setting(setting.key, setting.value)
    return {"status": "ok"}

# ==============================
# 🔔 Notification Test
# ==============================
@app.post("/test-notification")
def test_notification():
    notification.trigger_notifications("TEST FIRE", 0.99, None)
    return {"status": "ok"}