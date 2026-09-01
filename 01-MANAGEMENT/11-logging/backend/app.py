from flask import Flask, request
import time

app = Flask(__name__)

@app.route("/")
def home():
    return "LOGGING LAB — BACKEND WORKING\n"

@app.route("/error")
def error():
    return "SIMULATED APPLICATION ERROR\n", 500

@app.route("/slow")
def slow():
    time.sleep(2)
    return "SLOW RESPONSE\n"

@app.route("/health")
def health():
    return {
        "service": "logging-backend",
        "status": "healthy"
    }

app.run(host="0.0.0.0", port=8080)
