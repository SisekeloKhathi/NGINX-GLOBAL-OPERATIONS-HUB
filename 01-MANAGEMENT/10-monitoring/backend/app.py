from flask import Flask
import time

app = Flask(__name__)

@app.route("/")
def home():
    return "MONITORING LAB — BACKEND WORKING\n"

@app.route("/health")
def health():
    return {
        "status": "healthy",
        "service": "monitoring-backend"
    }

@app.route("/metrics")
def metrics():
    return {
        "requests": 100,
        "uptime_seconds": int(time.time())
    }

app.run(host="0.0.0.0", port=8080)
