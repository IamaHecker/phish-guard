import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import current_app

def send_email(subject, sender, recipients, text_body, html_body):
    """
    Sends an email using the configured SMTP server.
    Falls back to printing to console if MAIL_SERVER is not set.
    """
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ", ".join(recipients)

    part1 = MIMEText(text_body, 'plain')
    part2 = MIMEText(html_body, 'html')

    msg.attach(part1)
    msg.attach(part2)

    mail_server = current_app.config.get('MAIL_SERVER')
    
    if not mail_server:
        print(f"--------------------------------------------------")
        print(f"Sending Email (MOCK - Configure MAIL_SERVER to send real emails):")
        print(f"Subject: {subject}")
        print(f"From: {sender}")
        print(f"To: {recipients}")
        print(f"Body (HTML snippet): {html_body[:100]}...")
        print(f"--------------------------------------------------")
        current_app.logger.info(f"Mock email sent to {recipients}")
        return True

    try:
        if current_app.config.get('MAIL_USE_SSL'):
            server = smtplib.SMTP_SSL(mail_server, current_app.config.get('MAIL_PORT', 465))
        else:
            server = smtplib.SMTP(mail_server, current_app.config.get('MAIL_PORT', 587))
            if current_app.config.get('MAIL_USE_TLS'):
                server.starttls()
        
        username = current_app.config.get('MAIL_USERNAME')
        password = current_app.config.get('MAIL_PASSWORD')
        
        if username and password:
            server.login(username, password)
            
        server.sendmail(sender, recipients, msg.as_string())
        server.quit()
        current_app.logger.info(f"Real email sent to {recipients}")
        print(f"Successfully sent email to {recipients}")
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {e}")
        print(f"Error sending email: {e}")
        return False
