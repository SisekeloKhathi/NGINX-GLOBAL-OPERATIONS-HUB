from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/api/health")
def health():
    return jsonify(
        service="health-api",
        status="HEALTHY"
    )

app.run(host="0.0.0.0", port=8080)
