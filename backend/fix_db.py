from app.database import engine
from sqlalchemy import text

def fix_db():
    print("Dropping feedbacks table...")
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS feedbacks"))
        conn.commit()
    print("feedbacks table dropped.")

if __name__ == "__main__":
    fix_db()
