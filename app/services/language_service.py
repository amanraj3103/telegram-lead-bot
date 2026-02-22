"""
Language detection and management service
"""
from typing import Optional
try:
    from langdetect import detect
except ImportError:
    # Fallback if langdetect is not available
    def detect(text: str) -> str:
        return "en"

from app.utils.consent_texts import DEFAULT_LANGUAGE

SUPPORTED_LANGUAGES = {
    "en": "English",
    "pl": "Polish",
    "de": "German",
    "es": "Spanish",
    "uk": "Ukrainian",
    "hi": "Hindi",
    "ml": "Malayalam"
}

def detect_language(text: str) -> str:
    """
    Detect language from text using langdetect
    Falls back to English if detection fails or language is unsupported
    """
    if not text or not isinstance(text, str):
        return DEFAULT_LANGUAGE

    try:
        detected = detect(text.strip())
        # Only return supported languages, otherwise default to English
        return detected if detected in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE
    except Exception:
        # If detection fails, default to English
        return DEFAULT_LANGUAGE

def is_supported_language(language_code: str) -> bool:
    """Check if language code is supported"""
    return language_code in SUPPORTED_LANGUAGES

def get_supported_languages() -> dict:
    """Get all supported languages"""
    return SUPPORTED_LANGUAGES.copy()

def normalize_language_code(language_code: str) -> str:
    """Normalize language code to supported format"""
    if not language_code or not isinstance(language_code, str):
        return DEFAULT_LANGUAGE

    lang_code = language_code.lower().strip()
    return lang_code if lang_code in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE

