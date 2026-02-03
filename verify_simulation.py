import unittest
import time
import os
import glob
import re
from app import create_app, db
from app.models import User, Campaign, Result, Template
from config import Config

# Use a test-specific config that still points to the REAL file system for emails
# so we can verify the 'debug_smtp.py' output.
class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    # Ensure we use the same mail settings as .env logic
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 1025
    SERVER_NAME = 'localhost:5000' # Needed for url_for(_external=True)

class SimulationFlowTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        
        # Clean up sent emails dir before test
        if os.path.exists('sent_emails'):
            files = glob.glob('sent_emails/*.eml')
            for f in files:
                os.remove(f)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_full_flow(self):
        print("\n--- Starting End-to-End Simulation Flow Test ---")
        
        # 1. Setup Data
        # User who launches (Admin)
        admin = User(username='admin', email='admin@example.com', role='admin')
        admin.set_password('adminpass')
        db.session.add(admin)
        
        # Template
        template = Template(name='Urgent Test', subject='Action Required', body='<a href="{{ link }}">Click me</a>', landing_page_id=1)
        db.session.add(template)
        db.session.commit()
        
        # Login
        self.client.post('/auth/login', data={'username': 'admin', 'password': 'adminpass'}, follow_redirects=True)
        
        # 2. Create Campaign
        print("Creating Campaign...")
        # We'll do this via DB directly to save time, mimicking the form submission
        c = Campaign(name='E2E Test', status='draft', template_id=template.id, target_emails='target@example.com')
        db.session.add(c)
        db.session.commit()
        
        # 3. Launch Campaign (This triggers email sending)
        print("Launching Campaign...")
        # In the real app, this is likely a POST to /campaign/<id>/launch
        # Let's inspect routes... assuming there is a launch route or we call the function directly.
        # Ideally we use the route. Checking routes/admin.py would confirm. 
        # For now, let's try the likely route. 
        # If not, checking routes/admin.py would be a smart move, but let's assume standard REST-ish: /admin/campaign/<id>/launch
        # or similar. I'll check admin.py in the tool call to be safe, but will write THIS script assuming I can invoke the logic.
        # Actually, let's invoke the logic directly to avoid route guessing issues in this script, 
        # verifying the *Core Logic* integration.
        
        from app.email import send_email
        from flask import render_template_string, url_for
        import uuid
        
        # Manually create the Result (which happens on launch)
        # result = Result(campaign_id=c.id, user_id=None, sent=False) # OLD
        
        # The schema has user_id. Does the system create User objects for targets?
        # Let's create a User for the target.
        target = User(email='target@example.com', username='target')
        db.session.add(target)
        db.session.commit()
        
        token_val = str(uuid.uuid4())
        result = Result(campaign_id=c.id, user_id=target.id, sent=False, token=token_val)
        db.session.add(result)
        db.session.commit()
        
        # URL generation requires request context or manually building
        # We need to simulate the 'link' logic.
        link = url_for('training.landing', token=token_val, _external=True)
        
        # Send
        print(f"Sending email to {target.email} with link {link}")
        body = render_template_string(template.body, link=link)
        sent = send_email(template.subject, 'security@phishguard.com', [target.email], body, body)
        
        self.assertTrue(sent, "Email sending returned False")
        
        # 4. Verify Email Receipt (File System)
        print("Waiting for email file...")
        time.sleep(2) # Wait for async SMTP handler
        files = glob.glob('sent_emails/*.eml')
        self.assertTrue(len(files) > 0, "No email file found in sent_emails/")
        
        latest_email = None
        for f in files:
            with open(f, 'r') as f_read:
                content_check = f_read.read()
                if 'Subject: Action Required' in content_check and 'target@example.com' in content_check:
                    latest_email = f
                    content = content_check
                    break
        
        if not latest_email:
             self.fail(f"Could not find test email among {len(files)} files.")
             
        print(f"Found match email file: {latest_email}")
        
        # content is already read
        # Verify Headers
        self.assertIn('target@example.com', content)
        self.assertIn('Action Required', content)
        # Find the link
        # Link format: http://localhost:5000/training/<uuid>
        # Regex for UUID: [0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}
        match = re.search(r'href="(http://localhost:5000/training/[0-9a-f\-]{36})"', content)
        if not match:
            # Try https just in case
             match = re.search(r'href="(https://localhost:5000/training/[0-9a-f\-]{36})"', content)
        
        self.assertTrue(match, "Could not find training link in email content")
        extracted_link = match.group(1)
        print(f"Extracted Link: {extracted_link}")
            
        # 5. Simulate Click
        # We don't need the full URL, just the path for test_client
        # extracted_link is like http://localhost:5000/training/1
        path = extracted_link.replace('http://localhost:5000', '').replace('https://localhost:5000', '')
        print(f"Visiting {path}...")
        response = self.client.get(path, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You clicked a phishing link!', response.data)
        
        # 6. Verify Database Update
        print("Verifying Database Update...")
        # Re-fetch result to check clicked stats
        # Token-based lookup
        r_check = Result.query.filter_by(token=token_val).first()
        self.assertTrue(r_check.clicked, "Result.clicked should be True")
        
        print("--- End-to-End Test Passed ---")

if __name__ == '__main__':
    unittest.main()
