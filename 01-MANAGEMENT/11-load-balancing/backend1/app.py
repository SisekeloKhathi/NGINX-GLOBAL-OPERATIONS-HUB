from flask import Flask
import socket

app = Flask(__name__)
hostname = socket.gethostname()

@app.route("/")
def home():
    return f"Backend 1 - {hostname}\n"

@app.route("/health")
def health():
    return "OK"

app.run(host="0.0.0.0", port=8080)
