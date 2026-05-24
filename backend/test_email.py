"""
test_email.py -- Run this script to test if emails with image attachments
                 are sending correctly from SafeGuard AI.

Usage (from the backend/ folder):
    python test_email.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

import cv2
import numpy as np
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import traceback

# ── Load credentials ──────────────────────────────────────────────
EMAIL_PASSWORD  = os.getenv("EMAIL_PASSWORD", "")
SENDER_EMAIL    = os.getenv("SENDER_EMAIL",    "yoganandsegu3@gmail.com")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "yoganandsegu3@gmail.com")

print("=" * 55)
print("  SafeGuard AI -- Email Test Script")
print("=" * 55)
print(f"  Sender    : {SENDER_EMAIL}")
print(f"  Recipient : {RECIPIENT_EMAIL}")
print(f"  Password  : {'*' * len(EMAIL_PASSWORD)} ({len(EMAIL_PASSWORD)} chars)")
print("=" * 55)

if not EMAIL_PASSWORD:
    print("\n[ERROR] EMAIL_PASSWORD is empty in backend/.env\n")
    sys.exit(1)

if len(EMAIL_PASSWORD) != 16:
    print(f"\n[WARN] Gmail App Passwords are exactly 16 chars."
          f" Your password is {len(EMAIL_PASSWORD)} chars.")
    print("       It might still work if you have a custom setup.\n")

# ── Create a dummy test image ─────────────────────────────────────
print("\n[1/4] Creating dummy test image...")
img = np.zeros((480, 640, 3), dtype=np.uint8)
img[:] = (30, 30, 60)
cv2.rectangle(img, (50, 50), (590, 430), (0, 0, 200), -1)
cv2.putText(img, "SafeGuard AI",  (120, 200), cv2.FONT_HERSHEY_SIMPLEX, 2,   (255, 255, 255), 3)
cv2.putText(img, "TEST ALERT",    (160, 270), cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 255, 255),   3)
cv2.putText(img, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), (140, 340),
            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (200, 200, 200), 2)

success, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 90])
if not success:
    print("[ERROR] Failed to encode test image.")
    sys.exit(1)

img_bytes = buffer.tobytes()
print(f"   [OK] Test image created ({len(img_bytes)} bytes)")

# ── Build email ───────────────────────────────────────────────────
print("[2/4] Building email...")
msg = MIMEMultipart()
msg['From']    = SENDER_EMAIL
msg['To']      = RECIPIENT_EMAIL
msg['Subject'] = "[SafeGuard AI] Test Alert -- Image Attachment Check"

body = (
    f"SafeGuard AI -- Email Test\n"
    f"{'=' * 45}\n\n"
    f"Timestamp   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    f"Camera ID   : TEST-CAM\n"
    f"Emotion     : angry\n"
    f"Threat Level: HIGH RISK\n"
    f"Safety Score: 5%\n\n"
    f"This is a test email to verify that captured images\n"
    f"are being sent correctly as attachments.\n\n"
    f"If you can see a red image attached -- everything is working!\n\n"
    f"-- SafeGuard AI Security System"
)
msg.attach(MIMEText(body, 'plain'))

attachment = MIMEBase('image', 'jpeg')
attachment.set_payload(img_bytes)
encoders.encode_base64(attachment)
attachment.add_header('Content-Disposition', 'attachment',
                      filename='test_alert_screenshot.jpg')
msg.attach(attachment)
print("   [OK] Email built with image attachment")

# ── Send ──────────────────────────────────────────────────────────
print("[3/4] Connecting to Gmail SMTP (smtp.gmail.com:587)...")
try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    print("   [OK] TLS connection established")

    print("[4/4] Logging in and sending...")
    server.login(SENDER_EMAIL, EMAIL_PASSWORD)
    server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
    server.quit()

    print("\n" + "=" * 55)
    print("  EMAIL SENT SUCCESSFULLY!")
    print(f"  Check inbox: {RECIPIENT_EMAIL}")
    print("=" * 55)

except smtplib.SMTPAuthenticationError as e:
    print("\n" + "=" * 55)
    print("  AUTHENTICATION FAILED")
    print("=" * 55)
    print(f"  SMTP error detail: {e}\n")
    print("""
The password in backend/.env is NOT a valid Gmail App Password.

HOW TO FIX:
  1. Open  https://myaccount.google.com/security
     and make sure 2-Step Verification is ON.
  2. Open  https://myaccount.google.com/apppasswords
  3. Under 'Select app' choose 'Mail'
     Under 'Select device' choose 'Windows Computer'
  4. Click Generate -- you'll get a 16-character code like:
        abcd efgh ijkl mnop
  5. Open  backend/.env  and set:
        EMAIL_PASSWORD="abcdefghijklmnop"   (no spaces)
  6. Run this test again: python test_email.py
""")
    sys.exit(1)

except smtplib.SMTPException as e:
    print(f"\n[ERROR] SMTP error: {e}")
    traceback.print_exc()
    sys.exit(1)

except Exception as e:
    print(f"\n[ERROR] Unexpected error: {e}")
    traceback.print_exc()
    sys.exit(1)
