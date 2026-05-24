from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv
load_dotenv()

import asyncio
import json
import os

from database import init_db, get_db, Alert, EmotionLog
from emotion_engine import EmotionEngine
from safety_engine import SafetyEngine
from camera_manager import CameraManager


app = FastAPI(title="Safeguard AI API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines and managers
emotion_engine = None
safety_engine = None
cameras = {}

@app.on_event("startup")
async def startup_event():
    init_db()
    global emotion_engine, safety_engine
    
    print("[System] Initializing AI Engines...")
    emotion_engine = EmotionEngine()
    safety_engine = SafetyEngine()
    
    # Start default camera
    cam_index = os.getenv("CAMERA_INDEX", "0")
    cam = CameraManager(cam_id=cam_index, emotion_engine=emotion_engine, safety_engine=safety_engine)
    if cam.start():
        cameras[cam_index] = cam
    else:
        print(f"[System] Warning: Could not start camera {cam_index}")

@app.on_event("shutdown")
async def shutdown_event():
    for cam in cameras.values():
        cam.stop()

@app.websocket("/stream/{cam_id}")
async def websocket_endpoint(websocket: WebSocket, cam_id: str):
    await websocket.accept()
    if cam_id not in cameras:
        await websocket.close()
        return
        
    cam = cameras[cam_id]
    
    try:
        while True:
            # Send analytics
            if cam.current_analytics:
                await websocket.send_json({
                    "type": "analytics",
                    "data": cam.current_analytics
                })
            
            # Send frame
            if cam.current_frame:
                await websocket.send_json({
                    "type": "frame",
                    "image": cam.current_frame
                })
                
            await asyncio.sleep(1/30) # ~30fps loop
    except WebSocketDisconnect:
        print(f"Client disconnected from stream {cam_id}")
    except Exception as e:
        print(f"WebSocket error: {e}")

@app.get("/analytics/current")
def get_current_analytics(cam_id: str = "0"):
    if cam_id in cameras:
        return cameras[cam_id].current_analytics
    return {"error": "Camera not found"}

@app.get("/alerts")
def get_alerts(db: Session = Depends(get_db)):
    alerts = db.query(Alert).order_by(Alert.timestamp.desc()).limit(50).all()
    return alerts

@app.get("/system/health")
def get_system_health():
    import psutil
    cpu = psutil.cpu_percent(interval=None)
    # Mock GPU usage or read if available
    gpu = 0
    return {
        "status": "healthy",
        "cpu_usage": cpu,
        "gpu_usage": gpu,
        "active_cameras": len(cameras)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
