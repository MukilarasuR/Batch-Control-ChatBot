from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional, List

from app.models.batch_control import Batch, BatchTracking, Product, TrackingInfo
from app.models.common import Employee

# # ✅ ADDED — If you're using enums for status
# from app.models.enums import BatchStatusEnum  # 🔁 ADD THIS LINE if you're using enum type

class BatchCRUD:
    @staticmethod
    def get_batch_by_code(db: Session, batch_code: str) -> Optional[Batch]:
        return db.query(Batch).filter(Batch.batch_code == batch_code).first()

    @staticmethod
    def get_batch_tracking(db: Session, batch_id: int) -> List[TrackingInfo]:
        return db.query(TrackingInfo).filter(TrackingInfo.batch_id == batch_id).order_by(TrackingInfo.timestamp).all()

    @staticmethod
    def get_current_batch_location(db: Session, batch_code: str) -> Optional[dict]:
        batch = BatchCRUD.get_batch_by_code(db, batch_code)
        if not batch:
            return None

        latest_tracking = db.query(BatchTracking) \
            .filter(BatchTracking.batch_id == batch.id) \
            .order_by(BatchTracking.timestamp.desc()) \
            .first()

        if not latest_tracking:
            return None

        return {
            "batch_code": batch.batch_code,
            "location": latest_tracking.location,
            "status": latest_tracking.status.value,
            "timestamp": latest_tracking.timestamp,
            "handler": latest_tracking.handler.name if latest_tracking.handler else None
        }

    @staticmethod
    def get_batches_by_status(db: Session, status: str) -> List[dict]:
        subquery = db.query(BatchTracking.batch_id, func.max(BatchTracking.timestamp).label('max_time')) \
            .group_by(BatchTracking.batch_id).subquery()

        results = db.query(Batch, BatchTracking) \
            .join(BatchTracking, Batch.id == BatchTracking.batch_id) \
            .join(subquery, and_(
                BatchTracking.batch_id == subquery.c.batch_id,
                BatchTracking.timestamp == subquery.c.max_time
            )) \
            .filter(BatchTracking.status == status) \
            .all()

        return [
            {
                "batch_code": batch.batch_code,
                "product_name": batch.product.name,
                "location": tracking.location,
                "status": tracking.status.value,
                "handler": tracking.handler.name if tracking.handler else None
            }
            for batch, tracking in results
        ]
    
    
    # ✅ ADDED — New function for test_database.py
    @staticmethod
    def get_batch_statistics(db: Session) -> dict:
        total_batches = db.query(func.count(Batch.id)).scalar()

        # 🔁 If your BatchTracking.status is an enum, use the enum:
        active_batches = db.query(BatchTracking) \
            .join(Batch, Batch.id == BatchTracking.batch_id) \
            .filter(BatchTracking.status == BatchStatusEnum.ACTIVE).count()

        return {
            "total_batches": total_batches,
            "active_batches": active_batches
        }


batch_crud = BatchCRUD()