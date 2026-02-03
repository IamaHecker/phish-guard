from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='user') # admin, analyst, user
    department = db.Column(db.String(64)) # For cohorts

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    status = db.Column(db.String(20), default='draft') # draft, scheduled, running, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    template_id = db.Column(db.Integer, db.ForeignKey('template.id'))
    target_emails = db.Column(db.Text) # Comma-separated list of emails
    
    results = db.relationship('Result', backref='campaign', lazy='dynamic')

class Template(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    subject = db.Column(db.String(256))
    body = db.Column(db.Text) # HTML content
    landing_page_id = db.Column(db.Integer) # ID of the training page to show

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sent = db.Column(db.Boolean, default=False)
    opened = db.Column(db.Boolean, default=False)
    clicked = db.Column(db.Boolean, default=False)
    reported = db.Column(db.Boolean, default=False)
    quiz_passed = db.Column(db.Boolean, default=False)
    quiz_answers = db.Column(db.Text) # JSON string of answers
    token = db.Column(db.String(36), unique=True, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User')
