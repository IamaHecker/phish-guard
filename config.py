import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # Attempt 4: Use simple relative path. 
    # This creates the file in the CWD (which is project root on Render).
    # This avoids slash complexity with absolute paths in URIs.
    db_name = 'phish_guard.db'
    
    # Debug: Check if Render provided a DB URL automatically
    env_db_url = os.environ.get('DATABASE_URL')
    if env_db_url:
        print(f"--> CONFIG: Found DATABASE_URL in env: {env_db_url}")
    else:
        print(f"--> CONFIG: No DATABASE_URL in env. Using sqlite relative path.")

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # NOTE: We force the use of our sqlite DB for now to ensure stability, ignoring env for a moment
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_name}'
    print(f"--> CONFIG: Final SQLALCHEMY_DATABASE_URI: {SQLALCHEMY_DATABASE_URI}")

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
