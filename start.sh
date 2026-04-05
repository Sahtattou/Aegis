#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${ROOT_DIR}/.env"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "[ERROR] Missing .env file at ${ENV_FILE}"
  echo "Create it first (for example: cp .env.example .env) and fill required values."
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "[ERROR] Docker is not installed or not available in PATH."
  exit 1
fi

if docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD=(docker-compose)
else
  echo "[ERROR] Docker Compose is not available (need 'docker compose' or 'docker-compose')."
  exit 1
fi

echo "[INFO] Starting HARIS platform containers (build + detached)..."
"${COMPOSE_CMD[@]}" -f "${ROOT_DIR}/docker-compose.yml" up --build -d

echo
echo "[OK] HARIS platform is starting."
echo "Frontend: http://localhost:5173"
echo "Gateway:  http://localhost:8000"
echo ""
echo "To follow logs: ${COMPOSE_CMD[*]} -f ${ROOT_DIR}/docker-compose.yml logs -f"
echo "To stop stack:  ${COMPOSE_CMD[*]} -f ${ROOT_DIR}/docker-compose.yml down"
