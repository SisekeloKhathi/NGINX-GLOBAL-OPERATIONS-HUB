from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/api/users")
def users():
    return jsonify(
        service="users-api",
        status="OK",
        users=3
    )

app.run(host="0.0.0.0", port=8080)
