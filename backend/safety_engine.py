from ultralytics import YOLO
import cv2

class SafetyEngine:
    def __init__(self):
        # Load YOLOv8 for object detection (weapons, people)
        # Using yolov8n.pt by default. It detects 'person', 'knife', etc.
        try:
            self.model = YOLO('yolov8n.pt') 
            print("[Safety Engine] YOLO model loaded.")
        except Exception as e:
            print(f"[Safety Engine] Error loading YOLO: {e}")
            self.model = None

    def classify_risk(self, emotions, frame):
        """
        Level Conditions:
        SAFE: Neutral/Happy dominant
        ALERT: Mild stress/anxiety detected (Fear/Sad)
        WARNING: Fear/Disgust sustained
        HIGH RISK: Panic/Anger spike, violence/weapon detected
        """
        threat_level = "SAFE"
        safety_score = 100.0
        
        # 1. Analyze Objects
        objects_detected = []
        weapon_detected = False
        
        if self.model is not None:
            results = self.model(frame, verbose=False)
            for r in results:
                for box in r.boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    name = self.model.names[cls]
                    if conf > 0.4:
                        objects_detected.append(name)
                        # COCO classes for potential weapons: 43 (knife), 34 (baseball bat)
                        if name in ['knife', 'baseball bat']:
                            weapon_detected = True

        # 2. Analyze Emotions
        # emotions dict example: {'angry': 0.1, 'disgust': 0.0, 'fear': 80.0, 'happy': 0.0, 'sad': 10.0, 'surprise': 0.0, 'neutral': 9.9}
        if not emotions:
            return threat_level, safety_score, objects_detected
            
        angry = emotions.get('angry', 0)
        fear = emotions.get('fear', 0)
        disgust = emotions.get('disgust', 0)
        sad = emotions.get('sad', 0)
        happy = emotions.get('happy', 0)
        neutral = emotions.get('neutral', 0)
        
        negative_score = angry + fear + disgust + sad
        
        # Determine Threat Level
        if weapon_detected or angry > 70 or fear > 85:
            threat_level = "HIGH RISK"
            safety_score = max(0, 100 - (angry * 0.8 + fear * 0.8 + 50))
        elif fear > 40 or disgust > 50 or angry > 40:
            threat_level = "WARNING"
            safety_score = max(20, 100 - negative_score * 0.6)
        elif sad > 40 or fear > 20:
            threat_level = "ALERT"
            safety_score = max(50, 100 - negative_score * 0.3)
        else:
            threat_level = "SAFE"
            safety_score = max(80, 100 - negative_score * 0.1)
            
        return threat_level, round(safety_score, 1), objects_detected
