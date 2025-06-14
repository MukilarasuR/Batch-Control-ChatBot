from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from explore.sql_agent import agent_executor  # Correct import

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str  # ✅ Expecting 'message'

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    result = agent_executor.invoke({"input": request.message})
    response = result["output"].replace("```", "").strip()
    return {"response": response}
