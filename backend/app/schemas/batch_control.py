from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    success: bool
    message: str
    intent: str
    entities: Dict[str, Any]
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.now()

class BatchLocationResponse(BaseModel):
    batch_code: str
    location: str
    status: str
    timestamp: datetime
    handler: Optional[str]