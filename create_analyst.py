from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    # Check if analyst exists
    analyst = User.query.filter_by(username='analyst').first()
    if not analyst:
        analyst = User(username='analyst', email='analyst@phishguard.com', role='analyst')
        analyst.set_password('password123')
        db.session.add(analyst)
        db.session.commit()
        print("Created user 'analyst' with password 'password123'")
    else:
        print("User 'analyst' already exists.")
