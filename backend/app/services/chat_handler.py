from sqlalchemy.orm import Session
from app.crud.batch_control import batch_crud
from app.services.nlu import NLUService, QueryIntent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from app.config import settings  # ✅ Load env vars
from typing import Tuple, Dict  # ✅ Needed for return typing


# Initialize services
nlu_service = NLUService()

# ✅ Gemini LLM setup
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    google_api_key=settings.GEMINI_API_KEY,
    temperature=0.2
)

# ✅ Core chatbot logic
async def process_user_query(query: str, db: Session) -> str:
    parsed = nlu_service.process_query(query)
    intent = parsed["intent"]
    entities = parsed["entities"]
    batch_code = entities.get("batch_code")
    status = entities.get("status")

    if intent == QueryIntent.BATCH_LOCATION:
        if not batch_code:
            return "Please specify the batch code to find its location."
        data = batch_crud.get_current_batch_location(db, batch_code)
        if not data:
            return f"No tracking info found for batch {batch_code}."
        return (
            f"Batch {batch_code} is currently at {data['location']} with status '{data['status']}'. "
            f"It was last handled by {data['handler']} on {data['timestamp']}."
        )

    elif intent == QueryIntent.BATCH_HISTORY:
        if not batch_code:
            return "Please specify a batch code to view its history."
        batch = batch_crud.get_batch_by_code(db, batch_code)
        if not batch:
            return f"No batch found with code {batch_code}."
        history = batch_crud.get_batch_tracking(db, batch.id)
        if not history:
            return f"No tracking history found for batch {batch_code}."
        return f"Tracking history for batch {batch_code}:\n" + "\n".join(
            f"- {entry.timestamp.strftime('%Y-%m-%d %H:%M')} at {entry.location} (status: {entry.status.value})"
            for entry in history
        )

    elif intent == QueryIntent.BATCHES_BY_STATUS:
        if not status:
            return "Please specify a valid status like 'manufactured', 'in transit', or 'delivered'."
        results = batch_crud.get_batches_by_status(db, status.lower().replace(" ", "_"))
        if not results:
            return f"No batches found with status '{status}'."
        return f"Batches with status '{status}':\n" + "\n".join(
            f"- {r['batch_code']} ({r['product_name']} at {r['location']}, handler: {r['handler']})"
            for r in results
        )

    # ✅ Fallback to Gemini for unknown intents
    gemini_response = llm.invoke([HumanMessage(content=query)])
    return gemini_response.content.strip(), intent, entities
