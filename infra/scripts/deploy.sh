#!/usr/bin/env bash
# Despliega un tag de GHCR y vuelve al anterior si los healthchecks fallan.
set -euo pipefail

cd "$(dirname "$0")/.."

if [ $# -ne 1 ]; then
  echo "Uso: deploy.sh <sha-xxxxxxx|latest>|rollback" >&2
  exit 1
fi

requested="$1"

compose() {
  local -a files=(-f docker-compose.yml -f docker-compose.prod.yml)
  if [ "${CHERRY_DEDICATED:-0}" != "1" ]; then
    files+=(-f docker-compose.server.yml)
  fi
  docker compose "${files[@]}" "$@"
}

wait_healthy() {
  local deadline=$((SECONDS + 120))
  local svc status pending
  while [ "$SECONDS" -lt "$deadline" ]; do
    pending=0
    for svc in web api db worker; do
      status="$(
        compose ps --format '{{.Service}} {{.Health}}' |
          awk -v name="$svc" '$1 == name { print $2; exit }'
      )"
      if [ "$status" != "healthy" ]; then
        pending=1
      fi
    done
    if [ "$pending" -eq 0 ]; then
      return 0
    fi
    sleep 3
  done
  return 1
}

if [ "$requested" = "rollback" ]; then
  if [ ! -s .last_tag ]; then
    echo "No hay un tag anterior en infra/.last_tag." >&2
    exit 1
  fi
  tag="$(tr -d '[:space:]' < .last_tag)"
  echo "Volviendo a la imagen ${tag}."
else
  tag="$requested"
  if [ -f .current_tag ]; then
    cp .current_tag .last_tag
  fi
fi

if ! [[ "$tag" =~ ^(sha-[0-9a-f]{7,40}|latest)$ ]]; then
  echo "Tag inválido: ${tag}. Usa sha-<commit> o latest." >&2
  exit 1
fi

printf '%s\n' "$tag" > .current_tag
export IMAGE_TAG="$tag"

if [ -n "${GHCR_USER:-}" ] && [ -n "${GHCR_TOKEN:-}" ]; then
  echo "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_USER" --password-stdin >/dev/null
fi

echo "Descargando ${tag} y aplicando migraciones."
compose pull web api worker
compose run --rm --no-deps api alembic upgrade head
compose up -d --remove-orphans

if ! wait_healthy; then
  echo "Los healthchecks no pasaron en 120 s." >&2
  if [ "${ROLLBACK:-0}" = "1" ] || [ "$requested" = "rollback" ]; then
    echo "El rollback también falló. Revisa docker compose ps." >&2
    exit 1
  fi
  export ROLLBACK=1
  exec "$0" rollback
fi

echo "Despliegue listo: ${tag}."
