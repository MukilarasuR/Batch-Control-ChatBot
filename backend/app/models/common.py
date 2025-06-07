import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


from sqlalchemy import Column, String, Date, UUID, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import uuid


class Department(Base):
    __tablename__ = "departments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    head_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"))

    # Relationships
    employees = relationship("Employee", back_populates="department", foreign_keys="[Employee.department_id]")
    head = relationship("Employee", foreign_keys=[head_id])


class Employee(Base):
    __tablename__ = "employees"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"))
    designation = Column(String)
    date_joined = Column(Date)

    # Relationships
    department = relationship("Department", back_populates="employees", foreign_keys=[department_id])