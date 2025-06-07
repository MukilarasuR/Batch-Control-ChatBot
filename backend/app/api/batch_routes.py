from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.crud.batch_control import batch_crud

router = APIRouter(prefix="/batches", tags=["Batches"])

@router.get("/{batch_code}/current-location")
def get_current_location(batch_code: str, db: Session = Depends(get_db)):
    result = batch_crud.get_current_batch_location(db, batch_code)
    if not result:
        raise HTTPException(status_code=404, detail="Batch not found or no tracking info.")
    return result

@router.get("/status/{status}")
def get_batches_by_status(status: str, db: Session = Depends(get_db)):
    result = batch_crud.get_batches_by_status(db, status)
    return result
