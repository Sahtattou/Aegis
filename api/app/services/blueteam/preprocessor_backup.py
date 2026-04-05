import re
import unicodedata
from typing import Literal
from pydantic import BaseModel, Field

LanguageHint = Literal["ar", "fr", "mixed", "unknown"]

class PreprocessResult(BaseModel):
    original_text: str 
    normalized_text : str
    tokens: list[str] = Field(default_factory=list)
    language_hint: LanguageHint = "unknown"

_ARABIC_RANGE = re.compile(r"[\u0600-\u06FF]")
_FRENCH_HINT = re.compile(r"[àâçéèêëîïôûùüÿœæ]", re.IGNORECASE)
_URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
_EMAIL_RE = re.compile(r"\b[\w\.-]+@[\w\.-]+\.\w+\b")
_WHITESPACE_RE = re.compile(r"\s+")

def _detect_language(text: str) -> LanguageHint:
    has_ar = bool(_ARABIC_RANGE.search(text))
    has_fr = bool(_FRENCH_HINT.search(text))
    if has_ar and has_fr:
        return "mixed"
    if has_ar:
        return "ar"
    if has_fr:
        return "fr"
    return "unknown"

def _normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text).lower().strip()
    normalized = _URL_RE.sub(" <url> ", normalized)
    normalized = _EMAIL_RE.sub(" <email> ", normalized)
    normalized = _WHITESPACE_RE.sub(" ", normalized)
    return normalized


def preprocess(text: str) -> PreprocessResult:
    normalized = _normalize_text(text)
    tokens = [t for t in normalized.split(" ") if t ]
    return PreprocessResult(
        original_text=text,
        normalized_text=normalized,
        tokens=tokens,
        language_hint=_detect_language(text),
    )
