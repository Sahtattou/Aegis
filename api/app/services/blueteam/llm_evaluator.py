from dataclasses import dataclass

from app.models.detection import ThreatClassLabel


@dataclass
class LLMEvaluationResult:
    llm_confidence: float
    threat_class: ThreatClassLabel
    key_indicators: list[str]
    context_match: str
    available: bool
    provenance: str


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def evaluate_with_llm(
    *,
    attack_text: str,
    ioc_summary: dict[str, int],
    retrieved_context: list[str],
) -> LLMEvaluationResult:
    lowered = attack_text.lower()
    suspicious_terms = [
        "urgent",
        "verify",
        "password",
        "account",
        "عاجل",
        "تحقق",
        "mot de passe",
    ]

    term_hits = [term for term in suspicious_terms if term in lowered]
    signal_score = 0.0
    signal_score += min(0.4, len(term_hits) * 0.08)
    signal_score += min(0.2, ioc_summary.get("url_count", 0) * 0.05)
    signal_score += min(0.2, ioc_summary.get("suspicious_domain_count", 0) * 0.1)
    signal_score += min(0.2, ioc_summary.get("suspicious_extension_count", 0) * 0.1)
    llm_confidence = _clamp(0.2 + signal_score)

    if llm_confidence >= 0.75:
        threat_class: ThreatClassLabel = "malicious"
    elif llm_confidence >= 0.45:
        threat_class = "suspicious"
    else:
        threat_class = "benign"

    key_indicators = list(term_hits)
    if ioc_summary.get("url_count", 0) > 0:
        key_indicators.append("url_present")
    if ioc_summary.get("suspicious_domain_count", 0) > 0:
        key_indicators.append("typosquat_domain")
    if ioc_summary.get("suspicious_extension_count", 0) > 0:
        key_indicators.append("suspicious_attachment")

    if retrieved_context:
        context_match = "Context correlated with historical incidents"
    else:
        context_match = "No contextual correlation found"

    return LLMEvaluationResult(
        llm_confidence=llm_confidence,
        threat_class=threat_class,
        key_indicators=key_indicators,
        context_match=context_match,
        available=False,
        provenance="llm_fallback_heuristic",
    )
