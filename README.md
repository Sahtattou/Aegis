# HARIS Security Platform

Monorepo scaffold for a Neo4j-backed GraphRAG cybersecurity platform with:

- FastAPI backend (`api/`)
- React + Vite frontend (`frontend/`)
- Neo4j initialization scripts (`neo4j/init/`)

## Quick Start

1. Copy `.env.example` to `.env` and fill secrets.
2. Ensure APOC plugin jar is available under `neo4j/plugins/`.
3. Run:

```bash
docker compose up --build
```

## Repository Layout

See the directory structure under `api/`, `frontend/`, `neo4j/`, and `docs/`.
