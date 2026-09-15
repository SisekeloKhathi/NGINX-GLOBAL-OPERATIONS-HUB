# Global Operations Monitoring Stack

Collectors that pull FX rates, weather, flight data, and economic
indicators into a PostgreSQL database, visualised in Grafana.

## Architecture

    ┌───────────────┐   ┌──────────────────────┐   ┌──────────────┐
    │  Public APIs  │──▶│   NGINX Data Gateway │──▶│  Collectors  │
    │  (fx, meteo,  │   │   (port 8118)        │   │  (Python)    │
    │   opensky,    │   └──────────────────────┘   └──────┬───────┘
    │   worldbank)  │                                     │
    └───────────────┘                                     ▼
                                                  ┌──────────────┐
                                                  │  PostgreSQL  │
                                                  │  (ops_db)    │
                                                  └──────┬───────┘
                                                         │
                                                         ▼
                                                  ┌──────────────┐
                                                  │   Grafana    │
                                                  │   (port 3000)│
                                                  └──────────────┘

## Setup

### 1. Start containers

    docker start postgres grafana

### 2. Install Python dependencies

    pip install -r requirements.txt

### 3. Configure credentials

    cp .env.example .env
    # Edit .env and set DB_PASSWORD to the real value

### 4. Verify database connectivity

    docker exec -it postgres psql -U admin -d ops_db -c "SELECT 1;"

## Running a collector

    export DB_PASSWORD=secret       # or the value from .env
    python fx_collector.py          # Ctrl+C to stop

## Running all collectors in the background

    export DB_PASSWORD=secret
    nohup python fx_collector.py       &
    nohup python weather_collector.py  &
    nohup python flights_collector.py  &
    nohup python economics_collector.py &

    # To stop them all:
    pkill -f '_collector.py'

## Data tables

| Table            | Populated by             | Frequency |
|------------------|--------------------------|-----------|
| fx_rates         | fx_collector.py          | 1 minute  |
| weather_data     | weather_collector.py     | 1 minute  |
| flight_states    | flights_collector.py     | 1 minute  |
| economic_data    | economics_collector.py   | 1 minute  |

## Grafana

Open http://localhost:3000 and log in (default admin/admin).
The dashboard is in `grafana-dashboard.json` and can be imported
via Dashboards → Import.

## Environment variables

| Variable     | Default     | Purpose                     |
|--------------|-------------|-----------------------------|
| DB_HOST      | localhost   | PostgreSQL host             |
| DB_PORT      | 5432        | PostgreSQL port             |
| DB_NAME      | ops_db      | Database name               |
| DB_USER      | admin       | Database user               |
| DB_PASSWORD  | (none)      | Database password (required)|

## Troubleshooting

- **`fe_sendauth: no password supplied`** → `.env` isn't being
  read. Confirm you're running from the directory containing `.env`,
  or `export DB_PASSWORD=...` manually.
- **`connection refused`** → Postgres container isn't running.
  `docker start postgres`.
- **Empty Grafana panels** → Datasource UID mismatch. Check the
  datasource UID in Grafana matches `grafana-dashboard.json`.
