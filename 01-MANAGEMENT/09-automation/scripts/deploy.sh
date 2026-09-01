#!/bin/sh

set -e

echo "=== NGINX AUTOMATION DEPLOYMENT ==="

echo "[1/3] Testing NGINX configuration..."
docker exec nginx-automation nginx -t

echo "[2/3] Reloading NGINX..."
docker exec nginx-automation nginx -s reload

echo "[3/3] Testing application..."
curl -f http://localhost:8087/

echo
echo "=== DEPLOYMENT SUCCESSFUL ==="
