from app import create_app
from app.email import send_email

app = create_app()

with app.app_context():
    print("Testing email sending...")
    print(f"MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
    print(f"MAIL_PORT: {app.config.get('MAIL_PORT')}")
    
    try:
        sender_email = app.config.get('MAIL_USERNAME') or "test@example.com"
        send_email(
            subject="Test Email from Phish Guard",
            sender=sender_email,
            recipients=["vfv917@gmail.com"], # Sending to self for test
            text_body="This is a test email from Phish Guard.",
            html_body="<p>This is a <b>test</b> email from Phish Guard.</p>"
        )
        print("Email send function called.")
    except Exception as e:
        print(f"An error occurred: {e}")
