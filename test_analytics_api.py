import unittest
from app import create_app, db
from app.models import User, Campaign, Result
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False # Disable CSRF for testing forms if needed

class AnalyticsApiTestCase(unittest.TestCase):
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

    def login(self, username, password):
        return self.client.post('/auth/login', data=dict(
            username=username,
            password=password,
            remember_me='y' # 'y' or 'true' or just present often works for BooleanField depending on impl, but False/True works with WTF test client usually? 
            # Actually, with WTF_CSRF_ENABLED=False and test_client, simple dict works.
            # Let's just stick to the fields.
        ), follow_redirects=True)

    def test_analytics_api(self):
        # Create an analyst user
        u = User(username='analyst', email='analyst@example.com', role='analyst')
        u.set_password('password')
        db.session.add(u)
        
        # Create sample data
        c1 = Campaign(name='Test Campaign 1', status='running')
        c2 = Campaign(name='Test Campaign 2', status='completed')
        db.session.add(c1)
        db.session.add(c2)
        
        # Add results
        # 1. Sent only
        r1 = Result(campaign=c1, user=u, sent=True)
        # 2. Opened and Clicked and Passed
        r2 = Result(campaign=c1, user=u, sent=True, opened=True, clicked=True, quiz_passed=True)
        # 3. Opened only
        r3 = Result(campaign=c2, user=u, sent=True, opened=True)
        
        db.session.add_all([r1, r2, r3])
        db.session.commit()

        # Login
        self.login('analyst', 'password')

        # Test API
        response = self.client.get('/analyst/api/stats')
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        
        # Expected stats:
        # total_campaigns: 2
        # total_results: 3
        # opened_count: 2 (r2, r3)
        # clicked_count: 1 (r2)
        # passed_count: 1 (r2)
        
        self.assertEqual(json_data['total_campaigns'], 2)
        self.assertEqual(json_data['total_results'], 3)
        self.assertEqual(json_data['opened_count'], 2)
        self.assertEqual(json_data['clicked_count'], 1)
        self.assertEqual(json_data['passed_count'], 1)
        
        print("Analytics API Test Passed!")

if __name__ == '__main__':
    unittest.main()
