from .stopwords import remove_stopwords
from .keywords import extract_keywords
from .summarizer import summarize_text
from .language import detect_language

__all__ = [
    "remove_stopwords",
    "extract_keywords",
    "summarize_text",
    "detect_language"
]
