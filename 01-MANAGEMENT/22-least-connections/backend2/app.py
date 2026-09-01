from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "BACKEND 2 — FAST\n", 200

app.run(host="0.0.0.0", port=8080)
