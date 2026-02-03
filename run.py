from app import create_app

app = create_app()

# Deployment Fix: Auto-create tables and default user if they don't exist
from app import db
from app.models import User
with app.app_context():
    db.create_all()
    # Ensure default admin user exists
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@example.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
    # Ensure default analyst user exists
    if not User.query.filter_by(username='analyst').first():
        analyst = User(username='analyst', email='analyst@example.com', role='analyst')
        analyst.set_password('analyst123')
        db.session.add(analyst)
        db.session.commit()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
