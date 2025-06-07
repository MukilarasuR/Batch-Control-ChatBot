# test_imports.py
try:
    import psycopg2
    import sqlalchemy
    import fastapi
    import langchain
    print("✅ All packages installed successfully!")
except ImportError as e:
    print(f"❌ Missing package: {e}")