# HARIS Project Context

## Purpose

HARIS is designed as a cybersecurity platform for modeling and evaluating attack scenarios with transparent, auditable decision outputs.

The repository combines offensive simulation (Red Team) and defensive analysis (Blue Team) with a graph-backed persistence layer (Neo4j) and a frontend control surface.

## Problem Space

Traditional detection pipelines often suffer from one or more of:

- poor explainability,
- weak forensic traceability,
- brittle context usage,
- and unclear confidence calibration across heterogeneous detectors.

HARIS addresses this by combining rule-based checks, model inference, contextual retrieval, and audit/event persistence.

## System Intent

The platform is intended to:

1. Generate representative attack scenarios.
2. Evaluate payloads using a hybrid detection strategy.
3. Persist decisions and provenance into a graph model.
4. Expose forensic timelines for investigation.
5. Provide operator-friendly API and UI interfaces.

## Core Concepts

### Red Team

Produces structured synthetic attack artifacts that can be used to stress defensive controls.

### Blue Team

Processes payloads through a multi-stage evaluation pipeline and returns:

- model and LLM confidence,
- fused confidence,
- detection band,
- threat decision,
- explanation artifacts,
- audit linkage metadata.

### Blind Spot

Surfaces potential gaps where current detection confidence is weak or uncertain.

### Audit

Provides timeline-style operational visibility over recorded events and decisions.

### Graph Backbone (Neo4j)

Stores attacks, detections, contexts, and audit nodes to support retrieval and forensic traversals.

## Design Priorities

1. **Traceability** — Every important decision should be reconstructible.
2. **Resilience** — Fallback behaviors for unavailable external dependencies.
3. **Composability** — Service boundaries with a shared contract layer.
4. **Local-first operation** — Docker-based startup and explicit environment config.
5. **Explainability** — Analysts should get both machine and human-readable rationale.

## Scope Boundaries

### In Scope

- Local stack orchestration via Docker Compose
- Multi-service API architecture
- Graph persistence and vector-style retrieval pathways
- Frontend interaction through gateway API routes

### Out of Scope (in current repo state)

- Production cloud deployment templates
- Built-in CI workflow definitions
- External enterprise observability integrations

## User Personas

- **Security Analyst:** Reviews evaluation decisions and forensic timelines.
- **Red Team Operator:** Generates and iterates simulation payloads.
- **Platform Engineer:** Operates services, configures environments, and maintains model/data assets.
- **Developer/Researcher:** Extends detection logic, models, rules, and retrieval strategy.

## Expected Outcomes

When used as intended, HARIS should enable:

- repeatable scenario generation,
- explainable defensive assessments,
- structured event retention,
- and faster investigation workflows through graph-linked forensic context.

## Related Documentation

- `README.md` — quick start and service endpoints
- `docs/architecture.md` — runtime and logical architecture
- `docs/transparency_note.md` — transparency/XAI orientation
- `docs/PROJECT_DOCUMENTATION.md` — full technical reference
