"""
Enhanced Arabic/Darija preprocessor with comprehensive normalization heuristics.
Phase B.1 integration: Unicode → Diacritics → Characters → Repetition → Whitespace → Darija
Stack: Python stdlib only (unicodedata, re, string)

Research basis:
- Brenndoerfer (2025): Text Normalization for NLP
- Zarnoufi et al. (2020): MANorm - Moroccan Arabic Normalization
- h9-tect, motazsaad, salehA13: Production implementations
"""
import re
import unicodedata
from typing import Literal
from pydantic import BaseModel, Field

LanguageHint = Literal["ar", "fr", "mixed", "unknown"]


class PreprocessResult(BaseModel):
    original_text: str
    normalized_text: str
    tokens: list[str] = Field(default_factory=list)
    language_hint: LanguageHint = "unknown"
    normalization_steps: list[str] = Field(default_factory=list)


# ============================================================================
# PHASE 1: UNICODE NORMALIZATION FOUNDATION
# ============================================================================

def _normalize_nfc(text: str) -> str:
    """Apply NFC normalization - standard Unicode composition."""
    return unicodedata.normalize('NFC', text)


# ============================================================================
# PHASE 2: DIACRITICS REMOVAL (Tashkeel)
# ============================================================================

def _remove_diacritics(text: str) -> str:
    """Remove all Arabic diacritical marks using NFD + category filter."""
    decomposed = unicodedata.normalize('NFD', text)
    filtered = ''.join(
        c for c in decomposed if unicodedata.category(c) != 'Mn'
    )
    return unicodedata.normalize('NFC', filtered)


def _remove_tatweel(text: str) -> str:
    """Remove kashida elongation marks (U+0640)."""
    return text.replace('\u0640', '')


# ============================================================================
# PHASE 3: CHARACTER NORMALIZATION MAPS
# ============================================================================

def _normalize_alef_variants(text: str) -> str:
    """Normalize all alef variants to plain alef (ا)."""
    return re.sub(r'[إأآٱ]', 'ا', text)


def _normalize_taa_marbuta(text: str) -> str:
    """Normalize taa marbuta (ة) to haa (ه)."""
    return text.replace('ة', 'ه')


def _normalize_alef_maqsura(text: str) -> str:
    """Normalize alef maqsura (ى) to yaa (ي)."""
    return text.replace('ى', 'ي')


def _normalize_hamza_variants(text: str) -> str:
    """Normalize hamza-bearing variants to base consonants."""
    text = text.replace('ؤ', 'و')
    text = text.replace('ئ', 'ي')
    return text


def _normalize_moroccan_variants(text: str) -> str:
    """Normalize Moroccan Darija regional character variants."""
    moroccan_map = {
        'ڤ': 'ف',
        'گ': 'ك',
        'چ': 'ج',
        'پ': 'ب',
        'ڜ': 'ش',
    }
    for old, new in moroccan_map.items():
        text = text.replace(old, new)
    return text


def _normalize_digits(text: str) -> str:
    """Convert Arabic-Indic digits (٠-٩) to Western digits (0-9)."""
    arabic_digits = '٠١٢٣٤٥٦٧٨٩'
    western_digits = '0123456789'
    trans_table = str.maketrans(arabic_digits, western_digits)
    return text.translate(trans_table)


# ============================================================================
# PHASE 4: REPETITION NORMALIZATION
# ============================================================================

def _reduce_repeated_chars(text: str, max_repeat: int = 1) -> str:
    """Reduce repeated characters to max_repeat occurrences."""
    return re.sub(rf'(.)\1+', r'\1' * max_repeat, text)


# ============================================================================
# PHASE 5: WHITESPACE NORMALIZATION
# ============================================================================

def _normalize_unicode_spaces(text: str) -> str:
    """Normalize Unicode space variants to regular space."""
    space_variants = [
        '\u00A0',  # No-break space
        '\u2000', '\u2001', '\u2002', '\u2003', '\u2004',
        '\u2005', '\u2006', '\u2007', '\u2008', '\u2009',
        '\u200A', '\u202F', '\u205F', '\u3000',
    ]
    for variant in space_variants:
        text = text.replace(variant, ' ')
    return text


def _collapse_whitespace(text: str) -> str:
    """Collapse multiple spaces to single space."""
    return re.sub(r'\s+', ' ', text).strip()


# ============================================================================
# PHASE 6: PUNCTUATION & NOISE
# ============================================================================

def _remove_html_tags(text: str) -> str:
    """Remove HTML tags."""
    return re.sub(r'<[^>]+>', '', text)


def _remove_urls(text: str) -> str:
    """Remove URLs (both http and www variants)."""
    return re.sub(r'https?://\S+|www\.\S+', '', text, flags=re.IGNORECASE)


def _remove_emails(text: str) -> str:
    """Remove email addresses."""
    return re.sub(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', '', text)


# ============================================================================
# DETECTION HELPERS
# ============================================================================

_ARABIC_RANGE = re.compile(r'[\u0600-\u06FF]')
_FRENCH_HINT = re.compile(r'[àâçéèêëîïôûùüÿœæ]', re.IGNORECASE)


def _detect_language(text: str) -> LanguageHint:
    """Detect language hints from text."""
    has_ar = bool(_ARABIC_RANGE.search(text))
    has_fr = bool(_FRENCH_HINT.search(text))
    if has_ar and has_fr:
        return "mixed"
    if has_ar:
        return "ar"
    if has_fr:
        return "fr"
    return "unknown"


# ============================================================================
# MAIN PREPROCESSING PIPELINE
# ============================================================================

def preprocess(
    text: str,
    aggressive: bool = False,
    track_steps: bool = False,
    keep_digits_as_is: bool = False,
) -> PreprocessResult:
    """
    Comprehensive Arabic/Darija text normalization.

    Args:
        text: Input text to normalize
        aggressive: If True, apply max_repeat=1 for repetition; else max_repeat=2
        track_steps: If True, record normalization steps for debugging
        keep_digits_as_is: If True, don't convert Arabic-Indic digits to Western

    Returns:
        PreprocessResult with normalized_text, tokens, language_hint
    """
    steps = [] if track_steps else []
    normalized = text

    # PHASE 1: Unicode foundation
    normalized = _normalize_nfc(normalized)
    if track_steps:
        steps.append("NFC_normalization")

    # PHASE 2: Diacritics removal
    normalized = _remove_diacritics(normalized)
    if track_steps:
        steps.append("diacritics_removal")

    normalized = _remove_tatweel(normalized)
    if track_steps:
        steps.append("tatweel_removal")

    # PHASE 3: Character normalization
    normalized = _normalize_alef_variants(normalized)
    if track_steps:
        steps.append("alef_normalization")

    normalized = _normalize_taa_marbuta(normalized)
    if track_steps:
        steps.append("taa_marbuta_normalization")

    normalized = _normalize_alef_maqsura(normalized)
    if track_steps:
        steps.append("alef_maqsura_normalization")

    normalized = _normalize_hamza_variants(normalized)
    if track_steps:
        steps.append("hamza_normalization")

    normalized = _normalize_moroccan_variants(normalized)
    if track_steps:
        steps.append("moroccan_variants_normalization")

    if not keep_digits_as_is:
        normalized = _normalize_digits(normalized)
        if track_steps:
            steps.append("digit_normalization")

    # PHASE 4: Repetition reduction
    max_repeat = 1 if aggressive else 2
    normalized = _reduce_repeated_chars(normalized, max_repeat=max_repeat)
    if track_steps:
        steps.append(f"repetition_reduction_max{max_repeat}")

    # PHASE 5: Whitespace normalization
    normalized = _normalize_unicode_spaces(normalized)
    if track_steps:
        steps.append("unicode_space_normalization")

    # PHASE 6: Noise removal
    normalized = _remove_html_tags(normalized)
    if track_steps:
        steps.append("html_removal")

    normalized = _remove_urls(normalized)
    if track_steps:
        steps.append("url_removal")

    normalized = _remove_emails(normalized)
    if track_steps:
        steps.append("email_removal")

    # Final: Collapse whitespace and lowercase
    normalized = _collapse_whitespace(normalized).lower()
    if track_steps:
        steps.append("whitespace_collapse_lowercase")

    # Tokenization
    tokens = [t for t in normalized.split(' ') if t]

    return PreprocessResult(
        original_text=text,
        normalized_text=normalized,
        tokens=tokens,
        language_hint=_detect_language(text),
        normalization_steps=steps,
    )
