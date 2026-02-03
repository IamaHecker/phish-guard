import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText

# Load environment variables
load_dotenv('.env')

smtp_server = os.environ.get('MAIL_SERVER')
smtp_port = int(os.environ.get('MAIL_PORT') or 465)
smtp_user = os.environ.get('MAIL_USERNAME')
smtp_password = os.environ.get('MAIL_PASSWORD')
use_ssl = os.environ.get('MAIL_USE_SSL') == 'True'

print(f"--- Diagnosing Email Configuration ---")
print(f"Server: {smtp_server}:{smtp_port}")
print(f"User: {smtp_user}")
print(f"SSL: {use_ssl}")
print("--------------------------------------")

try:
    if use_ssl:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
    else:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
    
    print("1. Connection established.")
    
    server.login(smtp_user, smtp_password)
    print("2. Login successful.")
    
    msg = MIMEText("This is a test email from Phish Guard diagnostic tool.")
    msg['Subject'] = "Phish Guard Test"
    msg['From'] = smtp_user
    msg['To'] = smtp_user # Send to self
    
    server.send_message(msg)
    print("3. Email sent successfully!")
    server.quit()
    
except Exception as e:
    print(f"\n[ERROR] Failed to send email:")
    print(e)
