#!/bin/sh
# Respaldo diario: pg_dump custom + tar de media. Retención 14 días.
set -eu

: "${POSTGRES_USER:?Falta POSTGRES_USER}"
: "${POSTGRES_DB:?Falta POSTGRES_DB}"
: "${POSTGRES_PASSWORD:?Falta POSTGRES_PASSWORD}"

export PGPASSWORD="$POSTGRES_PASSWORD"
host="${PGHOST:-db}"
backup_dir="${BACKUP_DIR:-/backups}"
media_dir="${MEDIA_DIR:-/srv/media}"
stamp="$(date +%F)"

mkdir -p "$backup_dir"

pg_dump -h "$host" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc -f "$backup_dir/db-$stamp.dump"
tar -czf "$backup_dir/media-$stamp.tgz" -C "$media_dir" .

find "$backup_dir" -type f \( -name 'db-*.dump' -o -name 'media-*.tgz' \) -mtime +14 -delete

if [ -n "${OFFSITE_RESTIC_REPOSITORY:-}" ]; then
  if command -v restic >/dev/null 2>&1; then
    RESTIC_REPOSITORY="$OFFSITE_RESTIC_REPOSITORY"
    RESTIC_PASSWORD="${OFFSITE_RESTIC_PASSWORD:-}"
    export RESTIC_REPOSITORY RESTIC_PASSWORD
    restic backup "$backup_dir"
  else
    echo "Hay repositorio offsite, pero restic no está instalado. El respaldo local sí quedó."
  fi
fi

echo "Respaldo listo: $stamp"
