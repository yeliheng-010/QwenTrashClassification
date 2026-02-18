import sys
import os

# Add backend directory to path
sys.path.append(os.getcwd())

from app.database import engine
from sqlalchemy import inspect

try:
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Tables: {tables}")
    if "articles" in tables:
        print("Table 'articles' exists.")
        
        # Check columns
        columns = [c["name"] for c in inspector.get_columns("articles")]
        print(f"Columns: {columns}")
    else:
        print("Table 'articles' MISSING.")
except Exception as e:
    print(f"Error: {e}")
