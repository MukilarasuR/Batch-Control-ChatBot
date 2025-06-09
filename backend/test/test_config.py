import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from app.config import settings

def test_env_variables():
    assert settings.DATABASE_URL is not None, "DATABASE_URL is not set"
    assert settings.GEMINI_API_KEY is not None, "GEMINI_API_KEY is not set"
    assert settings.REDIS_URL.startswith("redis://"), "REDIS_URL is invalid"
