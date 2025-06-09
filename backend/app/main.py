import sys
import os
from dotenv import load_dotenv
load_dotenv()
# Add parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.config import settings
from app.database import Base, get_db
from app.api.batch_control import router as batch_router
from app.services.rag_pipeline import rag_pipeline  # ✅ Updated import

# ✅ Create DB engine and tables
engine = create_engine(settings.DATABASE_URL)
Base.metadata.create_all(bind=engine)

# ✅ Initialize FastAPI app
app = FastAPI(
    title="ERP Batch Control Chatbot",
    description="AI-powered chatbot for pharmaceutical batch tracking",
    version="1.0.0"
)

# ✅ Enable CORS (frontend access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 🔁 Update this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Define request model
class ChatRequest(BaseModel):
    query: str

# ✅ /chat endpoint using RAGPipeline
@app.post("/chat")
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        result = rag_pipeline.process_query(request.query, db)

        return {
            "success": result["success"],
            "message": result["message"],
            "intent": result["intent"],
            "entities": result["entities"],
            "data": result.get("data")
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Error: {str(e)}"})

# ✅ Include batch control endpoints
app.include_router(batch_router)

# ✅ Health check root endpoint
@app.get("/")
async def root():
    return {
        "message": "ERP Batch Control Chatbot API",
        "version": "1.0.0",
        "status": "running"
    }

# ✅ Optional mock message for UI testing
@app.get("/messages")
async def get_messages():
    return [{
        "id": "1",
        "role": "assistant",
        "content": "Hello! How can I help you today?",
        "timestamp": "2025-06-04T10:00:00Z"
    }]

# ✅ Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )
