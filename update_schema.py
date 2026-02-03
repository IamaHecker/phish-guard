import sqlite3
import os

# Path to the database
db_path = os.path.join('instance', 'phish_guard.db')

def upgrade_db():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("Attempting to add 'quiz_answers' column to 'result' table...")
        try:
            cursor.execute("ALTER TABLE result ADD COLUMN quiz_answers TEXT")
            print("Success: Column 'quiz_answers' added.")
        except sqlite3.OperationalError:
            print("Info: Column 'quiz_answers' already exists.")

        print("Attempting to add 'token' column to 'result' table...")
        try:
            cursor.execute("ALTER TABLE result ADD COLUMN token TEXT")
            cursor.execute("CREATE UNIQUE INDEX ix_result_token ON result (token)")
            print("Success: Column 'token' added.")
        except sqlite3.OperationalError as e:
             if "duplicate column" in str(e).lower():
                print("Info: Column 'token' already exists.")
             else:
                print(f"Error adding token: {e}")

        conn.commit()
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("Info: Column 'quiz_answers' already exists.")
        else:
            print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    upgrade_db()
