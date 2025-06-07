import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from app.services.rag_pipeline import rag_pipeline
from app.services.nlu import QueryIntent


@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)


def test_unknown_intent_uses_llm(mock_db, monkeypatch):
    query = "Tell me a joke"

    # ✅ Monkeypatch NLU to return UNKNOWN intent
    monkeypatch.setattr(
        "app.services.nlu.nlu_service.process_query",
        lambda q: {"intent": QueryIntent.UNKNOWN, "entities": {}}
    )

    # ✅ Monkeypatch LLM to avoid real API call
    rag_pipeline.llm.invoke = MagicMock(return_value=MagicMock(content="Here’s a test joke"))

    result = rag_pipeline.process_query(query, mock_db)

    assert result["success"] is True
    assert result["intent"] == "unknown"
    assert result["message"] == "Here’s a test joke"

def test_batch_info_intent(mock_db, monkeypatch):
    from app.crud.batch_control import batch_crud

    query = "Give info about batch B123"

    # ✅ Monkeypatch NLU output
    monkeypatch.setattr(
        "app.services.nlu.nlu_service.process_query",
        lambda q: {"intent": QueryIntent.BATCH_INFO, "entities": {"batch_code": "B123"}}
    )

    # ✅ Define mock batch object properly
    class MockProduct:
        name = "Paracetamol"

    class MockBatch:
        batch_code = "B123"
        product = MockProduct()
        quantity = 1000
        manufactured_date = "2024-05-01"

    # ✅ Mock database calls
    monkeypatch.setattr(batch_crud, "get_batch_by_code", lambda db, code: MockBatch())
    monkeypatch.setattr(batch_crud, "get_current_batch_location", lambda db, code: {
        "location": "Warehouse A",
        "status": "In Transit"
    })

    result = rag_pipeline.process_query(query, mock_db)

    assert result["success"] is True
    assert result["intent"] == "batch_info"
    assert "Paracetamol" in result["message"]



# def test_batch_info_intent(mock_db, monkeypatch):
#     from app.crud.batch_control import batch_crud

#     query = "Give info about batch B123"

#     # ✅ Monkeypatch NLU output
#     monkeypatch.setattr(
#         "app.services.nlu.nlu_service.process_query",
#         lambda q: {"intent": QueryIntent.BATCH_INFO, "entities": {"batch_code": "B123"}}
#     )



#     # ✅ Mock DB CRUD
#     monkeypatch.setattr(batch_crud, "get_batch_by_code", lambda db, code: MagicMock(
#         batch_code="B123",
#         product=MagicMock(name="Paracetamol"),
#         quantity=1000,
#         manufactured_date="2024-05-01"
#     ))
#     monkeypatch.setattr(batch_crud, "get_current_batch_location", lambda db, code: {
#         "location": "Warehouse A",
#         "status": "In Transit"
#     })

#     result = rag_pipeline.process_query(query, mock_db)

#     assert result["success"] is True
#     assert result["intent"] == "batch_info"
#     assert "Paracetamol" in result["message"]







# import pytest
# from unittest.mock import MagicMock
# from sqlalchemy.orm import Session
# from app.services.rag_pipeline import rag_pipeline
# from app.services.nlu import QueryIntent
# # from pydantic_settings import BaseSettings

# @pytest.fixture
# def mock_db():
#     return MagicMock(spec=Session)


# def test_unknown_intent_uses_llm(mock_db):
#     query = "Tell me a joke"
    
#     # Force NLU to return unknown
#     rag_pipeline.nlu_result = {
#         "intent": QueryIntent.UNKNOWN,
#         "entities": {}
#     }

#     result = rag_pipeline.process_query(query, mock_db)

#     assert result["success"] is True
#     assert "message" in result
#     assert result["intent"] == "unknown"


# def test_batch_info_intent(mock_db, monkeypatch):
#     from app.crud.batch_control import batch_crud

#     query = "Give info about batch B123"

#     def mock_nlu_result(query):
#         return {
#             "intent": QueryIntent.BATCH_INFO,
#             "entities": {"batch_code": "B123"}
#         }

#     def mock_get_batch_by_code(db, batch_code):
#         return MagicMock(
#             batch_code="B123",
#             product=MagicMock(name="Paracetamol"),
#             quantity=1000,
#             manufactured_date="2024-05-01"
#         )

#     def mock_get_current_batch_location(db, batch_code):
#         return {
#             "location": "Warehouse A",
#             "status": "In Transit"
#         }

#     monkeypatch.setattr("app.services.nlu.nlu_service.process_query", mock_nlu_result)
#     monkeypatch.setattr(batch_crud, "get_batch_by_code", mock_get_batch_by_code)
#     monkeypatch.setattr(batch_crud, "get_current_batch_location", mock_get_current_batch_location)

#     result = rag_pipeline.process_query(query, mock_db)

#     assert result["success"] is True
#     assert result["intent"] == "batch_info"
#     assert "Paracetamol" in result["message"]
