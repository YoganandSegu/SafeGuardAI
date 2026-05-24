import cv2
import threading
import time
import base64
import os
from datetime import datetime
from database import SessionLocal, Alert, EmotionLog
from alert_system import alert_system

# Absolute path to screenshots folder (next to backend/)
SCREENSHOTS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "screenshots")
)

class CameraManager:
    def __init__(self, cam_id=0, emotion_engine=None, safety_engine=None):
        self.cam_id = str(cam_id)
        # Handle string inputs for camera index if possible
        try:
            self.cam_index = int(cam_id)
        except ValueError:
            self.cam_index = cam_id
            
        self.cap = None
        self.is_running = False
        self.thread = None
        
        self.emotion_engine = emotion_engine
        self.safety_engine = safety_engine
        
        self.current_frame = None
        self.current_analytics = {
            "threat_level": "SAFE",
            "safety_score": 100,
            "fps": 0,
            "emotions": {}
        }
        
    def start(self):
        self.cap = cv2.VideoCapture(self.cam_index)
        if not self.cap.isOpened():
            print(f"[Camera Manager] Failed to open camera {self.cam_id}")
            return False
            
        # Target 25-30 FPS on CPU, set camera props if supported
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        self.is_running = True
        self.thread = threading.Thread(target=self._update_loop, daemon=True)
        self.thread.start()
        print(f"[Camera Manager] Started camera {self.cam_id}")
        return True
        
    def stop(self):
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=2)
        if self.cap:
            self.cap.release()
            
    def _update_loop(self):
        prev_time = time.time()
        
        while self.is_running:
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.1)
                continue
                
            # Process Frame
            emotions = {}
            if self.emotion_engine:
                frame, emotions = self.emotion_engine.analyze_frame(frame)
                
            threat_level = "SAFE"
            safety_score = 100.0
            objects_detected = []
            
            if self.safety_engine:
                threat_level, safety_score, objects_detected = self.safety_engine.classify_risk(emotions, frame)
                
            # Calculate FPS
            curr_time = time.time()
            fps = int(1 / (curr_time - prev_time)) if (curr_time - prev_time) > 0 else 0
            prev_time = curr_time
            
            # Overlay UI on frame
            cv2.putText(frame, f"FPS: {fps}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"RISK: {threat_level}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 
                        (0, 0, 255) if threat_level == "HIGH RISK" else (0, 255, 255), 2)
            cv2.putText(frame, f"SCORE: {safety_score}%", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            if emotions:
                # Show top emotion
                top_emotion = max(emotions, key=emotions.get)
                cv2.putText(frame, f"[{top_emotion.upper()} - {emotions[top_emotion]:.1f}%]", (10, 120), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)

            # Store current state for WebSockets
            _, buffer = cv2.imencode('.jpg', frame)
            self.current_frame = base64.b64encode(buffer).decode('utf-8')
            
            dominant_emotion = max(emotions, key=emotions.get) if emotions else "neutral"
            
            self.current_analytics = {
                "threat_level": threat_level,
                "safety_score": safety_score,
                "fps": fps,
                "emotions": emotions,
                "cam_id": self.cam_id,
                "emotion": dominant_emotion
            }
            
            # Trigger Alert if HIGH RISK
            if threat_level == "HIGH RISK":
                self._handle_alert(frame, self.current_analytics)

    def _handle_alert(self, frame, alert_data):
        """Save screenshot and fire email alert with the captured frame."""
        # --- Encode frame to JPEG bytes in-memory (no disk race condition) ---
        success, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
        img_bytes = buffer.tobytes() if success else None

        if not success:
            print("[Camera Manager] ⚠️  Failed to encode frame to JPEG bytes.")

        # --- Also persist to disk with an absolute path ---
        img_filename = None
        try:
            os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
            img_filename = os.path.join(
                SCREENSHOTS_DIR,
                f"alert_{self.cam_id}_{int(time.time())}.jpg"
            )
            if img_bytes:
                with open(img_filename, 'wb') as f:
                    f.write(img_bytes)
                print(f"[Camera Manager] Screenshot saved: {img_filename}")
        except Exception as e:
            print(f"[Camera Manager] ⚠️  Could not save screenshot to disk: {e}")
            img_filename = None

        # --- Trigger alert: pass bytes (primary) + path (fallback) ---
        alert_triggered = alert_system.trigger_alert(
            alert_data,
            img_bytes=img_bytes,
            img_path=img_filename
        )

        if alert_triggered:
            # Log to Database
            db = SessionLocal()
            try:
                new_alert = Alert(
                    cam_id=self.cam_id,
                    emotion=alert_data.get('emotion'),
                    threat_level=alert_data.get('threat_level'),
                    safety_score=alert_data.get('safety_score'),
                    screenshot_path=img_filename
                )
                db.add(new_alert)
                db.commit()
            except Exception as e:
                print(f"[Database] Error saving alert: {e}")
            finally:
                db.close()
