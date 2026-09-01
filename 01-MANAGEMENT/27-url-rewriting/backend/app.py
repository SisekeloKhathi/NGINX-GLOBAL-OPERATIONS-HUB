from flask import Flask, request
app = Flask(__name__)

@app.route("/users")
def users():
    return f"BACKEND RECEIVED: {request.path}\n", 200

@app.route("/orders")
def orders():
    return f"BACKEND RECEIVED: {request.path}\n", 200

app.run(host="0.0.0.0", port=8080)
