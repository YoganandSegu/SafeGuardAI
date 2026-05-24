# Safeguard AI - Human Safety & Behavioral Analysis System

A real-time surveillance intelligence platform with a professional dashboard, emotion analysis, threat detection, and automated emergency alerting.

## Features

- **Real-Time Emotion Engine**: Uses DeepFace and MediaPipe to detect faces and classify emotions.
- **Intelligent Safety Risk Engine**: Classifies risk into SAFE, ALERT, WARNING, and HIGH RISK based on emotions and detected objects (YOLOv8).
- **Automated Email Alert System**: Sends an async email with a snapshot when a HIGH RISK event occurs.
- **Professional Dashboard UI**: A react-based dashboard showing live feed, emotion probability bars, threat levels, and recent incidents.

## Setup Instructions

### 1. Prerequisites
- Python 3.9+
- Node.js 18+
- A webcam or IP camera stream

### 2. Backend Setup
1. Open a terminal and navigate to the `safeguard-ai` directory.
2. Optional: Create a virtual environment (`python -m venv venv` and activate it).
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   > Note: DeepFace and YOLOv8 will download their models automatically on the first run.

4. Set your Email App Password for alerts (optional, for email functionality):
   - Linux/Mac: `export EMAIL_PASSWORD="your_app_password"`
   - Windows: `$env:EMAIL_PASSWORD="your_app_password"`

5. Run the backend:
   ```bash
   cd backend
   python main.py
   ```

### 3. Frontend Setup
1. Open a new terminal and navigate to `safeguard-ai/frontend`.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the dev server:
   ```bash
   npm run dev
   ```
4. Open the displayed URL (usually `http://localhost:5173`) in your browser.

## Demo Guidelines
- To test the "HIGH RISK" alert, try making a sustained "angry" or "fearful" face at the camera, or hold an object that YOLOv8 detects as a knife.
- The UI will update the threat level to RED and the backend will trigger an email (if configured) and save a screenshot in the `screenshots` folder.
- There is a 60-second cooldown on emails to prevent spam.
