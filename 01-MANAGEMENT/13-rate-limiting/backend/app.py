from flask import Flask, request, jsonify
import time
import random

app = Flask(__name__)

@app.route("/")
def home():
    return {
        "message": "Rate Limiting Lab",
        "timestamp": time.time(),
        "client": request.remote_addr
    }

@app.route("/slow")
def slow():
    # Simulate slow endpoint with random delay
    delay = random.uniform(0.5, 1.5)
    time.sleep(delay)
    return {"message": f"Slow response complete (delayed {delay:.2f}s)"}

@app.route("/health")
def health():
    return "OK"

app.run(host="0.0.0.0", port=8080)
