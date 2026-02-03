import unittest
import uuid
import re
from app import create_app, db
from app.models import User, Campaign, Result, Template
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SERVER_NAME = 'localhost:5000'

class SecureLinksTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_secure_tokens(self):
        # 1. Setup
        user = User(username='testtarget', email='target@example.com')
        db.session.add(user)
        template = Template(name='T', subject='S', body='B', landing_page_id=1)
        db.session.add(template)
        db.session.commit()
        
        c = Campaign(name='C', template_id=template.id, status='running')
        db.session.add(c)
        db.session.commit()
        
        # 2. PROPER CREATION (Simulate admin.launch logic)
        # Verify creating result WITHOUT token fails or is insecure? 
        # Actually we want to verify the system creates it with token.
        # But we don't have the launch function imported here easily without mocking requests.
        # Let's manually create like the admin route does now:
        
        token_val = str(uuid.uuid4())
        r = Result(campaign_id=c.id, user_id=user.id, token=token_val)
        db.session.add(r)
        db.session.commit()
        
        # 3. Verify Lookups
        # A. Track Open
        url = f'/track/open/{token_val}'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Result.query.get(r.id).opened)
        
        # B. Track Click
        url = f'/track/click/{token_val}'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302) # Redirect
        self.assertTrue(Result.query.get(r.id).clicked)
        
        # C. Landing Page
        # Follow redirect or direct access
        url = f'/training/{token_val}'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        
        # 4. Verify Legacy/Invalid Access Fails
        # Try accessing with ID (should 404)
        resp = self.client.get(f'/training/{r.id}')
        self.assertEqual(resp.status_code, 404)
        
        # Try accessing with wrong token
        resp = self.client.get(f'/training/invalid-token')
        self.assertEqual(resp.status_code, 404)
        
        print("Secure Token Verification Passed!")

if __name__ == '__main__':
    unittest.main()
