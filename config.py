import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'phish_guard.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # URL Generation (Tunneling)
    SERVER_NAME = os.environ.get('SERVER_NAME') # e.g., 'abcdef.ngrok-free.app'
    
    # Mail settings (Mock for now)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', '').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', '').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['your-email@example.com']
