import os
from dotenv import load_dotenv
import sqlalchemy
from sqlalchemy import create_engine

# Simulate the logic in database.py
current_file = os.path.abspath("app/database.py") # path relative to backend/ where we run this
# backend/app/database.py -> dirname -> backend/app -> dirname -> backend -> dirname -> project_root
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
dotenv_path = os.path.join(project_root, '.env')

print(f"Loading .env from: {dotenv_path}")
load_dotenv(dotenv_path=dotenv_path)

url = os.getenv("DATABASE_URL")
print(f"DATABASE_URL read from env: {url}")

if not url:
    print("Error: DATABASE_URL is empty!")
    exit(1)

try:
    engine = create_engine(url)
    with engine.connect() as conn:
        print("Successfully connected to the database!")
except Exception as e:
    print(f"Connection failed: {e}")
