from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, ForeignKey, Enum, UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import enum

class BatchStatus(enum.Enum):
    MANUFACTURED = "Manufactured"
    IN_TRANSIT = "In Transit"
    DELIVERED = "Delivered"

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String)
    unit_price = Column(Numeric(10, 2))
    
    batches = relationship("Batch", back_populates="product")

class Batch(Base):
    __tablename__ = "batches"
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    batch_code = Column(String, unique=True, nullable=False)
    quantity = Column(Integer)
    manufactured_date = Column(Date)
    expiry_date = Column(Date)
    created_by = Column(UUID(as_uuid=True), ForeignKey("employees.id"))
    
    product = relationship("Product", back_populates="batches")
    creator = relationship("Employee")
    tracking_records = relationship("BatchTracking", back_populates="batch")
    tracking_history = relationship("TrackingInfo", back_populates="batch", cascade="all, delete-orphan")

class BatchTracking(Base):
    __tablename__ = "batch_tracking"
    
    id = Column(Integer, primary_key=True)
    batch_id = Column(Integer, ForeignKey("batches.id"))
    location = Column(String)
    status = Column(Enum(BatchStatus))
    timestamp = Column(DateTime)
    handled_by = Column(UUID(as_uuid=True), ForeignKey("employees.id"))
    
    batch = relationship("Batch", back_populates="tracking_records")
    handler = relationship("Employee")

class TrackingInfo(Base):
    __tablename__ = "tracking_info"

    id = Column(Integer, primary_key=True)
    batch_id = Column(Integer, ForeignKey("batches.id"))
    status = Column(Enum(BatchStatus), nullable=False)
    location = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    batch = relationship("Batch", back_populates="tracking_history")