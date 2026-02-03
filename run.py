from app import create_app

app = create_app()

# Deployment Fix: Auto-create tables and default user if they don't exist
from app import db
from app.models import User
import os

# Deployment Fix: Auto-create tables and default user if they don't exist
from app import db
from app.models import User
import os
import sys

with app.app_context():
    # Debug: Print DB URI
    print(f"--> RUN: Active Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # No longer needed to create instance dir if we use root, but keeping for safety
    # in case config changes back.
    try:
        db.create_all()
    except Exception as e:
        print(f"--> ERROR creating tables: {e}")

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

# Debug: Print all registered routes
print("Registered Routes:")
print(app.url_map)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
