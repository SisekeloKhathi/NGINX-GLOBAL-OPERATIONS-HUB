# NGINX Reverse Proxy

## Objective

Place NGINX in front of an application and forward client requests to the backend.

## Current Architecture

CLIENT
  |
  | HTTP :8080
  v
NGINX
  |
  | proxy_pass
  v
backend:8080
  |
  v
Flask application

## NGINX Configuration

server {
    listen 80;

    location / {
        proxy_pass http://backend:8080;
    }
}

## Docker Architecture

NGINX container:
nginx-lab

Backend container:
nginx-backend

Docker DNS:
backend

## Validation

Test NGINX configuration:

docker exec nginx-lab nginx -t

Inspect active configuration:

docker exec nginx-lab nginx -T

Test backend resolution:

docker exec nginx-lab getent hosts backend

Test application:

curl http://localhost:8080

## Expected Result

HTTP/1.1 200 OK

Response:

NGINX → BACKEND WORKING

## What This Demonstrates

- NGINX listening on port 80
- Docker port publishing
- Docker internal networking
- Docker DNS service discovery
- NGINX proxy_pass
- Reverse proxy request flow
- Backend application communication
