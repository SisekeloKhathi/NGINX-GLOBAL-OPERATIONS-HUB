#!/usr/bin/env python3
"""Self-healing loop for the NGINX operations gateway."""

import os
import json
import time
import threading
from datetime import datetime, timezone

import requests
from flask import Flask, jsonify

app = Flask(__name__)

PROM   = os.getenv("PROMETHEUS_URL", "http://prometheus:9090")
OLLAMA = os.getenv("OLLAMA_URL",     "http://ollama:11434")
MODEL  = os.getenv("OLLAMA_MODEL",   "llama3.2:1b")
CYCLE  = int(os.getenv("CYCLE_SECONDS", 60))

events = []


def now():
    return datetime.now(timezone.utc).isoformat()


def query_prom(expr):
    """Return a single scalar from Prometheus, or None, or {'error': ...}."""
    try:
        r = requests.get(f"{PROM}/api/v1/query", params={"query": expr}, timeout=5)
        r.raise_for_status()
        result = r.json().get("data", {}).get("result", [])
        return float(result[0]["value"][1]) if result else None
    except Exception as e:
        return {"error": str(e)}


def ask_ollama(prompt):
    """Return the model's reply, or an error string on failure."""
    try:
        r = requests.post(
            f"{OLLAMA}/api/generate",
            json={"model": MODEL, "prompt": prompt, "stream": False},
            timeout=60,
        )
        r.raise_for_status()
        return r.json().get("response", "")
    except Exception as e:
        return f"ollama_error: {e}"


def execute_action(action, context):
    """Execute a pre-approved remediation. LLM proposes, this disposes.

    restart_nginx is deliberately NOT implemented. A false positive on
    a connection-count threshold would cause an outage that a text
    diagnosis cannot justify.
    """
    if action == "restart_nginx":
        return "refused: manual approval required"
    if action == "log_and_alert":
        return "logged"
    if action == "no_op":
        return "no_op"
    return f"unknown action: {action}"


def cycle():
    """One evaluation pass: read metrics, check anomaly, maybe ask, log."""
    metrics = {
        "connections_active":  query_prom("nginx_connections_active"),
        "connections_reading": query_prom("nginx_connections_reading"),
        "connections_writing": query_prom("nginx_connections_writing"),
    }

    conn = metrics.get("connections_active")
    busy = (metrics.get("connections_reading") or 0) + (
        metrics.get("connections_writing") or 0
    )

    anomaly = (
        isinstance(conn, (int, float)) and conn > 50 and conn > (busy * 3 + 10)
    )
    if not anomaly:
        return

    prompt = (
        "You are an SRE assistant. NGINX metrics:\n"
        + json.dumps(metrics, indent=2)
        + "\nOne sentence: likely cause and safest action?"
    )
    diagnosis = ask_ollama(prompt)

    event = {
        "time": now(),
        "metrics": metrics,
        "diagnosis": diagnosis.strip(),
        "action": "log_and_alert",
        "result": execute_action("log_and_alert", metrics),
    }
    events.append(event)
    print(json.dumps(event))


def background_loop():
    while True:
        try:
            cycle()
        except Exception as e:
            print(f"cycle error: {e}")
        time.sleep(CYCLE)


@app.route("/health")
def health():
    return jsonify({"status": "ok", "model": MODEL, "time": now()})


@app.route("/events")
def list_events():
    return jsonify({"events": events[-20:]})


@app.route("/test_llm")
def test_llm():
    """Smoke test — proves Ollama is reachable and the model is loaded."""
    return jsonify({"reply": ask_ollama("Say hello in five words.")})


if __name__ == "__main__":
    threading.Thread(target=background_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=5002, debug=False)