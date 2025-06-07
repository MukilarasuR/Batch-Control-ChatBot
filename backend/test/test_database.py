"""
Test script to verify database connection and operations
Run this to test your setup
"""
import sys, os

# Go up to the project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.database import test_connection, create_tables, SessionLocal
from app.crud.batch_control import batch_crud  # ✅ Correct path

def test_database_setup():
    """Test database connection and basic operations"""
    print("🧪 Testing Database Setup...")

    print("\n1️⃣ Testing database connection...")
    if not test_connection():
        print("❌ Database connection failed. Check your config.py settings.")
        return False

    print("\n2️⃣ Creating database tables...")
    try:
        create_tables()
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        return False

    print("\n3️⃣ Testing CRUD operations...")
    db = SessionLocal()

    try:
        batch = batch_crud.get_batch_by_code(db, "VDT-052025-A")
        if batch:
            print(f"✅ Found batch: {batch.batch_code}")
        else:
            print("ℹ️ No sample batch found (normal if database is empty)")

        stats = batch_crud.get_batch_statistics(db)
        print(f"✅ Batch statistics: {stats}")

        print("\n✅ All database tests passed!")
        return True

    except Exception as e:
        print(f"❌ CRUD test failed: {e}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    test_database_setup()