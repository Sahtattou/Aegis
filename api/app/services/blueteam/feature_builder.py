from dataclasses import dataclass
import re

from .ioc_extractor import IOCExtractionResult


@dataclass
class FeatureVector:
    names: list[str]
    values: list[float]


URGENCY_TERMS = [
    "سيُغلق",
    "عاجل",
    "فوري",
    "خلال 24 ساعة",
    "urgent",
    "immédiat",
    "immediate",
    "verify",
]

BRAND_TERMS = [
    "poste tunisienne",
    "poste.tn",
    "biat",
    "stb",
    "tunisie telecom",
    "tunisietelecom",
    "ooredoo",
]

ARABIC_CHARS = re.compile(r"[\u0600-\u06FF]")
DIGIT_CHARS = re.compile(r"\d")


def _count_occurrences(text: str, terms: list[str]) -> int:
    lowered = text.lower()
    return sum(lowered.count(term.lower()) for term in terms)


def _arabic_dominance(text: str) -> float:
    if not text:
        return 0.0
    arabic_count = len(ARABIC_CHARS.findall(text))
    return arabic_count / max(len(text), 1)


def build_handcrafted_features(text: str, iocs: IOCExtractionResult) -> FeatureVector:
    token_count = max(len(text.split()), 1)
    url_count = len(iocs.urls)
    domain_typosquat_count = len(iocs.suspicious_domains)
    phone_count = len(iocs.phone_numbers)
    base64_count = len(iocs.base64_chunks)
    ext_count = len(iocs.suspicious_extensions)
    urgency_count = _count_occurrences(text, URGENCY_TERMS)
    brand_match_count = _count_occurrences(text, BRAND_TERMS)
    digit_count = len(DIGIT_CHARS.findall(text))
    text_length = len(text)
    link_to_text_ratio = url_count / token_count
    is_arabic_dominant = 1.0 if _arabic_dominance(text) >= 0.4 else 0.0

    names = [
        "urgency_count",
        "brand_match_count",
        "suspicious_url_count",
        "domain_typosquat_count",
        "phone_count",
        "base64_count",
        "suspicious_extension_count",
        "link_to_text_ratio",
        "message_length",
        "digit_count",
        "is_arabic_dominant",
    ]
    values = [
        float(urgency_count),
        float(brand_match_count),
        float(url_count),
        float(domain_typosquat_count),
        float(phone_count),
        float(base64_count),
        float(ext_count),
        float(link_to_text_ratio),
        float(text_length),
        float(digit_count),
        float(is_arabic_dominant),
    ]
    return FeatureVector(names=names, values=values)


def combine_feature_vector(
    embedding: list[float], handcrafted: FeatureVector
) -> FeatureVector:
    embedding_names = [f"emb_{idx}" for idx in range(len(embedding))]
    names = embedding_names + handcrafted.names
    values = list(embedding) + handcrafted.values
    return FeatureVector(names=names, values=values)
