from app import create_app, db
from sqlalchemy import inspect

app = create_app()

with app.app_context():
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('campaign')]
    if 'target_emails' in columns:
        print("SUCCESS: target_emails column exists.")
    else:
        print("FAILURE: target_emails column missing.")
