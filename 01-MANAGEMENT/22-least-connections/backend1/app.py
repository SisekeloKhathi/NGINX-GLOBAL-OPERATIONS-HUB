from flask import Flask
import time

app = Flask(__name__)

@app.route("/")
def home():
    time.sleep(5)
    return "BACKEND 1 — SLOW\n", 200

@app.route("/health")
def health():
    return "BACKEND 1 OK\n", 200

app.run(host="0.0.0.0", port=8080)
