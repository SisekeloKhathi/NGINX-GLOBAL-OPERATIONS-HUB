#!/usr/bin/env python3
import os
from datetime import datetime, timezone
import psycopg2
import psycopg2.extras
from flask import Flask, jsonify

app = Flask(__name__)

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

@app.route("/fx")
def fx():
    rows = fetch_all("SELECT DISTINCT ON (target_currency) target_currency, rate, timestamp FROM fx_rates ORDER BY target_currency, timestamp DESC")
    rates = {r["target_currency"]: float(r["rate"]) for r in rows}
    latest = max((r["timestamp"] for r in rows), default=None)
    return jsonify({"source": "fx", "updated": latest.isoformat() if latest else None, "server_time": now_iso(), "rates": rates})

@app.route("/weather")
def weather():
    r = fetch_one("SELECT temperature, windspeed, winddirection, weathercode, timestamp FROM weather_data ORDER BY timestamp DESC LIMIT 1")
    if not r:
        return jsonify({"source": "weather", "updated": None, "data": None})
    return jsonify({"source": "weather", "updated": r["timestamp"].isoformat() if r["timestamp"] else None, "server_time": now_iso(), "data": {"temperature": float(r["temperature"]) if r["temperature"] is not None else None, "windspeed": float(r["windspeed"]) if r["windspeed"] is not None else None, "winddirection": float(r["winddirection"]) if r["winddirection"] is not None else None, "weathercode": int(r["weathercode"]) if r["weathercode"] is not None else None}})

@app.route("/flights")
def flights():
    r = fetch_one("SELECT aircraft_count, timestamp FROM flight_states ORDER BY timestamp DESC LIMIT 1")
    if not r:
        return jsonify({"source": "flights", "updated": None, "data": None})
    return jsonify({"source": "flights", "updated": r["timestamp"].isoformat() if r["timestamp"] else None, "server_time": now_iso(), "data": {"aircraft_count": int(r["aircraft_count"])}})

@app.route("/economics")
def economics():
    r = fetch_one("SELECT value, reporting_year, timestamp FROM economic_data ORDER BY timestamp DESC LIMIT 1")
    if not r:
        return jsonify({"source": "economics", "updated": None, "data": None})
    return jsonify({"source": "economics", "updated": r["timestamp"].isoformat() if r["timestamp"] else None, "server_time": now_iso(), "data": {"value": float(r["value"]) if r["value"] is not None else None, "reporting_year": r["reporting_year"]}})

@app.route("/all")
def all_sources():
    return jsonify({"server_time": now_iso(), "fx": fx().get_json(), "weather": weather().get_json(), "flights": flights().get_json(), "economics": economics().get_json()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
