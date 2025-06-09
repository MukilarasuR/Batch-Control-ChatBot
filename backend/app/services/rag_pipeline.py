import sys
import os
from dotenv import load_dotenv
load_dotenv()

from typing import Dict, Any
from sqlalchemy.orm import Session
from langchain.schema import HumanMessage

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.config import settings
from app.services.nlu import nlu_service, QueryIntent
from app.crud.batch_control import batch_crud

# Load Gemini
if os.getenv("ENV") == "test":
    from unittest.mock import MagicMock
    LLM_INSTANCE = MagicMock()
else:
    from langchain_google_genai import ChatGoogleGenerativeAI
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set in your .env or config.")
    LLM_INSTANCE = ChatGoogleGenerativeAI(
        model=os.getenv("GENAI_MODEL", "gemini-pro"),
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.1
    )


class RAGPipeline:
    def __init__(self):
        self.llm = LLM_INSTANCE
        self.response_templates = {
            QueryIntent.BATCH_LOCATION: """
Batch {batch_code} is currently at {location}.
Status: {status}
Last handled by: {handler} on {timestamp}.
""",
            QueryIntent.BATCH_HANDLER: """
Batch {batch_code} was handled by {handler}.
Current status: {status} at {location}.
""",
            QueryIntent.BATCH_HISTORY: """
Tracking history for batch {batch_code}:
{history}
""",
            QueryIntent.BATCHES_BY_STATUS: """
Batches with status "{status}":
{batch_list}
""",
            QueryIntent.BATCH_INFO: """
Batch {batch_code} Info:
• Product: {product_name}
• Quantity: {quantity} units
• Manufactured on: {manufactured_date}
• Current Status: {status}
• Location: {location}
"""
        }

    def process_query(self, query: str, db: Session) -> Dict[str, Any]:
        print(f"[DEBUG] User Query: {query}")
        nlu_result = nlu_service.process_query(query)
        intent = nlu_result["intent"]
        entities = nlu_result["entities"]
        print(f"[DEBUG] Intent: {intent}, Entities: {entities}")

        # Friendly chatbot responses
        if intent == QueryIntent.GREETING:
            return {
                "success": True,
                "message": "👋 Hello! How can I help you today?",
                "intent": intent.value,
                "entities": entities
            }

        elif intent == QueryIntent.THANKS:
            return {
                "success": True,
                "message": "😊 You're welcome! Let me know if you need anything else.",
                "intent": intent.value,
                "entities": entities
            }

        elif intent == QueryIntent.FAREWELL:
            return {
                "success": True,
                "message": "👋 Goodbye! Have a great day!",
                "intent": intent.value,
                "entities": entities
            }

        # Fallback for unknown
        if intent == QueryIntent.UNKNOWN:
            prompt = f"You are an ERP assistant. Try to respond clearly or casually.\n\nUser Query: {query}"
            try:
                llm_response = self.llm.invoke([HumanMessage(content=prompt)]).content
            except Exception as e:
                print(f"[LLM ERROR] {e}")
                llm_response = "Sorry, I couldn't understand your question. Please try again."

            return {
                "success": True,
                "message": llm_response.strip(),
                "intent": intent.value,
                "entities": entities
            }

        # Structured queries
        data = self._retrieve_data(intent, entities, db)
        if not data:
            return {
                "success": False,
                "message": "No data found. Please check the batch code or status.",
                "intent": intent.value,
                "entities": entities
            }

        response = self._generate_response(intent, data)
        return {
            "success": True,
            "message": response,
            "intent": intent.value,
            "entities": entities,
            "data": data
        }

    def _retrieve_data(self, intent: QueryIntent, entities: Dict[str, Any], db: Session) -> Dict[str, Any] | None:
        batch_code = entities.get("batch_code")
        status = entities.get("status")

        if status:
            status = status.lower()

        try:
            if intent in [QueryIntent.BATCH_LOCATION, QueryIntent.BATCH_HANDLER, QueryIntent.BATCH_INFO]:
                if not batch_code:
                    return None

                if intent in [QueryIntent.BATCH_LOCATION, QueryIntent.BATCH_HANDLER]:
                    return batch_crud.get_current_batch_location(db, batch_code)

                if intent == QueryIntent.BATCH_INFO:
                    batch = batch_crud.get_batch_by_code(db, batch_code)
                    if batch:
                        current = batch_crud.get_current_batch_location(db, batch_code)
                        return {
                            "batch_code": batch.batch_code,
                            "product_name": batch.product.name,
                            "quantity": batch.quantity,
                            "manufactured_date": batch.manufactured_date,
                            "status": current["status"] if current else "Unknown",
                            "location": current["location"] if current else "Unknown"
                        }

            elif intent == QueryIntent.BATCH_HISTORY and batch_code:
                batch = batch_crud.get_batch_by_code(db, batch_code)
                if batch:
                    history = batch_crud.get_batch_tracking(db, batch.id)
                    return {
                        "batch_code": batch_code,
                        "history": [
                            {
                                "location": record.location,
                                "status": record.status.value,
                                "timestamp": record.timestamp,
                                "handler": record.handler.name if record.handler else "Unknown"
                            }
                            for record in history
                        ]
                    }

            elif intent == QueryIntent.BATCH_CHART and batch_code:
                batch = batch_crud.get_batch_by_code(db, batch_code)
                if batch:
                    history = batch_crud.get_batch_tracking(db, batch.id)
                    return {
                        "batch_code": batch_code,
                        "chart_data": [
                            {
                                "x": record.timestamp.strftime("%Y-%m-%d %H:%M"),
                                "y": record.status.value
                            }
                            for record in history
                        ]
                    }

            elif intent == QueryIntent.BATCHES_BY_STATUS and status:
                return {
                    "status": status,
                    "batches": batch_crud.get_batches_by_status(db, status)
                }

        except Exception as e:
            print(f"[ERROR] Data fetch failed: {e}")
        return None

    def _generate_response(self, intent: QueryIntent, data: Dict[str, Any]) -> str:
        template = self.response_templates.get(intent)

        try:
            if intent == QueryIntent.BATCH_LOCATION:
                return template.format(
                    batch_code=data["batch_code"],
                    location=data["location"],
                    status=data["status"],
                    timestamp=data["timestamp"].strftime("%Y-%m-%d %H:%M"),
                    handler=data.get("handler", "Unknown")
                ).strip()

            elif intent == QueryIntent.BATCH_HANDLER:
                return template.format(
                    batch_code=data["batch_code"],
                    handler=data.get("handler", "Unknown"),
                    status=data["status"],
                    location=data["location"]
                ).strip()

            elif intent == QueryIntent.BATCH_HISTORY:
                history_text = "\n".join([
                    f"• {record['timestamp'].strftime('%Y-%m-%d %H:%M')} - {record['status']} at {record['location']} (Handler: {record['handler']})"
                    for record in data["history"]
                ])
                return template.format(batch_code=data["batch_code"], history=history_text).strip()

            elif intent == QueryIntent.BATCHES_BY_STATUS:
                batch_list = "\n".join([
                    f"• {b['batch_code']} - {b['product_name']} @ {b['location']} (Handler: {b['handler']})"
                    for b in data["batches"]
                ]) or "No batches found."
                return template.format(status=data["status"], batch_list=batch_list).strip()

            elif intent == QueryIntent.BATCH_INFO:
                return template.format(**data).strip()

            elif intent == QueryIntent.BATCH_CHART:
                return f"Here is the trend chart for batch {data['batch_code']}."

        except KeyError as e:
            return f"Missing data field in template: {e}"

        return "Sorry, something went wrong while generating the response."


# ✅ Export singleton
rag_pipeline = RAGPipeline()
