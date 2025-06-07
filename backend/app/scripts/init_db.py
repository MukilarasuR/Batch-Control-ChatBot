import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.common import Department, Employee
from app.models.batch_control import Product, Batch, BatchTracking, BatchStatus
from app.database import Base
from app.config import settings
from datetime import datetime, date
import uuid


def init_database():
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # Create departments
        warehouse_dept = Department(
            id=uuid.uuid4(),
            name="Warehouse Operations"
        )

        quality_dept = Department(
            id=uuid.uuid4(),
            name="Quality Control"
        )

        db.add_all([warehouse_dept, quality_dept])
        db.commit()

        # Create employees
        john_smith = Employee(
            id=uuid.uuid4(),
            name="John Smith",
            email="john.smith@acmepharma.com",
            department_id=warehouse_dept.id,
            designation="Warehouse Manager",
            date_joined=date(2023, 1, 15)
        )

        jane_doe = Employee(
            id=uuid.uuid4(),
            name="Jane Doe",
            email="jane.doe@acmepharma.com",
            department_id=quality_dept.id,
            designation="QC Specialist",
            date_joined=date(2023, 3, 10)
        )

        db.add_all([john_smith, jane_doe])
        db.commit()

        # Create products
        vitamin_d = Product(
            name="Vitamin D Tablets",
            category="Supplements",
            unit_price=0.50
        )

        db.add(vitamin_d)
        db.commit()

        # Create batch
        batch = Batch(
            product_id=vitamin_d.id,
            batch_code="VDT-052025-A",
            quantity=10000,
            manufactured_date=date(2025, 5, 20),
            expiry_date=date(2027, 5, 20),
            created_by=jane_doe.id
        )

        db.add(batch)
        db.commit()

        # Create tracking records
        tracking_records = [
            BatchTracking(
                batch_id=batch.id,
                location="Production Floor A",
                status=BatchStatus.MANUFACTURED,
                timestamp=datetime(2025, 5, 20, 10, 0, 0),
                handled_by=jane_doe.id
            ),
            BatchTracking(
                batch_id=batch.id,
                location="Quality Control Lab",
                status=BatchStatus.IN_TRANSIT,
                timestamp=datetime(2025, 5, 21, 14, 30, 0),
                handled_by=jane_doe.id
            ),
            BatchTracking(
                batch_id=batch.id,
                location="Warehouse B",
                status=BatchStatus.DELIVERED,
                timestamp=datetime(2025, 5, 22, 9, 15, 0),
                handled_by=john_smith.id
            )
        ]

        db.add_all(tracking_records)
        db.commit()

        print("Database initialized successfully!")
        print("Sample data created:")
        print(f"- Batch: {batch.batch_code}")
        print(f"- Current location: Warehouse B")
        print(f"- Handler: John Smith")

    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_database()