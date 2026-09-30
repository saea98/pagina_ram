#!/usr/bin/env bash
# Restaura base y media de una fecha (YYYY-MM-DD) y vuelve a levantar el stack.
set -euo pipefail

cd "$(dirname "$0")/.."

date_stamp="${1:-}"
if ! [[ "$date_stamp" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
  echo "Uso: restore.sh <fecha YYYY-MM-DD>" >&2
  exit 1
fi

if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

compose() {
  local -a files=(-f docker-compose.yml -f docker-compose.prod.yml)
  if [ "${CHERRY_DEDICATED:-0}" != "1" ]; then
    files+=(-f docker-compose.server.yml)
  fi
  docker compose "${files[@]}" "$@"
}

volume_name() {
  docker volume ls -q \
    --filter "label=com.docker.compose.project=cherry" \
    --filter "label=com.docker.compose.volume=$1"
}

echo "Comprobando respaldo ${date_stamp}."
compose run --rm --no-deps --entrypoint sh backup -c \
  "test -f '/backups/db-${date_stamp}.dump' && test -f '/backups/media-${date_stamp}.tgz'"

echo "Deteniendo web, api y worker."
compose stop web api worker

echo "Restaurando la base."
compose run --rm --no-deps --entrypoint sh backup -c \
  "pg_restore -h db --clean --if-exists --no-owner -U \"\$POSTGRES_USER\" -d \"\$POSTGRES_DB\" '/backups/db-${date_stamp}.dump'"

echo "Restaurando los medios."
media_vol="$(volume_name media)"
backups_vol="$(volume_name backups)"
if [ -z "$media_vol" ] || [ -z "$backups_vol" ]; then
  echo "No encontré los volúmenes media o backups del proyecto cherry." >&2
  exit 1
fi
docker run --rm \
  -v "${backups_vol}:/backups:ro" \
  -v "${media_vol}:/srv/media" \
  postgres:17.11-alpine \
  tar -xzf "/backups/media-${date_stamp}.tgz" -C /srv/media

echo "Levantando los servicios."
compose up -d
echo "Restauración lista: ${date_stamp}."
