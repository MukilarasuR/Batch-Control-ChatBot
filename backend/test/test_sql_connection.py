import psycopg2
from sqlalchemy import create_engine, text

# Test psycopg2 connection
try:
    conn = psycopg2.connect(
        host="localhost",
        database="chatbot_db",
        user="postgres",
        password="2309"  # Replace with your password
    )
    cur = conn.cursor()
    cur.execute("SELECT batch_code FROM batches LIMIT 1;")
    result = cur.fetchone()
    print(f"✅ Direct connection works! Found batch: {result[0]}")
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")

# Test SQLAlchemy connection
try:
    engine = create_engine("postgresql://postgres:2309@localhost:5432/chatbot_db")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM batches;"))
        count = result.fetchone()[0]
        print(f"✅ SQLAlchemy works! Total batches: {count}")
except Exception as e:
    print(f"❌ SQLAlchemy failed: {e}")