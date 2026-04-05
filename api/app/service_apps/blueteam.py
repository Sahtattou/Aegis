from fastapi import FastAPI

from app.db.repository import Repository
from app.models.detection import EvaluateRequest, EvaluateResponse
from app.services.blueteam.pipeline import run_pipeline

app = FastAPI(title="HARIS Blue Team Service")
repository = Repository()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "blueteam"}


@app.post("/evaluate", response_model=EvaluateResponse)
def evaluate(payload: EvaluateRequest) -> EvaluateResponse:
    response = run_pipeline(payload)
    repository.create_blue_evaluation(
        detection_id=f"det-{response.audit_event_id}",
        attack_id=response.attack_id,
        content=payload.content,
        source=payload.source,
        pipeline_version=response.pipeline_version,
        ml_confidence=response.ml_confidence,
        llm_confidence=response.llm_confidence,
        fused_confidence=response.fused_confidence,
        decision=response.decision,
        threat_class=response.threat_class,
        detected=response.detected,
        band=response.band.value,
        blind_spot=response.blind_spot,
        gap_severity=response.gap_severity,
        payload_hash=response.payload_hash,
        context_ids=response.rag_context_used,
        audit_event_id=response.audit_event_id,
    )
    return response


@app.get("/forensics/{attack_id}")
def forensic_timeline(attack_id: str) -> dict:
    timeline = repository.get_attack_forensic_timeline(attack_id)
    return {
        "schema_version": "forensic.timeline.v1",
        **timeline,
    }
