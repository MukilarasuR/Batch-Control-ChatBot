import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict

from app.database import get_db
from app.schemas.batch_control import ChatRequest, ChatResponse
from app.services.chat_handler import process_user_query
from app.crud.batch_control import batch_crud

router = APIRouter(prefix="/api/v1", tags=["batch-control"])

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "batch-control-chatbot"}

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Main chatbot endpoint – processes natural language queries about batch tracking
    using the NLU + CRUD logic (not RAG).
    """
    try:
        response_text, intent, entities = await process_user_query(request.message, db)
        return ChatResponse(
            success=True,
            message=response_text,
            intent="intent",         # Optional: You can return intent from process_user_query if needed
            entities={},           # Optional: You can enhance process_user_query to return entities too
            data=None
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

@router.get("/batch/{batch_code}")
async def get_batch_info(batch_code: str, db: Session = Depends(get_db)):
    """
    Retrieve current tracking info for a specific batch by code.
    """
    try:
        batch_info = batch_crud.get_current_batch_location(db, batch_code)
        if not batch_info:
            raise HTTPException(status_code=404, detail="Batch not found")
        return batch_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))