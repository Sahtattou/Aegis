from datetime import UTC, datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

DecisionLabel = Literal["malicious", "suspicious", "benign"]
ThreatClassLabel = Literal["malicious", "suspicious", "benign"]
GapSeverity = Literal["LOW", "MEDIUM", "HIGH"]


class DetectionBand(str, Enum):
    DETECTED = "detected"
    UNCERTAIN = "uncertain"
    BLIND_SPOT = "blind_spot"


class EvaluateRequest(BaseModel):
    attack_id: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    source: str | None = None
    metadata: dict[str, str] = Field(default_factory=dict)


class EvaluateResponse(BaseModel):
    pipeline_version: str = "1.3.0"
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    attack_id: str

    ml_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    class_probability_map: dict[str, float] = Field(default_factory=dict)
    llm_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    llm_threat_class: ThreatClassLabel = "suspicious"
    llm_key_indicators: list[str] = Field(default_factory=list)
    llm_provenance: str = "llm_unset"
    fused_confidence: float = Field(ge=0.0, le=1.0)

    detected: bool
    band: DetectionBand
    threat_class: ThreatClassLabel

    rule_matched: bool
    matched_rules: list[str] = Field(default_factory=list)
    rule_id: str | None = None
    rule_explanation: str | None = None
    rule_rationale: str | None = None
    rule_approved_by: str | None = None

    signal_features_count: int = 0
    ioc_summary: dict[str, int] = Field(default_factory=dict)
    hand_crafted_features: dict[str, float] = Field(default_factory=dict)

    model_label: str | None = None
    decision: DecisionLabel

    explanation_fr: str
    xai_top_contributors: list[dict[str, float | str]] = Field(default_factory=list)
    explanation_machine: dict[str, str | float | list[str]] = Field(
        default_factory=dict
    )
    evidence: list[str] = Field(default_factory=list)
    rag_context_used: list[str] = Field(default_factory=list)
    context_match: str = ""

    blind_spot: bool
    gap_severity: GapSeverity

    payload_hash: str
    audit_event_id: str

    pipeline_trace: list[str] = Field(default_factory=list)


class ForensicTimelineEvent(BaseModel):
    event_id: str
    ts: str
    event_type: str
    detection: dict[str, str | float | bool]
    context_references: list[dict[str, str]] = Field(default_factory=list)
    audit_linkage: dict[str, str] = Field(default_factory=dict)


class ForensicTimelineResponse(BaseModel):
    schema_version: str = "forensic.timeline.v1"
    attack_id: str
    events: list[ForensicTimelineEvent] = Field(default_factory=list)
    total_events: int = 0
    data_completeness: str = "degraded"
