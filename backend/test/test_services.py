from app.services.nlu import nlu_service, QueryIntent

def test_intent_detection_location():
    query = "Where is batch VDT-052025-A?"
    result = nlu_service.process_query(query)
    assert result["intent"] == QueryIntent.BATCH_LOCATION
    assert result["entities"]["batch_code"] == "VDT-052025-A"

def test_intent_detection_handler():
    query = "Who handled VDT-052025-A?"
    result = nlu_service.process_query(query)
    assert result["intent"] == QueryIntent.BATCH_HANDLER
    assert result["entities"]["batch_code"] == "VDT-052025-A"

def test_intent_detection_history():
    query = "Show the full history of ABC-123456-B"
    result = nlu_service.process_query(query)
    assert result["intent"] == QueryIntent.BATCH_HISTORY

def test_intent_detection_by_status():
    query = "List all batches that are delivered"
    result = nlu_service.process_query(query)
    assert result["intent"] == QueryIntent.BATCHES_BY_STATUS  # ✅ updated to match the revised NLU logic
    assert result["entities"]["status"] == "Delivered"        # ✅ check for status extracted

def test_unknown_intent():
    query = "What's the weather in Chennai?"
    result = nlu_service.process_query(query)
    assert result["intent"] == QueryIntent.UNKNOWN
