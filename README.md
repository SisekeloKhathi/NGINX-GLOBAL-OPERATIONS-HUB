# NGINX Global Operations Hub

One paragraph: what this is, what it demonstrates.

## Stack
Table of eight containers, one line each, with port.

## Quick start
Three commands:
  ./scripts/gen-secrets.sh
  cd .../terraform && terraform init && terraform apply
  ./verify.sh

## What this demonstrates
The six Gaps as a table — gap | blueprint objective | file | verified by.

## Architecture
One ASCII diagram of the container network.

## Design decisions worth reading
- Why NGINX is the only public surface
- Why the self-healer refuses to auto-restart NGINX
- Why secrets are bcrypt, not plaintext

## What's not here
Real CA, HA, multi-host, secret rotation, real alerting.

## Status
Checklist of what's running and what's planned.