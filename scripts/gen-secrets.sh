#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SECRETS_DIR="${REPO_ROOT}/secrets"
FORCE=0
[[ "${1:-}" == "--force" ]] && FORCE=1

log()  { printf '\033[1;34m[secrets]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[secrets]\033[0m %s\n' "$*"; }
die()  { printf '\033[1;31m[secrets]\033[0m %s\n' "$*" >&2; exit 1; }

command -v openssl >/dev/null 2>&1 || die "openssl required"
command -v htpasswd >/dev/null 2>&1 || warn "htpasswd missing, using openssl passwd"

mkdir -p "${SECRETS_DIR}"

ADMIN_PW_FILE="${SECRETS_DIR}/admin_password.txt"
if [[ ! -f "${ADMIN_PW_FILE}" || ${FORCE} -eq 1 ]]; then
  log "generating admin password"
  openssl rand -base64 24 | tr -d '\n' > "${ADMIN_PW_FILE}"
  chmod 600 "${ADMIN_PW_FILE}"
else
  log "admin password exists"
fi
ADMIN_PW="$(cat "${ADMIN_PW_FILE}")"

if [[ ! -f "${SECRETS_DIR}/gateway.crt" || ${FORCE} -eq 1 ]]; then
  log "generating gateway TLS cert"
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout "${SECRETS_DIR}/gateway.key" \
    -out    "${SECRETS_DIR}/gateway.crt" \
    -subj "//C=ZA\\ST=Gauteng\\L=Johannesburg\\O=Ops\\CN=localhost" \
    >/dev/null 2>&1 || true
  [[ -f "${SECRETS_DIR}/gateway.crt" ]] || die "gateway.crt was not created"
  [[ -f "${SECRETS_DIR}/gateway.key" ]] || die "gateway.key was not created"
  chmod 600 "${SECRETS_DIR}/gateway.key"
else
  log "gateway cert exists"
fi

if [[ ! -f "${SECRETS_DIR}/ca.crt" || ${FORCE} -eq 1 ]]; then
  log "generating CA"
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout "${SECRETS_DIR}/ca.key" \
    -out    "${SECRETS_DIR}/ca.crt" \
    -subj "//C=ZA\\ST=Gauteng\\L=Johannesburg\\O=Ops\\CN=ClientCA" \
    >/dev/null 2>&1 || true
  [[ -f "${SECRETS_DIR}/ca.crt" ]] || die "ca.crt was not created"
  [[ -f "${SECRETS_DIR}/ca.key" ]] || die "ca.key was not created"
  chmod 600 "${SECRETS_DIR}/ca.key"

  log "generating client cert"
  openssl req -nodes -newkey rsa:2048 \
    -keyout "${SECRETS_DIR}/client.key" \
    -out    "${SECRETS_DIR}/client.csr" \
    -subj "//C=ZA\\ST=Gauteng\\L=Johannesburg\\O=Ops\\CN=admin-client" \
    >/dev/null 2>&1 || true
  [[ -f "${SECRETS_DIR}/client.csr" ]] || die "client.csr was not created"

  openssl x509 -req \
    -in "${SECRETS_DIR}/client.csr" \
    -CA "${SECRETS_DIR}/ca.crt" -CAkey "${SECRETS_DIR}/ca.key" \
    -CAcreateserial \
    -out "${SECRETS_DIR}/client.crt" -days 365 \
    >/dev/null 2>&1 || true
  [[ -f "${SECRETS_DIR}/client.crt" ]] || die "client.crt was not created"
  chmod 600 "${SECRETS_DIR}/client.key"
  rm -f "${SECRETS_DIR}/client.csr" "${SECRETS_DIR}/ca.srl"
else
  log "CA and client cert exist"
fi

if [[ ! -f "${SECRETS_DIR}/.htpasswd" || ${FORCE} -eq 1 ]]; then
  log "generating .htpasswd"
  if command -v htpasswd >/dev/null 2>&1; then
    htpasswd -bcB "${SECRETS_DIR}/.htpasswd" admin "${ADMIN_PW}"
  else
    printf 'admin:%s\n' "$(openssl passwd -apr1 "${ADMIN_PW}")" > "${SECRETS_DIR}/.htpasswd"
  fi
  chmod 600 "${SECRETS_DIR}/.htpasswd"
else
  log ".htpasswd exists"
fi

log "writing db.env"
cat > "${SECRETS_DIR}/db.env" <<EOF
DB_HOST=postgres
DB_PORT=5432
DB_NAME=ops_db
DB_USER=admin
DB_PASSWORD=${ADMIN_PW}
EOF
chmod 600 "${SECRETS_DIR}/db.env"

log "done — ${SECRETS_DIR}"
log "admin password: ${ADMIN_PW_FILE}"