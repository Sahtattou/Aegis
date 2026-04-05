import importlib
import logging
from hashlib import sha256
from uuid import uuid4

from app.models.detection import (
    DecisionLabel,
    DetectionBand,
    EvaluateRequest,
    EvaluateResponse,
    GapSeverity,
)
from app.services.blueteam.classifier import classify
from app.services.blueteam.embeddings import embed
from app.services.blueteam.graphrag import retrieve_context
from app.services.blueteam.llm_evaluator import evaluate_with_llm
from app.services.blueteam.preprocessor import preprocess
from app.services.blueteam.rules_engine import apply_rules, load_rules
from app.services.blueteam.xai import explain_french_analyst
from app.services.blueteam.xai_shap import compute_top_contributors

_feature_builder = importlib.import_module("app.services.blueteam.feature_builder")
_ioc_extractor = importlib.import_module("app.services.blueteam.ioc_extractor")

logger = logging.getLogger(__name__)


def _coerce_decision(value: str) -> DecisionLabel:
    if value == "malicious":
        return "malicious"
    if value == "benign":
        return "benign"
    return "suspicious"


def _fuse_confidence(ml_confidence: float, llm_confidence: float) -> float:
    fused = (0.6 * ml_confidence) + (0.4 * llm_confidence)
    return max(0.0, min(1.0, fused))


def _class_score_map() -> dict[str, float]:
    return {"benign": 0.0, "suspicious": 0.0, "malicious": 0.0}


def _resolve_hybrid_decision(
    *,
    ml_label: str,
    ml_confidence: float,
    llm_label: str,
    llm_confidence: float,
    band: DetectionBand,
) -> DecisionLabel:
    if band == DetectionBand.BLIND_SPOT:
        return "suspicious"

    score_map = _class_score_map()
    score_map[ml_label if ml_label in score_map else "suspicious"] += (
        0.6 * ml_confidence
    )
    score_map[llm_label if llm_label in score_map else "suspicious"] += (
        0.4 * llm_confidence
    )

    best_label = max(score_map, key=lambda label: score_map[label])
    if band == DetectionBand.UNCERTAIN and best_label == "benign":
        return "suspicious"
    return _coerce_decision(best_label)


def _resolve_band(fused_confidence: float) -> DetectionBand:
    if fused_confidence >= 0.65:
        return DetectionBand.DETECTED
    if fused_confidence >= 0.40:
        return DetectionBand.UNCERTAIN
    return DetectionBand.BLIND_SPOT


def _resolve_gap_severity(band: DetectionBand) -> GapSeverity:
    if band == DetectionBand.BLIND_SPOT:
        return "HIGH"
    if band == DetectionBand.UNCERTAIN:
        return "MEDIUM"
    return "LOW"


def _rule_explanation(matched_rules: list[str]) -> str | None:
    if not matched_rules:
        return None
    return f"Matched rule(s): {', '.join(matched_rules)}"


def _contributors_as_dicts(top_contributors) -> list[dict[str, float | str]]:
    return [
        {
            "feature": item.feature,
            "contribution": item.contribution,
            "direction": item.direction,
        }
        for item in top_contributors
    ]


def _payload_hash(payload: str) -> str:
    digest = sha256(payload.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def _ioc_summary(ioc_result) -> dict[str, int]:
    return {
        "url_count": len(ioc_result.urls),
        "domain_count": len(ioc_result.domains),
        "suspicious_domain_count": len(ioc_result.suspicious_domains),
        "phone_count": len(ioc_result.phone_numbers),
        "base64_count": len(ioc_result.base64_chunks),
        "suspicious_extension_count": len(ioc_result.suspicious_extensions),
    }


def _handcrafted_dict(feature_vector) -> dict[str, float]:
    return {
        name: value
        for name, value in zip(feature_vector.names, feature_vector.values, strict=True)
    }


def _rule_probability_map(
    decision: DecisionLabel, confidence: float
) -> dict[str, float]:
    bounded = max(0.0, min(1.0, confidence))
    remainder = max(0.0, (1.0 - bounded) / 2.0)
    probability_map = {
        "benign": remainder,
        "suspicious": remainder,
        "malicious": remainder,
    }
    probability_map[decision] = bounded
    total = sum(probability_map.values())
    if total <= 0.0:
        return {"benign": 0.2, "suspicious": 0.6, "malicious": 0.2}
    return {label: value / total for label, value in probability_map.items()}


def run_pipeline(req: EvaluateRequest) -> EvaluateResponse:
    trace: list[str] = []

    preprocessed = preprocess(req.content)
    trace.append("preprocess")

    ioc_result = _ioc_extractor.extract_iocs(preprocessed.normalized_text)
    trace.append("ioc_extraction")

    handcrafted = _feature_builder.build_handcrafted_features(
        preprocessed.normalized_text, ioc_result
    )
    trace.append("feature_builder")

    rules = load_rules()
    trace.append("load_rules")
    rules_result = apply_rules(preprocessed.normalized_text, rules)
    trace.append("rules_engine")

    if rules_result.matched:
        ml_confidence = rules_result.confidence or 0.90
        llm_eval = evaluate_with_llm(
            attack_text=preprocessed.normalized_text,
            ioc_summary=_ioc_summary(ioc_result),
            retrieved_context=[],
        )
        trace.append("llm_evaluator")
        if not llm_eval.available:
            trace.append("llm_fallback")
            logger.warning(
                "LLM unavailable in rules path; using fallback provenance=%s attack_id=%s",
                llm_eval.provenance,
                req.attack_id,
            )
        llm_confidence = llm_eval.llm_confidence
        fused_confidence = _fuse_confidence(ml_confidence, llm_confidence)
        band = _resolve_band(fused_confidence)
        gap_severity = _resolve_gap_severity(band)
        decision = _resolve_hybrid_decision(
            ml_label=_coerce_decision(rules_result.decision or "malicious"),
            ml_confidence=ml_confidence,
            llm_label=llm_eval.threat_class,
            llm_confidence=llm_confidence,
            band=band,
        )

        top_contributors = compute_top_contributors(
            handcrafted.names,
            handcrafted.values,
            top_k=5,
        )
        contributor_dicts = _contributors_as_dicts(top_contributors)
        explanation, explanation_machine = explain_french_analyst(
            decision=decision,
            confidence=fused_confidence,
            evidence=rules_result.evidence,
            top_contributors=contributor_dicts,
            rule_rationale=(
                rules_result.rule_provenance.rationale
                if rules_result.rule_provenance
                else None
            ),
            rule_approved_by=(
                rules_result.rule_provenance.approved_by
                if rules_result.rule_provenance
                else None
            ),
        )
        trace.append("xai_shap")
        trace.append("xai")

        return EvaluateResponse(
            attack_id=req.attack_id,
            pipeline_version="1.3.0",
            ml_confidence=ml_confidence,
            class_probability_map=_rule_probability_map(decision, ml_confidence),
            llm_confidence=llm_confidence,
            llm_threat_class=llm_eval.threat_class,
            llm_key_indicators=llm_eval.key_indicators,
            llm_provenance=llm_eval.provenance,
            fused_confidence=fused_confidence,
            detected=band == DetectionBand.DETECTED,
            band=band,
            threat_class=decision,
            rule_matched=True,
            matched_rules=rules_result.matched_rules,
            rule_id=rules_result.matched_rules[0]
            if rules_result.matched_rules
            else None,
            rule_explanation=_rule_explanation(rules_result.matched_rules),
            rule_rationale=(
                rules_result.rule_provenance.rationale
                if rules_result.rule_provenance
                else None
            ),
            rule_approved_by=(
                rules_result.rule_provenance.approved_by
                if rules_result.rule_provenance
                else None
            ),
            signal_features_count=len(handcrafted.values),
            ioc_summary=_ioc_summary(ioc_result),
            hand_crafted_features=_handcrafted_dict(handcrafted),
            model_label=None,
            decision=decision,
            explanation_fr=explanation,
            xai_top_contributors=contributor_dicts,
            explanation_machine=explanation_machine,
            evidence=rules_result.evidence,
            rag_context_used=[],
            context_match="Rule-based prefilter match",
            blind_spot=band == DetectionBand.BLIND_SPOT,
            gap_severity=gap_severity,
            payload_hash=_payload_hash(req.content),
            audit_event_id=f"audit-{uuid4()}",
            pipeline_trace=trace,
        )

    embedding = embed(preprocessed.normalized_text)
    trace.append("embeddings")
    combined_features = _feature_builder.combine_feature_vector(embedding, handcrafted)
    trace.append("feature_vector_assembly")

    clf = classify(combined_features.values)
    trace.append("classifier")

    gr = retrieve_context(preprocessed.normalized_text)
    trace.append("graphrag")

    llm_eval = evaluate_with_llm(
        attack_text=preprocessed.normalized_text,
        ioc_summary=_ioc_summary(ioc_result),
        retrieved_context=gr.evidence,
    )
    trace.append("llm_evaluator")
    if not llm_eval.available:
        trace.append("llm_fallback")
        logger.warning(
            "LLM unavailable in ml path; using fallback provenance=%s attack_id=%s",
            llm_eval.provenance,
            req.attack_id,
        )

    ml_confidence = clf.confidence
    llm_confidence = llm_eval.llm_confidence
    fused_confidence = _fuse_confidence(ml_confidence, llm_confidence)
    band = _resolve_band(fused_confidence)
    gap_severity = _resolve_gap_severity(band)
    decision = _resolve_hybrid_decision(
        ml_label=clf.label,
        ml_confidence=ml_confidence,
        llm_label=llm_eval.threat_class,
        llm_confidence=llm_confidence,
        band=band,
    )
    if band == DetectionBand.BLIND_SPOT:
        logger.info("Blind spot detection band for attack_id=%s", req.attack_id)

    top_contributors = compute_top_contributors(
        combined_features.names,
        combined_features.values,
        top_k=5,
    )
    contributor_dicts = _contributors_as_dicts(top_contributors)
    explanation, explanation_machine = explain_french_analyst(
        decision=decision,
        confidence=fused_confidence,
        evidence=gr.evidence,
        top_contributors=contributor_dicts,
        rule_rationale=None,
        rule_approved_by=None,
    )
    trace.append("xai_shap")
    trace.append("xai")

    return EvaluateResponse(
        attack_id=req.attack_id,
        pipeline_version="1.3.0",
        ml_confidence=ml_confidence,
        class_probability_map=clf.probability_map,
        llm_confidence=llm_confidence,
        llm_threat_class=llm_eval.threat_class,
        llm_key_indicators=llm_eval.key_indicators,
        llm_provenance=llm_eval.provenance,
        fused_confidence=fused_confidence,
        detected=band == DetectionBand.DETECTED,
        band=band,
        threat_class=decision,
        rule_matched=False,
        matched_rules=[],
        rule_id=None,
        rule_explanation=None,
        rule_rationale=None,
        rule_approved_by=None,
        signal_features_count=len(combined_features.values),
        ioc_summary=_ioc_summary(ioc_result),
        hand_crafted_features=_handcrafted_dict(handcrafted),
        model_label=clf.label,
        decision=decision,
        explanation_fr=explanation,
        xai_top_contributors=contributor_dicts,
        explanation_machine=explanation_machine,
        evidence=gr.evidence,
        rag_context_used=gr.context_ids,
        context_match=llm_eval.context_match,
        blind_spot=band == DetectionBand.BLIND_SPOT,
        gap_severity=gap_severity,
        payload_hash=_payload_hash(req.content),
        audit_event_id=f"audit-{uuid4()}",
        pipeline_trace=trace,
    )
