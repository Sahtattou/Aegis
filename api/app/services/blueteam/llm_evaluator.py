from dataclasses import dataclass
import json
import importlib
import logging

from app.config import settings

from app.models.detection import ThreatClassLabel

logger = logging.getLogger(__name__)


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


def _build_heuristic_result(
    *,
    attack_text: str,
    ioc_summary: dict[str, int],
    retrieved_context: list[str],
    provenance: str,
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
        provenance=provenance,
    )


def _coerce_threat_class(value: str) -> ThreatClassLabel:
    lowered = value.strip().lower()
    if lowered == "malicious":
        return "malicious"
    if lowered == "benign":
        return "benign"
    return "suspicious"


def _evaluate_with_openai(
    *,
    attack_text: str,
    ioc_summary: dict[str, int],
    retrieved_context: list[str],
) -> LLMEvaluationResult | None:
    if not settings.openai_api_key:
        return None

    try:
        openai_module = importlib.import_module("openai")
        OpenAI = getattr(openai_module, "OpenAI")
    except Exception as exc:
        logger.warning("OpenAI dependency unavailable: %s", exc)
        return None

    system_prompt = (
        "You are a Tunisian cybersecurity analyst. "
        "Return strict JSON with keys: llm_confidence, threat_class, key_indicators, context_match. "
        "threat_class must be one of malicious/suspicious/benign."
    )
    user_prompt = json.dumps(
        {
            "attack_text": attack_text,
            "ioc_summary": ioc_summary,
            "retrieved_context": retrieved_context,
        },
        ensure_ascii=False,
    )

    try:
        client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            timeout=settings.openai_timeout_seconds,
            max_retries=settings.openai_max_retries,
        )
        completion = client.chat.completions.create(
            model=settings.openai_model,
            response_format={"type": "json_object"},
            temperature=0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        content = completion.choices[0].message.content or "{}"
        parsed = json.loads(content)

        llm_confidence = _clamp(float(parsed.get("llm_confidence", 0.5)))
        threat_class = _coerce_threat_class(
            str(parsed.get("threat_class", "suspicious"))
        )
        key_indicators_raw = parsed.get("key_indicators", [])
        if not isinstance(key_indicators_raw, list):
            key_indicators_raw = []
        key_indicators = [str(item) for item in key_indicators_raw]
        context_match = str(parsed.get("context_match", "OpenAI evaluation completed"))

        return LLMEvaluationResult(
            llm_confidence=llm_confidence,
            threat_class=threat_class,
            key_indicators=key_indicators,
            context_match=context_match,
            available=True,
            provenance=f"openai:{settings.openai_model}",
        )
    except Exception as exc:
        logger.warning("OpenAI call failed, falling back to heuristic: %s", exc)
        return _build_heuristic_result(
            attack_text=attack_text,
            ioc_summary=ioc_summary,
            retrieved_context=retrieved_context,
            provenance="openai_error_fallback",
        )


def evaluate_with_llm(
    *,
    attack_text: str,
    ioc_summary: dict[str, int],
    retrieved_context: list[str],
) -> LLMEvaluationResult:
    openai_result = _evaluate_with_openai(
        attack_text=attack_text,
        ioc_summary=ioc_summary,
        retrieved_context=retrieved_context,
    )
    if openai_result is not None:
        return openai_result

    return _build_heuristic_result(
        attack_text=attack_text,
        ioc_summary=ioc_summary,
        retrieved_context=retrieved_context,
        provenance="llm_fallback_heuristic",
    )
