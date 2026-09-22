#!/usr/bin/env python3
import os
from datetime import datetime, timezone
import psycopg2
import psycopg2.extras
import json
import redis
from flask import Flask, jsonify

app = Flask(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
CACHE_TTL = int(os.getenv("CACHE_TTL", 60))

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "postgres"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME", "ops_db"),
    "user": os.getenv("DB_USER", "admin"),
    "password": os.getenv("DB_PASSWORD"),
}

def db_conn():
    return psycopg2.connect(**DB_CONFIG)

def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def fetch_one(q, p=None):
    with db_conn() as c:
        with c.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(q, p or ())
            r = cur.fetchone()
            return dict(r) if r else None

def fetch_all(q, p=None):
    with db_conn() as c:
        with c.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(q, p or ())
            return [dict(r) for r in cur.fetchall()]

@app.route("/health")
def health():
    try:
        with db_conn() as c:
            with c.cursor() as cur:
                cur.execute("SELECT 1")
        return jsonify({"status": "ok", "time": now_iso()})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

def cached_response(key, loader):
    try:
        cached = redis_client.get(key)
        if cached:
            data = json.loads(cached)
            data["cache"] = "hit"
            return jsonify(data)

        data = loader()

        try:
            redis_client.setex(key, CACHE_TTL, json.dumps(data))
        except Exception:
            pass

        data["cache"] = "miss"
        return jsonify(data)

    except Exception:
        try:
            data = loader()
            data["cache"] = "fallback"
            return jsonify(data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500


def load_fx():
    rows = fetch_all("SELECT DISTINCT ON (target_currency) target_currency, rate, timestamp FROM fx_rates ORDER BY target_currency, timestamp DESC")
    rates = {r["target_currency"]: float(r["rate"]) for r in rows}
    latest = max((r["timestamp"] for r in rows), default=None)
    return {"source": "fx", "updated": latest.isoformat() if latest else None, "server_time": now_iso(), "rates": rates}


def load_weather():
    r = fetch_one("SELECT temperature, windspeed, winddirection, weathercode, timestamp FROM weather_data ORDER BY timestamp DESC LIMIT 1")
    if not r:
        return {"source": "weather", "updated": None, "server_time": now_iso(), "data": None}
    return {"source": "weather", "updated": r["timestamp"].isoformat() if r["timestamp"] else None, "server_time": now_iso(), "data": {"temperature": float(r["temperature"]) if r["temperature"] is not None else None, "windspeed": float(r["windspeed"]) if r["windspeed"] is not None else None, "winddirection": float(r["winddirection"]) if r["winddirection"] is not None else None, "weathercode": int(r["weathercode"]) if r["weathercode"] is not None else None}}


def load_flights():
    r = fetch_one("SELECT aircraft_count, timestamp FROM flight_states ORDER BY timestamp DESC LIMIT 1")
    if not r:
        return {"source": "flights", "updated": None, "server_time": now_iso(), "data": None}
    return {"source": "flights", "updated": r["timestamp"].isoformat() if r["timestamp"] else None, "server_time": now_iso(), "data": {"aircraft_count": int(r["aircraft_count"])}}


def load_economics():
    r = fetch_one("SELECT value, reporting_year, timestamp FROM economic_data ORDER BY timestamp DESC LIMIT 1")
    if not r:
        return {"source": "economics", "updated": None, "server_time": now_iso(), "data": None}
    return {"source": "economics", "updated": r["timestamp"].isoformat() if r["timestamp"] else None, "server_time": now_iso(), "data": {"value": float(r["value"]) if r["value"] is not None else None, "reporting_year": r["reporting_year"]}}


@app.route("/fx")
def fx():
    return cached_response("display-api:fx", load_fx)


@app.route("/weather")
def weather():
    return cached_response("display-api:weather", load_weather)


@app.route("/flights")
def flights():
    return cached_response("display-api:flights", load_flights)


@app.route("/economics")
def economics():
    return cached_response("display-api:economics", load_economics)


@app.route("/all")
def all_sources():
    return jsonify({"server_time": now_iso(), "fx": fx().get_json(), "weather": weather().get_json(), "flights": flights().get_json(), "economics": economics().get_json()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
