from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return {
        "message": "SSL Lab - Backend Working",
        "headers": dict(request.headers),
        "scheme": request.scheme
    }

@app.route("/health")
def health():
    return "OK"

app.run(host="0.0.0.0", port=8080)
