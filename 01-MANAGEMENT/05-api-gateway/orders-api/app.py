from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/api/orders")
def orders():
    return jsonify(
        service="orders-api",
        status="OK",
        orders=5
    )

app.run(host="0.0.0.0", port=8080)
