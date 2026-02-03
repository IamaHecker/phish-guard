from app import create_app, db
from app.models import User, Template

app = create_app()

with app.app_context():
    db.create_all()
    
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@example.com', role='admin')
        admin.set_password('admin')
        db.session.add(admin)
        print("Created admin user (password: admin)")
        
    if not User.query.filter_by(username='user1').first():
        user1 = User(username='user1', email='user1@example.com', role='user', department='Sales')
        user1.set_password('user1')
        db.session.add(user1)
        print("Created standard user1")

    if not Template.query.first():
        template = Template(
            name='Password Reset',
            subject='Urgent: Password Reset Required',
            body='<p>Dear User,</p><p>Your password has expired. Please click <a href="{{link}}">here</a> to reset it.</p>',
            landing_page_id=1
        )
        db.session.add(template)
        print("Created default template")
        
    db.session.commit()
    print("Database initialized.")
