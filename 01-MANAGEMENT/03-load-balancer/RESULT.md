# NGINX Load Balancer — Lab Result

Date: 2026-08-31

## Normal Operation

NGINX distributed requests across:

- backend-1
- backend-2
- backend-3

## Failure Injection

backend-2 was stopped.

Result:

- backend-1 continued serving traffic
- backend-3 continued serving traffic
- backend-2 received no traffic

## Recovery

backend-2 was restarted.

Six requests were sent after recovery.

Observed:

BACKEND-1
BACKEND-3
BACKEND-1
BACKEND-2
BACKEND-3
BACKEND-1

Backend-2 successfully received traffic again.

## Final Result

LOAD BALANCING = PASS
FAILURE HANDLING = PASS
BACKEND RECOVERY = PASS

## Architecture

CLIENT
  ↓
NGINX :8081
  ↓
backend_pool
  ├── backend-1
  ├── backend-2
  └── backend-3
