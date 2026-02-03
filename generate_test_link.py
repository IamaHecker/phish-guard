from app import create_app, db
from app.models import User, Campaign, Result
import sys

app = create_app()

def generate_link():
    with app.app_context():
        # 1. Get or Create Test User
        user = User.query.filter_by(email='test@example.com').first()
        if not user:
            print("Creating test user 'test@example.com'...")
            user = User(username='testuser', email='test@example.com')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()

        # 2. Get or Create Test Campaign
        campaign = Campaign.query.filter_by(name='Test Campaign').first()
        if not campaign:
            print("Creating test campaign 'Test Campaign'...")
            campaign = Campaign(name='Test Campaign')
            db.session.add(campaign)
            db.session.commit()

        # 3. Create Result
        result = Result(campaign_id=campaign.id, user_id=user.id)
        db.session.add(result)
        db.session.commit()

        # 4. Generate Link
        link = f"http://127.0.0.1:5000/track/click/{result.id}"
        print("\n" + "="*50)
        print(f"TRACKING LINK GENERATED:")
        print(link)
        print("="*50 + "\n")
        print("Clicking this link will:")
        print("1. Mark the result as clicked in the database.")
        print("2. Redirect you to the 'Learn More' / Training Landing page.")

if __name__ == "__main__":
    generate_link()
