#!/usr/bin/env bash

set -euo pipefail

PROJECT_DIR="$(
  cd "$(dirname "${BASH_SOURCE[0]}")/.."
  pwd
)"

ENV_FILE="${PROJECT_DIR}/.env.production"
COMPOSE_FILE="${PROJECT_DIR}/compose.production.yml"
MODEL_FILE="${PROJECT_DIR}/models/yolo26n.pt"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Missing .env.production"
  echo "Copy .env.production.example and configure it first."
  exit 1
fi

if [[ ! -f "${MODEL_FILE}" ]]; then
  echo "Missing models/yolo26n.pt"
  echo "Download or copy the model file before starting."
  exit 1
fi

cd "${PROJECT_DIR}"

docker compose \
  --env-file "${ENV_FILE}" \
  --file "${COMPOSE_FILE}" \
  config \
  --quiet

docker compose \
  --env-file "${ENV_FILE}" \
  --file "${COMPOSE_FILE}" \
  build \
  --pull

docker compose \
  --env-file "${ENV_FILE}" \
  --file "${COMPOSE_FILE}" \
  up \
  --detach

docker compose \
  --env-file "${ENV_FILE}" \
  --file "${COMPOSE_FILE}" \
  ps