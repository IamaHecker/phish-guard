from app import create_app, db
from app.models import User, Template

app = create_app()

with app.app_context():
    db.create_all()
    
    # Create Admin User
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@example.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        print("Admin user created.")

    # Create Analyst User
    if not User.query.filter_by(username='analyst').first():
        analyst = User(username='analyst', email='analyst@example.com', role='analyst')
        analyst.set_password('analyst123')
        db.session.add(analyst)
        print("Analyst user created.")
        
    # Create Default Template
    if not Template.query.first():
        template = Template(name='Urgent Password Reset', subject='Action Required: Reset Password', body='<p>Click here to reset your password.</p>', landing_page_id=1)
        db.session.add(template)
        print("Default template created.")

    db.session.commit()
    print("Database initialized.")
