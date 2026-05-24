import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import time
import traceback
from datetime import datetime
import threading
from dotenv import load_dotenv

load_dotenv()

class AlertSystem:
    def __init__(self):
        self.cooldown = 60  # seconds between alerts
        self.last_alert_time = 0
        self.email_password = os.getenv("EMAIL_PASSWORD")
        self.sender_email = os.getenv("SENDER_EMAIL", "yoganandsegu3@gmail.com")
        self.recipient_email = os.getenv("RECIPIENT_EMAIL", "yoganandsegu3@gmail.com")

    def _send_email_sync(self, alert_data, img_bytes=None, img_path=None):
        """Send alert email with an attached screenshot.
        
        Accepts either raw image bytes (img_bytes) or a file path (img_path).
        img_bytes takes priority over img_path.
        """
        if not self.email_password:
            print("[Alert System] ❌ EMAIL_PASSWORD not set in .env. Skipping email alert.")
            return

        if not self.sender_email:
            print("[Alert System] ❌ SENDER_EMAIL not set in .env. Skipping email alert.")
            return

        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            msg['Subject'] = f"[🚨 ALERT] High Risk Behavior Detected — Cam {alert_data.get('cam_id', 'Unknown')}"

            body = (
                f"SafeGuard AI — Automated Security Alert\n"
                f"{'=' * 45}\n\n"
                f"Timestamp    : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Camera ID    : {alert_data.get('cam_id', 'N/A')}\n"
                f"Emotion      : {alert_data.get('emotion', 'N/A')}\n"
                f"Threat Level : {alert_data.get('threat_level', 'HIGH RISK')}\n"
                f"Safety Score : {alert_data.get('safety_score', 0)}%\n\n"
                f"Description  : Panic/Anger spike detected by the AI system.\n"
                f"Action       : Please review the attached screenshot immediately.\n\n"
                f"— SafeGuard AI Security System"
            )
            msg.attach(MIMEText(body, 'plain'))

            # Resolve image data — prefer raw bytes, fall back to file path
            image_data = None
            image_name = "alert_screenshot.jpg"

            if img_bytes is not None and len(img_bytes) > 0:
                image_data = img_bytes
                image_name = f"alert_cam{alert_data.get('cam_id', '0')}_{int(time.time())}.jpg"
                print(f"[Alert System] Attaching image from bytes ({len(image_data)} bytes)")

            elif img_path:
                if os.path.exists(img_path):
                    with open(img_path, 'rb') as f:
                        image_data = f.read()
                    image_name = os.path.basename(img_path)
                    print(f"[Alert System] Attaching image from file: {img_path} ({len(image_data)} bytes)")
                else:
                    print(f"[Alert System] ⚠️  Screenshot file not found: {img_path}")

            if image_data:
                attachment = MIMEBase('image', 'jpeg')
                attachment.set_payload(image_data)
                encoders.encode_base64(attachment)
                attachment.add_header(
                    'Content-Disposition',
                    'attachment',
                    filename=image_name
                )
                msg.attach(attachment)
            else:
                print("[Alert System] ⚠️  No image data available — sending email without attachment.")

            print(f"[Alert System] Connecting to Gmail SMTP...")
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(self.sender_email, self.email_password)
            server.sendmail(self.sender_email, self.recipient_email, msg.as_string())
            server.quit()
            print(f"[Alert System] ✅ Email sent successfully to {self.recipient_email}")

        except smtplib.SMTPAuthenticationError:
            print(
                "[Alert System] ❌ SMTP Authentication Failed!\n"
                "  → Make sure you are using a Gmail App Password (not your regular password).\n"
                "  → Enable 2FA on your Google account, then generate an App Password at:\n"
                "    https://myaccount.google.com/apppasswords\n"
                "  → Paste the 16-character App Password (no spaces) into backend/.env as EMAIL_PASSWORD"
            )
        except smtplib.SMTPException as e:
            print(f"[Alert System] ❌ SMTP error: {e}")
            traceback.print_exc()
        except Exception as e:
            print(f"[Alert System] ❌ Unexpected error sending email: {e}")
            traceback.print_exc()

    def trigger_alert(self, alert_data, img_bytes=None, img_path=None):
        """Trigger an alert with optional image attachment.
        
        Args:
            alert_data: dict with cam_id, emotion, threat_level, safety_score
            img_bytes:  raw JPEG bytes of the captured frame (preferred)
            img_path:   path to a saved screenshot file (fallback)
        """
        current_time = time.time()
        if current_time - self.last_alert_time < self.cooldown:
            remaining = int(self.cooldown - (current_time - self.last_alert_time))
            print(f"[Alert System] Cooldown active — next alert in {remaining}s")
            return False

        self.last_alert_time = current_time
        print(f"[Alert System] 🚨 TRIGGERING HIGH RISK ALERT FOR CAM {alert_data.get('cam_id')}")

        # Send email in background thread to avoid blocking the camera loop
        t = threading.Thread(
            target=self._send_email_sync,
            args=(alert_data,),
            kwargs={'img_bytes': img_bytes, 'img_path': img_path},
            daemon=True
        )
        t.start()
        return True

alert_system = AlertSystem()
