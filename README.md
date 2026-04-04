# HARIS Security Platform

Monorepo scaffold for a Neo4j-backed GraphRAG cybersecurity platform with:

- FastAPI microservices (`api/`) split into:
  - gateway (`:8000`)
  - redteam (`:8001`)
  - blueteam (`:8002`)
  - blindspot (`:8003`)
  - audit (`:8004`)
- React + Vite frontend (`frontend/`)
- Neo4j initialization scripts (`neo4j/init/`)

## Quick Start

1. Copy `.env.example` to `.env` and fill secrets.
2. Ensure APOC plugin jar is available under `neo4j/plugins/`.
3. Run:

```bash
docker compose up --build
```

## Red Team Simulation (Kali)

The repository includes an optional Kali Linux simulation container configured with a `redteam` profile.

Start standard stack (no attacker container):

```bash
docker compose up --build
```

Start Kali simulation container when needed:

```bash
docker compose --profile redteam up -d kali-redteam
```

The Kali container is isolated on an internal network (`redteam_net`) and is intended for local simulation workflows only.

## Service Endpoints

- Gateway: `http://localhost:8000`
- Red Team: `http://localhost:8001`
- Blue Team: `http://localhost:8002`
- Blind Spot: `http://localhost:8003`
- Audit: `http://localhost:8004`

## Repository Layout

See the directory structure under `api/`, `frontend/`, `neo4j/`, and `docs/`.
