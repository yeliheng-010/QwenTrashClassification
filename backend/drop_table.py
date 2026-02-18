import sys
import os
sys.path.append(os.getcwd())

from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS articles"))
    conn.commit()
    print("Dropped table 'articles'")
