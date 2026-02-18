import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add the parent directory to sys.path to ensure we can load env vars correctly if needed
# But here we just need the connection string
backend_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(backend_dir, ".env")
load_dotenv(env_path)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("Error: DATABASE_URL not found in .env")
    sys.exit(1)

def add_is_active_column():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        try:
            # Check if column exists
            result = conn.execute(text("SHOW COLUMNS FROM users LIKE 'is_active'"))
            if result.fetchone():
                print("Column 'is_active' already exists. Skipping.")
            else:
                print("Adding 'is_active' column to 'users' table...")
                conn.execute(text("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用'"))
                conn.commit()
                print("Column 'is_active' added successfully.")
        except Exception as e:
            print(f"Error updating database: {e}")

if __name__ == "__main__":
    add_is_active_column()
