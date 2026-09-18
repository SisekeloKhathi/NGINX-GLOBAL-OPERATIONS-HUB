\# Changelog



All notable changes to the NGINX Global Operations Hub project, in reverse chronological order.



\## 2026-09-16 — Blueprint gap closures, TLS hardening, secrets cleanup



\- Add root README

\- Untrack `secrets/` and remove stray `.py.txt`

\- Refactor secrets out of git

\- \*\*Gap 6\*\*: TLS troubleshooting runbook (blueprint Exam 4.3)

\- \*\*Gap 5\*\*: path-specific HTTP → HTTPS redirect for admin paths (blueprint Exam 3.5)

\- Ignore PKCS#12 bundles (contain client keys)

\- Ignore CA serial and CSR intermediate files

\- \*\*Gap 4\*\*: enable mTLS in HTTPS server block

\- \*\*Gap 4\*\*: mTLS via `ssl\_client\_certificate` and `ssl\_verify\_client` (blueprint Exam 3.4)

\- \*\*Gap 3\*\*: per-location log levels (blueprint Exam 3.3)

\- \*\*Gap 2\*\*: Unix socket upstream demonstration (blueprint Exam 2.4)

\- \*\*Gap 1\*\*: load balancing (`least\_conn`, `ip\_hash`) — no backup server on `ip\_hash`, per NGINX docs

\- Disable Grafana login; NGINX Basic Auth is the sole gate

\- Slow flights collector to 5-min interval

\- Fix Grafana proxy; ignore config backups



\## 2026-09-15 — Dashboard surface, HTTPS/auth, rate-limit hardening, IaC



\*\*Dashboard \& observability\*\*

\- Ignore local config backups

\- Fix Grafana proxy; add auth-disabled Grafana env vars

\- Fix Grafana proxy: remove subpath stripping

\- Add HTTPS routes for display, screens, dashboard, metrics; fix Grafana `root\_url`

\- Add `/dashboard/` and `/metrics/` NGINX routes; dedupe

\- Fix screens mount path — 3 levels up, not 4

\- Add screen template + NGINX routes for `/screen/` and `/api/display/`

\- Add display API, Prometheus, nginx-exporter; NGINX as public surface



\*\*HTTPS \& auth\*\*

\- Track `.htpasswd` and cert key for reproducible clone

\- Track gateway `.htpasswd` so the stack is reproducible from clone

\- Add certs and Terraform mounts for HTTPS + Basic Auth

\- Fix `/admin/` Basic Auth with `try\_files` + named location; add HTTPS on 8443



\*\*Rate limiting \& upstream tuning\*\*

\- Bump weather read timeout to 15s for upstream keepalive compatibility

\- Add upstream pools with keepalive; add bandwidth throttle on flights; restrict to GET/HEAD/OPTIONS; widen 429 cache; ignore upstream no-store

\- Flights collector: back off 15 minutes on 429 to align with gateway cache

\- Widen 429 cache window to 15 minutes to give upstream cooldown time

\- Cache 429 responses to break rate-limit spiral



\*\*Automation \& infrastructure as code\*\*

\- Use `command` instead of `shell` for Grafana health check

\- Fix ansible-lint violations: name plays, use `command`, prefix registers

\- Add GitHub Actions CI for Terraform, Ansible, and Python validation

\- Add Ansible playbooks to verify the ops stack

\- Ignore `.sql` files in terraform directory

\- Remove accidentally committed DB backup

\- Add Terraform to manage Postgres, Grafana, and NGINX gateway containers

\- Add automation engine: SQL/HTTP triggers, edge detection, actions

\- Add README and requirements for reproducible setup

\- Ignore `cache/` directories at repo root

\- Add FX/weather/flights/economics collectors; load DB config from env



\## 2026-09-06 — Monitoring stack and public gateway



\- Add complete monitoring stack configuration

\- Add NGINX public data gateway



\## 2026-09-01 — Initial commit



\- Initial NGINX Global Operations Hub scaffold

