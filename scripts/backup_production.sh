#!/usr/bin/env bash

set -Eeuo pipefail

PROJECT_DIR="$(
  cd "$(dirname "${BASH_SOURCE[0]}")/.."
  pwd
)"

ENV_FILE="${PROJECT_DIR}/.env.production"
COMPOSE_FILE="${PROJECT_DIR}/compose.production.yml"
BACKUP_DIR="${PROJECT_DIR}/backups"

TIMESTAMP="$(
  date -u +"%Y%m%dT%H%M%SZ"
)"

MYSQL_BACKUP="${BACKUP_DIR}/mysql-${TIMESTAMP}.sql.gz"
UPLOADS_BACKUP="${BACKUP_DIR}/uploads-${TIMESTAMP}.tar.gz"
RESULTS_BACKUP="${BACKUP_DIR}/results-${TIMESTAMP}.tar.gz"

MYSQL_TEMP="${MYSQL_BACKUP}.tmp"
UPLOADS_TEMP="${UPLOADS_BACKUP}.tmp"
RESULTS_TEMP="${RESULTS_BACKUP}.tmp"

cleanup() {
  rm -f \
    "${MYSQL_TEMP}" \
    "${UPLOADS_TEMP}" \
    "${RESULTS_TEMP}"
}

trap cleanup EXIT

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Missing file: ${ENV_FILE}"
  exit 1
fi

if [[ ! -f "${COMPOSE_FILE}" ]]; then
  echo "Missing file: ${COMPOSE_FILE}"
  exit 1
fi

mkdir -p "${BACKUP_DIR}"

cd "${PROJECT_DIR}"

COMPOSE=(
  docker compose
  --env-file "${ENV_FILE}"
  --file "${COMPOSE_FILE}"
)

RUNNING_SERVICES="$(
  "${COMPOSE[@]}" ps \
    --status running \
    --services
)"

for service in mysql backend; do
  if ! grep -qx "${service}" <<< "${RUNNING_SERVICES}"; then
    echo "Production service is not running: ${service}"
    echo "Start the production stack first:"
    echo "./scripts/production_up.sh"
    exit 1
  fi
done

echo "Backing up MySQL..."

"${COMPOSE[@]}" \
  exec \
  --no-TTY \
  mysql \
  sh \
  -eu \
  -c '
    : "${MYSQL_USER:?MYSQL_USER is not set}"
    : "${MYSQL_PASSWORD:?MYSQL_PASSWORD is not set}"
    : "${MYSQL_DATABASE:?MYSQL_DATABASE is not set}"

    exec mysqldump \
      --single-transaction \
      --quick \
      --routines \
      --triggers \
      --user="$MYSQL_USER" \
      --password="$MYSQL_PASSWORD" \
      "$MYSQL_DATABASE"
  ' \
  | gzip -c \
  > "${MYSQL_TEMP}"

gzip -t "${MYSQL_TEMP}"
mv "${MYSQL_TEMP}" "${MYSQL_BACKUP}"

echo "Backing up uploaded files..."

"${COMPOSE[@]}" \
  exec \
  --no-TTY \
  backend \
  tar \
  -czf - \
  -C /data/uploads \
  . \
  > "${UPLOADS_TEMP}"

tar -tzf "${UPLOADS_TEMP}" > /dev/null
mv "${UPLOADS_TEMP}" "${UPLOADS_BACKUP}"

echo "Backing up result files..."

"${COMPOSE[@]}" \
  exec \
  --no-TTY \
  backend \
  tar \
  -czf - \
  -C /data/results \
  . \
  > "${RESULTS_TEMP}"

tar -tzf "${RESULTS_TEMP}" > /dev/null
mv "${RESULTS_TEMP}" "${RESULTS_BACKUP}"

echo
echo "Backup completed:"
echo "${BACKUP_DIR}"
echo
ls -lh \
  "${MYSQL_BACKUP}" \
  "${UPLOADS_BACKUP}" \
  "${RESULTS_BACKUP}"
