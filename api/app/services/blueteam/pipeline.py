from app.models.detection import DecisionLabel, EvaluateRequest, EvaluateResponse
from app.services.blueteam.classifier import classify
from app.services.blueteam.embeddings import embed
from app.services.blueteam.graphrag import retrieve_context
from app.services.blueteam.preprocessor import preprocess
from app.services.blueteam.rules_engine import apply_rules, load_rules
from app.services.blueteam.xai import explain_french


def _coerce_decision(value: str) -> DecisionLabel:
    if value == "malicious":
        return "malicious"
    if value == "benign":
        return "benign"
    return "suspicious"


def run_pipeline(req: EvaluateRequest) -> EvaluateResponse:
    trace: list[str] = []
    preprocessed = preprocess(req.content)
    trace.append("preprocess")
    rules = load_rules()
    trace.append("load_rules")
    rules_result = apply_rules(preprocessed.normalized_text, rules)
    trace.append("rules_engine")
    if rules_result.matched:
        explanation = explain_french(
            decision=rules_result.decision or "malicious",
            confidence=rules_result.confidence or 0.9,
            evidence=rules_result.evidence,
        )
        trace.append("xai")
        return EvaluateResponse(
            attack_id=req.attack_id,
            decision=_coerce_decision(rules_result.decision or "malicious"),
            confidence=rules_result.confidence or 0.9,
            matched_rules=rules_result.matched_rules,
            model_label=None,
            explanation_fr=explanation,
            evidence=rules_result.evidence,
            pipeline_trace=trace,
        )
    features = embed(preprocessed.normalized_text)
    trace.append("embeddings")
    clf = classify(features)
    trace.append("classifier")
    gr = retrieve_context(preprocessed.normalized_text)
    trace.append("graphrag")
    explanation = explain_french(
        decision=clf.label,
        confidence=clf.confidence,
        evidence=gr.evidence,
    )
    trace.append("xai")
    return EvaluateResponse(
        attack_id=req.attack_id,
        decision=_coerce_decision(clf.label),
        confidence=clf.confidence,
        matched_rules=[],
        model_label=clf.label,
        explanation_fr=explanation,
        evidence=gr.evidence,
        pipeline_trace=trace,
    )
