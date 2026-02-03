import asyncio
from aiosmtpd.controller import Controller
import os
from datetime import datetime

class CustomHandler:
    async def handle_DATA(self, server, session, envelope):
        print(f"--------------------------------------------------")
        print(f"Received Email at {datetime.now()}")
        print(f"From: {envelope.mail_from}")
        print(f"To: {envelope.rcpt_tos}")
        
        content = envelope.content.decode('utf8', errors='replace')
        print("Message Content:")
        print(content)
        print(f"--------------------------------------------------")
        
        # Save to file for easy viewing
        if not os.path.exists('sent_emails'):
            os.makedirs('sent_emails')
            
        filename = f"sent_emails/email_{datetime.now().strftime('%Y%m%d_%H%M%S')}.eml"
        with open(filename, 'w') as f:
            f.write(f"From: {envelope.mail_from}\n")
            f.write(f"To: {envelope.rcpt_tos}\n")
            f.write(content)
        print(f"Saved to {filename}")
        
        return '250 Message accepted for delivery'

if __name__ == '__main__':
    controller = Controller(CustomHandler(), hostname='localhost', port=1025)
    controller.start()
    print("Local SMTP Server running on localhost:1025...")
    print("Press Enter to stop")
    
    try:
        input()
    except KeyboardInterrupt:
        pass
    finally:
        controller.stop()
