from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "SHARED MEMORY LAB — BACKEND WORKING"

@app.route("/counter")
def counter():
    return "SHARED MEMORY TEST"

app.run(host="0.0.0.0", port=8080)
