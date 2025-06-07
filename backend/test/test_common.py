import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sys
import os
print("Current working directory:", os.getcwd())
print("sys.path:", sys.path)



# from app.models.employee_department import Base, Department, Employee
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.employee_department import Base, Department, Employee
import uuid
from datetime import date


# Use a test-specific SQLite DB
TEST_DB_URL = "sqlite:///./test_models.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def test_db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    # Drop tables after tests
    Base.metadata.drop_all(bind=engine)


def test_create_department_and_employee(test_db):
    # Create department
    department = Department(name="Engineering")
    test_db.add(department)
    test_db.commit()
    test_db.refresh(department)

    # Create employee in department
    employee = Employee(
        name="John Doe",
        email="john@example.com",
        designation="Engineer",
        date_joined=date.today(),
        department_id=department.id
    )
    test_db.add(employee)
    test_db.commit()
    test_db.refresh(employee)

    # Set head of department
    department.head_id = employee.id
    test_db.commit()
    test_db.refresh(department)

    # Assertions
    assert department.id is not None
    assert employee.id is not None
    assert department.head_id == employee.id
    assert employee.department_id == department.id
    assert department.employees[0].email == "john@example.com"
