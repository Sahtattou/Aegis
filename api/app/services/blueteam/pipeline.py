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
from .feature_builder import (
    build_handcrafted_features,
    combine_feature_vector,
)
from app.services.blueteam.graphrag import retrieve_context
from .ioc_extractor import extract_iocs
from app.services.blueteam.preprocessor import preprocess
from app.services.blueteam.rules_engine import apply_rules, load_rules
from app.services.blueteam.xai import explain_french


def _coerce_decision(value: str) -> DecisionLabel:
    if value == "malicious":
        return "malicious"
    if value == "benign":
        return "benign"
    return "suspicious"


def _fuse_confidence(ml_confidence: float, llm_confidence: float) -> float:
    fused = (0.6 * ml_confidence) + (0.4 * llm_confidence)
    return max(0.0, min(1.0, fused))


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


def run_pipeline(req: EvaluateRequest) -> EvaluateResponse:
    trace: list[str] = []

    preprocessed = preprocess(req.content)
    trace.append("preprocess")

    ioc_result = extract_iocs(preprocessed.normalized_text)
    trace.append("ioc_extraction")

    handcrafted = build_handcrafted_features(preprocessed.normalized_text, ioc_result)
    trace.append("feature_builder")

    rules = load_rules()
    trace.append("load_rules")
    rules_result = apply_rules(preprocessed.normalized_text, rules)
    trace.append("rules_engine")

    if rules_result.matched:
        ml_confidence = rules_result.confidence or 0.90
        llm_confidence = 0.0
        fused_confidence = _fuse_confidence(ml_confidence, llm_confidence)
        band = _resolve_band(fused_confidence)
        gap_severity = _resolve_gap_severity(band)
        decision = _coerce_decision(rules_result.decision or "malicious")

        explanation = explain_french(
            decision=decision,
            confidence=fused_confidence,
            evidence=rules_result.evidence,
        )
        trace.append("xai")

        return EvaluateResponse(
            attack_id=req.attack_id,
            ml_confidence=ml_confidence,
            llm_confidence=llm_confidence,
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
            signal_features_count=len(handcrafted.values),
            ioc_summary=_ioc_summary(ioc_result),
            hand_crafted_features=_handcrafted_dict(handcrafted),
            model_label=None,
            decision=decision,
            explanation_fr=explanation,
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
    combined_features = combine_feature_vector(embedding, handcrafted)
    trace.append("feature_vector_assembly")

    clf = classify(combined_features.values)
    trace.append("classifier")

    gr = retrieve_context(preprocessed.normalized_text)
    trace.append("graphrag")

    ml_confidence = clf.confidence
    llm_confidence = 0.0
    fused_confidence = _fuse_confidence(ml_confidence, llm_confidence)
    band = _resolve_band(fused_confidence)
    gap_severity = _resolve_gap_severity(band)
    decision = _coerce_decision(clf.label)

    explanation = explain_french(
        decision=decision,
        confidence=fused_confidence,
        evidence=gr.evidence,
    )
    trace.append("xai")

    return EvaluateResponse(
        attack_id=req.attack_id,
        ml_confidence=ml_confidence,
        llm_confidence=llm_confidence,
        fused_confidence=fused_confidence,
        detected=band == DetectionBand.DETECTED,
        band=band,
        threat_class=decision,
        rule_matched=False,
        matched_rules=[],
        rule_id=None,
        rule_explanation=None,
        signal_features_count=len(combined_features.values),
        ioc_summary=_ioc_summary(ioc_result),
        hand_crafted_features=_handcrafted_dict(handcrafted),
        model_label=clf.label,
        decision=decision,
        explanation_fr=explanation,
        evidence=gr.evidence,
        rag_context_used=[
            "static:incident-A102",
            "static:campaign-credential-harvesting",
        ],
        context_match="Static context evidence (GraphRAG stub)",
        blind_spot=band == DetectionBand.BLIND_SPOT,
        gap_severity=gap_severity,
        payload_hash=_payload_hash(req.content),
        audit_event_id=f"audit-{uuid4()}",
        pipeline_trace=trace,
    )
