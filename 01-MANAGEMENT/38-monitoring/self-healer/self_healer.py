#!/usr/bin/env bash
#
# gen-secrets.sh — generates every secret the local stack needs.
#
# Idempotent by default: re-running is a no-op if the files already
# exist. Pass --force to rotate everything (used before demos so
# nobody sees stale credentials in a screen share).
#
# All output goes to secrets/, which is gitignored. See
# secrets.example/README.md for what each file is and who uses it.
#
# Reference: openssl req(1), openssl x509(1), htpasswd(1), and the
# ngx_http_ssl_module / ngx_http_auth_basic_module docs.

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

# ---------------------------------------------------------------------
# Admin password
#
# One password file is the single source of truth for everything that
# authenticates as "admin": the Basic Auth hash below, and the
# Postgres password written into db.env. Reading it once here means
# a re-run cannot desync the two.
# ---------------------------------------------------------------------
ADMIN_PW_FILE="${SECRETS_DIR}/admin_password.txt"
if [[ ! -f "${ADMIN_PW_FILE}" || ${FORCE} -eq 1 ]]; then
  log "generating admin password"
  openssl rand -base64 24 | tr -d '\n' > "${ADMIN_PW_FILE}"
  chmod 600 "${ADMIN_PW_FILE}"
else
  log "admin password exists"
fi
ADMIN_PW="$(cat "${ADMIN_PW_FILE}")"

# ---------------------------------------------------------------------
# Gateway TLS certificate
#
# This is the cert NGINX presents to clients on :8443. CN=localhost
# because the lab is only reachable on localhost. The cert is
# self-signed — a real deployment would chain to an internal CA.
# ---------------------------------------------------------------------
#
# MSYS_NO_PATHCONV=1 disables Git Bash's automatic path rewriting.
# Without it, the /C=ZA/... in -subj gets mangled into
# C:/Program Files/Git/C=ZA/..., which produces a broken subject.
# The doubled leading slash in -subj is a related workaround.
if [[ ! -f "${SECRETS_DIR}/gateway.crt" || ${FORCE} -eq 1 ]]; then
  log "generating gateway TLS cert"
  MSYS_NO_PATHCONV=1 openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout "${SECRETS_DIR}/gateway.key" \
    -out    "${SECRETS_DIR}/gateway.crt" \
    -subj "//C=ZA\\ST=Gauteng\\L=Johannesburg\\O=Ops\\CN=localhost" \
    >/dev/null 2>&1
  chmod 600 "${SECRETS_DIR}/gateway.key"
else
  log "gateway cert exists"
fi

# ---------------------------------------------------------------------
# Demo CA and one client certificate
#
# NGINX verifies mTLS clients against ca.crt. The client cert is
# signed by the same CA so curl --cert works out of the box.
# This CA is local-only — its private key is in secrets/ca.key and
# must never leave this machine.
# ---------------------------------------------------------------------
if [[ ! -f "${SECRETS_DIR}/ca.crt" || ${FORCE} -eq 1 ]]; then
  log "generating CA"
  MSYS_NO_PATHCONV=1 openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout "${SECRETS_DIR}/ca.key" \
    -out    "${SECRETS_DIR}/ca.crt" \
    -subj "//C=ZA\\ST=Gauteng\\L=Johannesburg\\O=Ops\\CN=ClientCA" \
    >/dev/null 2>&1
  chmod 600 "${SECRETS_DIR}/ca.key"

  log "generating client cert"
  MSYS_NO_PATHCONV=1 openssl req -nodes -newkey rsa:2048 \
    -keyout "${SECRETS_DIR}/client.key" \
    -out    "${SECRETS_DIR}/client.csr" \
    -subj "//C=ZA\\ST=Gauteng\\L=Johannesburg\\O=Ops\\CN=admin-client" \
    >/dev/null 2>&1
  MSYS_NO_PATHCONV=1 openssl x509 -req \
    -in "${SECRETS_DIR}/client.csr" \
    -CA "${SECRETS_DIR}/ca.crt" -CAkey "${SECRETS_DIR}/ca.key" \
    -CAcreateserial \
    -out "${SECRETS_DIR}/client.crt" -days 365 \
    >/dev/null 2>&1
  chmod 600 "${SECRETS_DIR}/client.key"
  rm -f "${SECRETS_DIR}/client.csr" "${SECRETS_DIR}/ca.srl"
#!/usr/bin/env bash
#
# gen-secrets.sh — generates every secret the local stack needs.
#
# Idempotent by default: re-running is a no-op if the files already
# exist. Pass --force to rotate everything (used before demos so
# nobody sees stale credentials in a screen share).
#
# All output goes to secrets/, which is gitignored. See
# secrets.example/README.md for what each file is and who uses it.
#
# Reference: openssl req(1), openssl x509(1), htpasswd(1), and the
# ngx_http_ssl_module / ngx_http_auth_basic_module docs.

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

# ---------------------------------------------------------------------
# Admin password
#
# One password file is the single source of truth for everything that
# authenticates as "admin": the Basic Auth hash below, and the
# Postgres password written into db.env. Reading it once here means
# a re-run cannot desync the two.
# ---------------------------------------------------------------------
ADMIN_PW_FILE="${SECRETS_DIR}/admin_password.txt"
if [[ ! -f "${ADMIN_PW_FILE}" || ${FORCE} -eq 1 ]]; then
  log "generating admin password"
  openssl rand -base64 24 | tr -d '\n' > "${ADMIN_PW_FILE}"
  chmod 600 "${ADMIN_PW_FILE}"
else
  log "admin password exists"
fi
ADMIN_PW="$(cat "${ADMIN_PW_FILE}")"

# ---------------------------------------------------------------------
# Gateway TLS certificate
#
# This is the cert NGINX presents to clients on :8443. CN=localhost
# because the lab is only reachable on localhost. The cert is
# self-signed — a real deployment would chain to an internal CA.
# ---------------------------------------------------------------------
#
# MSYS_NO_PATHCONV=1 disables Git Bash's automatic path rewriting.
# Without it, the /C=ZA/... in -subj gets mangled into
# C:/Program Files/Git/C=ZA/..., which produces a broken subject.
# The doubled leading slash in -subj is a related workaround.
if [[ ! -f "${SECRETS_DIR}/gateway.crt" || ${FORCE} -eq 1 ]]; then
  log "generating gateway TLS cert"
  MSYS_NO_PATHCONV=1 openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout "${SECRETS_DIR}/gateway.key" \
    -out    "${SECRETS_DIR}/gateway.crt" \
    -subj "//C=ZA\\ST=Gauteng\\L=Johannesburg\\O=Ops\\CN=localhost" \
    >/dev/null 2>&1
  chmod 600 "${SECRETS_DIR}/gateway.key"
else
  log "gateway cert exists"
fi

# ---------------------------------------------------------------------
# Demo CA and one client certificate
#
# NGINX verifies mTLS clients against ca.crt. The client cert is
# signed by the same CA so curl --cert works out of the box.
# This CA is local-only — its private key is in secrets/ca.key and
# must never leave this machine.
# ---------------------------------------------------------------------
if [[ ! -f "${SECRETS_DIR}/ca.crt" || ${FORCE} -eq 1 ]]; then
  log "generating CA"
  MSYS_NO_PATHCONV=1 openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout "${SECRETS_DIR}/ca.key" \
    -out    "${SECRETS_DIR}/ca.crt" \
    -subj "//C=ZA\\ST=Gauteng\\L=Johannesburg\\O=Ops\\CN=ClientCA" \
    >/dev/null 2>&1
  chmod 600 "${SECRETS_DIR}/ca.key"

  log "generating client cert"
  MSYS_NO_PATHCONV=1 openssl req -nodes -newkey rsa:2048 \
    -keyout "${SECRETS_DIR}/client.key" \
    -out    "${SECRETS_DIR}/client.csr" \
    -subj "//C=ZA\\ST=Gauteng\\L=Johannesburg\\O=Ops\\CN=admin-client" \
    >/dev/null 2>&1
  MSYS_NO_PATHCONV=1 openssl x509 -req \
    -in "${SECRETS_DIR}/client.csr" \
    -CA "${SECRETS_DIR}/ca.crt" -CAkey "${SECRETS_DIR}/ca.key" \
    -CAcreateserial \
    -out "${SECRETS_DIR}/client.crt" -days 365 \
    >/dev/null 2>&1
  chmod 600 "${SECRETS_DIR}/client.key"
  rm -f "${SECRETS_DIR}/client.csr" "${SECRETS_DIR}/ca.srl"
