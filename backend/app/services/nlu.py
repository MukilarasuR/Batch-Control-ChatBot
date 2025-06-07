import re
from typing import Dict, Optional
from enum import Enum

class QueryIntent(Enum):
    BATCH_LOCATION = "batch_location"
    BATCH_HANDLER = "batch_handler"
    BATCH_HISTORY = "batch_history"
    BATCHES_BY_STATUS = "batches_by_status"
    BATCH_INFO = "batch_info"
    BATCH_CHART = "batch_chart"
    UNKNOWN = "unknown"

class EntityExtractor:
    def __init__(self):
        self.batch_code_pattern = r'[A-Z]{3}-\d{6}-[A-Z]'  # e.g., VDT-052025-A
        self.status_patterns = {
            'manufactured': r'\b(manufactured|production|made)\b',
            'in_transit': r'\b(transit|shipping|transport|moving)\b',
            'delivered': r'\b(delivered|received|arrived|completed)\b'
        }

    def extract_batch_code(self, text: str) -> Optional[str]:
        # Try strict pattern first (e.g. VDT-052025-A)
        match = re.search(self.batch_code_pattern, text.upper())
        if match:
            return match.group()
        # Fallback: try to find numeric batch code like "102" or "1234"
        simple_num_match = re.search(r'\b\d{2,6}\b', text)
        if simple_num_match:
            return simple_num_match.group()
        return None

    def extract_status(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        for status, pattern in self.status_patterns.items():
            if re.search(pattern, text_lower):
                return status.replace('_', ' ').title()
        return None

class IntentClassifier:
    def __init__(self):
        self.intent_patterns = {
            QueryIntent.BATCH_LOCATION: [
                r'\b(where|location|located|position|current place)\b'
            ],
            QueryIntent.BATCH_HANDLER: [
                r'\b(who|handler|handled|delivered by|responsible|employee)\b'
            ],
            QueryIntent.BATCH_HISTORY: [
                r'\b(history|tracking|timeline|complete record|how it went)\b'
            ],
            QueryIntent.BATCHES_BY_STATUS: [
                r'\b(batches|all|list|show)\b.*\b(status|state|condition|delivered|manufactured|in transit|completed)\b'
            ],
            QueryIntent.BATCH_INFO: [
                r'\b(info|information|details|about|summary)\b'
            ],
            QueryIntent.BATCH_CHART: [
                r'\b(graph|chart|plot|visual|trend|line graph)\b'
            ],
        }

    def classify_intent(self, text: str) -> QueryIntent:
        text_lower = text.lower()
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return intent
        return QueryIntent.UNKNOWN

class NLUService:
    def __init__(self):
        self.entity_extractor = EntityExtractor()
        self.intent_classifier = IntentClassifier()

    def process_query(self, query: str) -> Dict:
        return {
            "intent": self.intent_classifier.classify_intent(query),
            "entities": {
                "batch_code": self.entity_extractor.extract_batch_code(query),
                "status": self.entity_extractor.extract_status(query)
            },
            "original_query": query
        }

# Instance to use in chat_handler
nlu_service = NLUService()
