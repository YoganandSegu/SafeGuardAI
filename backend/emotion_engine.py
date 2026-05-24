import cv2
import mediapipe as mp
from deepface import DeepFace
import time

class EmotionEngine:
    def __init__(self):
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)
        # DeepFace loads models lazily by default, we can do a dummy inference to load it if needed
        self.last_analysis_time = 0
        self.analysis_interval = 0.5 # Analyze emotion every 0.5 seconds to save CPU
        self.current_emotions = {}
        
    def analyze_frame(self, frame):
        """
        Detects faces using MediaPipe. If faces are found and interval has passed,
        analyzes emotion using DeepFace.
        Returns the processed frame and the current emotions.
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_detection.process(rgb_frame)
        
        bboxes = []
        if results.detections:
            for detection in results.detections:
                bboxC = detection.location_data.relative_bounding_box
                ih, iw, _ = frame.shape
                x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)
                bboxes.append((x, y, w, h))
                
                # Draw bounding box
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
        
        current_time = time.time()
        if results.detections and (current_time - self.last_analysis_time > self.analysis_interval):
            try:
                # Analyze entire frame for simplicity, deepface will find the face
                # Or pass a cropped face. DeepFace is robust.
                analysis = DeepFace.analyze(rgb_frame, actions=['emotion'], enforce_detection=False, silent=True)
                
                # Handle single or multiple faces
                if isinstance(analysis, list):
                    main_face = analysis[0]
                else:
                    main_face = analysis
                    
                self.current_emotions = main_face['emotion']
                self.last_analysis_time = current_time
            except Exception as e:
                print(f"[Emotion Engine] Error: {e}")
                
        return frame, self.current_emotions
