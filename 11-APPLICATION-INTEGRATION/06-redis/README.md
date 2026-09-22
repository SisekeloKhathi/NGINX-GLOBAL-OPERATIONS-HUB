# Redis Cache

## What I am building

I am using Redis as the fast temporary memory layer for the Global Operations Hub.

I am keeping PostgreSQL as the persistent database.

I am using Redis to cache frequently requested display data so the display API does not repeatedly query PostgreSQL for the same information.

I am also using Redis so the display API can continue working when Redis is temporarily unavailable.

## Architecture

```text
NGINX :8118
    |
    v
display-api :5001
    |
    +----> Redis :6379
    |        |
    |        +---- Cached responses
    |
    +----> PostgreSQL :5432
             |
             +---- Persistent data
```

I am separating the responsibilities:

- NGINX is my public entry point.
- display-api is my application layer.
- Redis is my fast temporary cache.
- PostgreSQL is my persistent data store.

## Redis deployment

I am running Redis as a Docker container.

```text
Container: redis
Image: redis:7-alpine
Port: 6379
Network: ops-network
Volume: redis-data
```

I am enabling Redis AOF persistence so Redis data can survive a container restart.

## Application connection

I am giving display-api the Redis connection information through environment variables:

```text
REDIS_HOST=redis
REDIS_PORT=6379
CACHE_TTL=60
```

I am using the Docker service name `redis` because Docker provides service discovery on `ops-network`.

I am setting the cache TTL to 60 seconds so cached information does not remain indefinitely.

## What I am caching

I am caching these display API responses:

```text
display-api:fx
display-api:weather
display-api:flights
display-api:economics
```

## How the cache works

```text
Request
   |
   v
Check Redis
   |
   +---- HIT ----> Return cached data
   |
   +---- MISS ---> Read PostgreSQL
                       |
                       v
                  Store in Redis
                       |
                       v
                  Return data
```

I am returning the cache state in the API response:

```text
cache=hit
cache=miss
cache=fallback
```

## Failure handling

I am treating Redis as an optimization rather than a dependency that can take down the display API.

I tested the failure path by stopping Redis. The display API returned `cache=fallback` and continued serving the existing data.

I then started Redis again. The display API successfully returned `cache=hit`.

## Verification

I am checking Redis directly:

```bash
# I am writing a temporary test value into Redis.
docker exec redis redis-cli SET hub:test "redis-working" EX 300

# I am reading the value back from Redis.
docker exec redis redis-cli GET hub:test
```

I am checking the display API cache keys:

```bash
# I am checking which display API responses are currently cached.
docker exec redis redis-cli KEYS "display-api:*"
```

I am testing the complete NGINX to display-api to Redis path:

```bash
# I am testing the display API through the NGINX public entry point.
curl -s http://localhost:8118/api/display/fx
```

## Where I took the configuration from

I am using the Redis Docker configuration from:

`01-MANAGEMENT/37-public-data-gateway/docker-compose.yml`

I am using the display API implementation from:

`01-MANAGEMENT/38-monitoring/display-api/`

I am using Terraform to manage the display API container from:

`01-MANAGEMENT/40-automation/terraform/`

## Result

I now have Redis running inside the existing Global Operations Hub infrastructure.

I have demonstrated cache miss, cache hit, Redis failure fallback, and Redis recovery.

Redis is therefore providing a fast caching layer without becoming a single point of failure for the display API.
