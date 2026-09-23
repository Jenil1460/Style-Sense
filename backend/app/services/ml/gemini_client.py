"""
GeminiClient — Shared singleton for Google Gemini API access.

Provides:
- get_gemini_client() → cached genai.Client instance
- is_available() → quick check if API key is configured

Used by:
- RecommendationEngine (Gemini 3.6 Flash for AI styling tips)
- AnalysisService (Gemini 3.6 Flash for AI fashion summary)

"""

import logging

logger = logging.getLogger(__name__)

_client = None
_initialized = False


def get_gemini_client():
    """
    Returns a cached genai.Client instance.
    Returns None if GEMINI_API_KEY is not configured.
    """
    global _client, _initialized

    if _initialized:
        return _client

    _initialized = True

    try:
        from app.config.settings import settings
        api_key = getattr(settings, "GEMINI_API_KEY", None)

        if not api_key:
            logger.warning("[GeminiClient] No GEMINI_API_KEY configured — Gemini features disabled.")
            return None

        from google import genai
        _client = genai.Client(api_key=api_key)
        logger.info("[GeminiClient] Gemini client initialized successfully.")
        return _client

    except Exception as e:
        logger.error(f"[GeminiClient] Failed to initialize Gemini client: {e}")
        return None


def is_available() -> bool:
    """Quick check if Gemini client is ready."""
    return get_gemini_client() is not None
