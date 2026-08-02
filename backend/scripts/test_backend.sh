#!/usr/bin/env bash

set -Eeuo pipefail

BACKEND_DIR="$(
  cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
  pwd
)"

PROJECT_DIR="$(
  cd -- "${BACKEND_DIR}/.."
  pwd
)"

COMPOSE_FILE="${PROJECT_DIR}/docker-compose.test.yml"

export APP_ENV="test"
export LOG_LEVEL="WARNING"
export SQL_ECHO="false"

export DB_HOST="127.0.0.1"
export DB_PORT="3307"
export DB_NAME="traffic_detection_test"
export DB_USER="traffic_test"
export DB_PASSWORD="traffic_test_password"

export CELERY_BROKER_URL="redis://127.0.0.1:6380/0"
export CELERY_RESULT_BACKEND="redis://127.0.0.1:6380/1"

export MODEL_NAME="fake-yolo.pt"
export INFERENCE_DEVICE="cpu"

export UPLOAD_DIR="${BACKEND_DIR}/.test-data/uploads"
export RESULT_DIR="${BACKEND_DIR}/.test-data/results"
export VIDEO_UPLOAD_DIR="${BACKEND_DIR}/.test-data/uploads/videos"
export VIDEO_RESULT_DIR="${BACKEND_DIR}/.test-data/results/videos"

export CORS_ORIGINS='["http://127.0.0.1:5173","http://localhost:5173"]'
export ALLOWED_HOSTS='["127.0.0.1","localhost","testserver"]'

if [[ ! -f "${COMPOSE_FILE}" ]]; then
  echo "Test Docker Compose file was not found:"
  echo "${COMPOSE_FILE}"
  exit 1
fi

cleanup() {
  local exit_code=$?

  echo
  echo "Stopping test services..."

  docker compose \
    -f "${COMPOSE_FILE}" \
    down \
    --volumes \
    --remove-orphans \
    || true

  exit "${exit_code}"
}

trap cleanup EXIT

docker compose \
  -f "${COMPOSE_FILE}" \
  up \
  -d \
  --wait

cd "${BACKEND_DIR}"

alembic upgrade head

pytest \
  --cov=app \
  --cov-report=term-missing \
  --cov-report=xml