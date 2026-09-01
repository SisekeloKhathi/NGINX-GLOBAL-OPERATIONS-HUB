from flask import Flask, request
import time

app = Flask(__name__)

@app.route("/")
def home():
    return "MODULES LAB — BACKEND WORKING\n"

@app.route("/slow")
def slow():
    time.sleep(2)
    return "SLOW RESPONSE — MODULE TEST\n"

@app.route("/headers")
def headers():
    return {
        "host": request.headers.get("Host"),
        "user_agent": request.headers.get("User-Agent"),
        "x_forwarded_for": request.headers.get("X-Forwarded-For"),
        "x_real_ip": request.headers.get("X-Real-IP")
    }

app.run(host="0.0.0.0", port=8080)
