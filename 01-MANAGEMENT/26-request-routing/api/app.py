from flask import Flask, jsonify
app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "service": "API",
        "status": "healthy"
    })

app.run(host="0.0.0.0", port=8080)
