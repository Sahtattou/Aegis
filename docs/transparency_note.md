# Transparency Note

This note documents how HARIS supports transparency, explainability, and operator review.

## 1) Transparency Objectives

HARIS aims to make security decisions:

- interpretable,
- attributable,
- and reviewable after the fact.

This is implemented through structured outputs, pipeline traces, and audit-linked persistence.

## 2) Explainability in Blue Team Outputs

Blue Team evaluation responses include multiple transparency signals:

- `ml_confidence`
- `llm_confidence`
- `fused_confidence`
- `decision` and `band`
- `xai_top_contributors`
- `explanation_fr`
- `explanation_machine`
- `pipeline_trace`
- `audit_event_id`
- `payload_hash`

These fields are generated in the Blue Team pipeline and service layers.

Primary files:

- `api/app/services/blueteam/pipeline.py`
- `api/app/service_apps/blueteam.py`
- `api/app/models/detection.py`

## 3) Auditability and Forensics

HARIS persists evaluation context to Neo4j so that decision history can be reconstructed.

- Blue Team evaluations are stored with audit linkage metadata.
- Audit service exposes timeline retrieval (`GET /timeline`).
- Blue Team forensic endpoint exposes timeline per attack (`GET /forensics/{attack_id}`).

Primary files:

- `api/app/db/repository.py`
- `api/app/service_apps/audit.py`
- `api/app/service_apps/blueteam.py`

## 4) Human-in-the-Loop Position

HARIS is built to assist analysts, not replace analyst judgment.

Recommended usage model:

1. Use machine output to prioritize triage.
2. Review explanation and contributors.
3. Cross-check forensic timeline and context references.
4. Apply analyst policy and domain judgment before final action.

## 5) Confidence and Decision Interpretation

- **`fused_confidence`** combines ML and LLM signal strength.
- **Detection band** indicates certainty tier:
  - detected,
  - uncertain,
  - blind spot.
- **Blind spot** markers should trigger additional analyst review and control-gap investigation.

## 6) Provenance and Reproducibility Signals

HARIS emits and stores metadata supporting reproducibility:

- pipeline version
- payload hash
- rule match information (when applicable)
- context identifiers from retrieval
- audit event identifiers

Together, these provide an evidence chain from input payload to decision output.

## 7) Current Limitations and Practical Considerations

- Confidence values are model-derived and should be interpreted as decision support, not certainty.
- Fallback logic exists for unavailable external dependencies; this improves continuity but may reduce semantic depth.
- Analysts should treat low-confidence and blind-spot outputs as escalation candidates.

## 8) Operational Guidance

To maintain transparency quality over time:

1. Keep model artifacts versioned and documented.
2. Preserve Neo4j constraints and seed/index initialization consistency.
3. Monitor drift between synthetic red-team payload characteristics and real-world attack patterns.
4. Review and update rule sets and explanation quality periodically.
