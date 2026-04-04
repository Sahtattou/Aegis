#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="${SCRIPT_DIR}/frontend"

if [[ ! -d "${FRONTEND_DIR}" ]]; then
  echo "Frontend directory not found at ${FRONTEND_DIR}" >&2
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is required but was not found in PATH." >&2
  exit 1
fi

cd "${FRONTEND_DIR}"

if [[ ! -d node_modules ]]; then
  echo "Installing frontend dependencies..."
  npm install
fi

echo "Starting frontend dev server on http://localhost:5173"
exec npm run dev -- --host 0.0.0.0 --port 5173
