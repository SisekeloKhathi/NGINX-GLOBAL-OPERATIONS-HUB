from flask import Flask, request, jsonify, make_response
import time
import random

app = Flask(__name__)

@app.route("/")
def home():
    return {
        "message": "Caching Lab",
        "timestamp": time.time()
    }

@app.route("/cached")
def cached():
    time.sleep(0.5)  # Simulate processing time
    response = make_response({
        "message": "Cached Response",
        "generated_at": time.time(),
        "random_value": random.randint(1, 1000)
    })
    response.headers['Cache-Control'] = 'public, max-age=60'
    return response

@app.route("/uncached")
def uncached():
    time.sleep(0.5)  # Simulate processing time
    return {
        "message": "Uncached Response",
        "generated_at": time.time(),
        "random_value": random.randint(1, 1000)
    }

@app.route("/health")
def health():
    return "OK"

app.run(host="0.0.0.0", port=8080)
