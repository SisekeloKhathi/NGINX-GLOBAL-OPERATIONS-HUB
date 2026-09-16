#!/usr/bin/env bash
#
# refactor-secrets.sh — one-shot migration of secrets out of git.
#
# Moves cert/key/htpasswd material from 37-public-data-gateway/ into
# a top-level secrets/ directory, generates anything missing, stops
# git from tracking secrets, repoints NGINX and Terraform, recreates
# the NGINX container, and verifies the whole chain.
#
# Safe to re-run: every step is idempotent. Does NOT commit or push —
# review the diff with `git status` and commit yourself.
#
# Run from anywhere; the script computes its own repo root.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CERTS_DIR="${REPO_ROOT}/01-MANAGEMENT/37-public-data-gateway/certs"
NGINX_DIR="${REPO_ROOT}/01-MANAGEMENT/37-public-data-gateway/nginx"
SECRETS_DIR="${REPO_ROOT}/secrets"
TF_DIR="${REPO_ROOT}/01-MANAGEMENT/40-automation/terraform"
STAMP="$(date +%Y%m%d_%H%M%S)"

log()  { printf '\033[1;34m[refactor]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[refactor]\033[0m %s\n' "$*"; }
fail() { printf '\033[1;31m[refactor]\033[0m %s\n' "$*" >&2; exit 1; }
step() { printf '\n\033[1;36m== %s ==\033[0m\n' "$*"; }

[[ -d "${REPO_ROOT}/.git" ]] || fail "not a git repo: ${REPO_ROOT}"
[[ -f "${NGINX_DIR}/nginx.conf" ]] || fail "nginx.conf not found at ${NGINX_DIR}"

# ---------------------------------------------------------------------
# Backups
#
# Timestamped so a failed run never destroys the previous backup.
# gitignored via the *.backup* rule already in .gitignore.
# ---------------------------------------------------------------------
step "backups"
cp "${NGINX_DIR}/nginx.conf" "${NGINX_DIR}/nginx.conf.backup-${STAMP}"
cp "${TF_DIR}/main.tf"       "${TF_DIR}/main.tf.backup-${STAMP}"
log "backed up nginx.conf and main.tf with suffix .backup-${STAMP}"

# ---------------------------------------------------------------------
# Move existing secrets into secrets/
#
# The running NGINX still mounts the old paths, so this must happen
# before the container is recreated. Existing files are never
# overwritten — a file already in secrets/ wins.
# ---------------------------------------------------------------------
step "moving existing secrets into secrets/"
mkdir -p "${SECRETS_DIR}"

for f in gateway.crt gateway.key ca.crt ca.key client.crt client.key; do
  if [[ -f "${CERTS_DIR}/${f}" && ! -f "${SECRETS_DIR}/${f}" ]]; then
    mv "${CERTS_DIR}/${f}" "${SECRETS_DIR}/${f}"
    log "moved ${f}"
  fi
done

if [[ -f "${NGINX_DIR}/.htpasswd" && ! -f "${SECRETS_DIR}/.htpasswd" ]]; then
  mv "${NGINX_DIR}/.htpasswd" "${SECRETS_DIR}/.htpasswd"
  log "moved .htpasswd"
fi

# Intermediates that should never persist
rm -f "${CERTS_DIR}/ca.srl" "${CERTS_DIR}/client.csr" "${CERTS_DIR}/client.p12"

# ---------------------------------------------------------------------
# Generate anything missing
#
# gen-secrets.sh is idempotent, so this fills in only what's absent.
# The gateway cert is left alone if it exists — rotating it would
# break the running NGINX until the container is recreated.
# ---------------------------------------------------------------------
step "generating any missing secrets"
bash "${REPO_ROOT}/scripts/gen-secrets.sh" || fail "gen-secrets.sh failed"

for f in gateway.crt gateway.key ca.crt ca.key client.crt client.key .htpasswd admin_password.txt; do
  [[ -f "${SECRETS_DIR}/${f}" ]] || fail "missing secret after generation: ${f}"
done
log "all expected secret files present"

# ---------------------------------------------------------------------
# Untrack secrets from git
#
# --cached leaves files on disk and only removes them from the index.
# Ignore failures for files that are already untracked.
# ---------------------------------------------------------------------
step "untracking secrets from git"
(
  cd "${REPO_ROOT}"
  git rm --cached -q \
    01-MANAGEMENT/37-public-data-gateway/certs/gateway.key 2>/dev/null || true
  git rm --cached -q \
    01-MANAGEMENT/37-public-data-gateway/certs/gateway.crt 2>/dev/null || true
  git rm --cached -q \
    01-MANAGEMENT/37-public-data-gateway/certs/ca.crt 2>/dev/null || true
  git rm --cached -q \
    01-MANAGEMENT/37-public-data-gateway/certs/client.crt 2>/dev/null || true
  git rm --cached -q \
    01-MANAGEMENT/37-public-data-gateway/nginx/.htpasswd 2>/dev/null || true
)
log "git index updated"

# ---------------------------------------------------------------------
# Repoint nginx.conf
#
# sed is idempotent: a file already using /etc/nginx/secrets/ is
# unchanged. grep verifies the swap actually happened.
# ---------------------------------------------------------------------
step "repointing nginx.conf"
sed -i 's|/etc/nginx/certs/|/etc/nginx/secrets/|g' "${NGINX_DIR}/nginx.conf"

remaining="$(grep -c '/etc/nginx/certs/' "${NGINX_DIR}/nginx.conf" || true)"
[[ "${remaining}" == "0" ]] || fail "nginx.conf still has ${remaining} /etc/nginx/certs/ references"

rewritten="$(grep -c '/etc/nginx/secrets/' "${NGINX_DIR}/nginx.conf" || true)"
[[ "${rewritten}" -ge 1 ]] || fail "nginx.conf has no /etc/nginx/secrets/ references"
log "nginx.conf: 0 old paths, ${rewritten} new paths"

# ---------------------------------------------------------------------
# Repoint Terraform mounts
#
# Only the two mounts that point at certs/ and .htpasswd change. The
# nginx.conf mount and the screens mount are untouched.
# ---------------------------------------------------------------------
step "repointing Terraform mounts"

sed -i \
  's|source    = abspath("../../37-public-data-gateway/nginx/.htpasswd")|source    = abspath("../../../secrets/.htpasswd")|' \
  "${TF_DIR}/main.tf"

sed -i \
  's|source    = abspath("../../37-public-data-gateway/certs")|source    = abspath("../../../secrets")|' \
  "${TF_DIR}/main.tf"

sed -i \
  's|target    = "/etc/nginx/certs"|target    = "/etc/nginx/secrets"|' \
  "${TF_DIR}/main.tf"

(
  cd "${TF_DIR}"
  if ! terraform validate >/dev/null 2>&1; then
    terraform validate 2>&1 | tail -10
    fail "terraform validate failed — aborting before apply"
  fi
)
log "terraform validate: ok"

# ---------------------------------------------------------------------
# Recreate the NGINX container
#
# -replace forces destroy+create so new mount paths take effect.
# ---------------------------------------------------------------------
step "recreating NGINX container"
(
  cd "${TF_DIR}"
  terraform apply -replace=docker_container.nginx_gateway -auto-approve \
    2>&1 | tail -6
)

# Docker Desktop on Windows can take 10-15s to fully start the
# container after apply reports success.
sleep 15

# ---------------------------------------------------------------------
# Verify
#
# Mount paths first, then HTTP. /admin/ on HTTP returns 301 by
# design (Gap 5 redirects human-facing paths to HTTPS); the auth
# challenge lives on the HTTPS listener.
# ---------------------------------------------------------------------
step "verifying"

mounts="$(docker inspect nginx-public-data-gateway \
  --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{"\n"}}{{end}}')"

if echo "${mounts}" | grep -q '/secrets ->'; then
  log "secrets/ is mounted"
else
  echo "${mounts}"
  fail "secrets/ is NOT mounted — check docker inspect output above"
fi

if echo "${mounts}" | grep -q '/secrets/.htpasswd ->'; then
  log "secrets/.htpasswd is mounted"
else
  echo "${mounts}"
  fail "secrets/.htpasswd is NOT mounted"
fi

health="$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8118/health)"
[[ "${health}" == "200" ]] || fail "/health returned ${health}, expected 200"
log "/health: 200"

http_admin="$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8118/admin/)"
[[ "${http_admin}" == "301" ]] || fail "/admin/ on HTTP returned ${http_admin}, expected 301"
log "/admin/ on HTTP: 301 (redirects to HTTPS)"

https_admin="$(curl -sk -o /dev/null -w '%{http_code}' https://localhost:8443/admin/)"
[[ "${https_admin}" == "401" ]] || fail "/admin/ on HTTPS returned ${https_admin}, expected 401"
log "/admin/ on HTTPS without auth: 401"

admin_pw="$(cat "${SECRETS_DIR}/admin_password.txt")"
https_admin_ok="$(curl -sk -o /dev/null -w '%{http_code}' -u "admin:${admin_pw}" https://localhost:8443/admin/)"
[[ "${https_admin_ok}" == "200" ]] || fail "/admin/ with auth returned ${https_admin_ok}, expected 200"
log "/admin/ with auth: 200"

# ---------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------
step "done"

printf 'secrets/ contents:\n'
ls -1 "${SECRETS_DIR}" | sed 's/^/  /'

printf '\ncerts/ leftovers:\n'
ls -1 "${CERTS_DIR}" | sed 's/^/  /'

printf '\ngit status:\n'
(
  cd "${REPO_ROOT}"
  git status --short | sed 's/^/  /'
)

printf '\nnext: review the diff, then commit.\n'
printf '      git add -A && git commit -m "Refactor secrets out of git"\n'
printf '\nif /health failed, tail the container log:\n'
printf '      docker logs --tail 30 nginx-public-data-gateway\n'