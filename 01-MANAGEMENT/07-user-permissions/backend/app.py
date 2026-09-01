from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "USER PERMISSIONS LAB — BACKEND WORKING"

@app.route("/public")
def public():
    return "PUBLIC AREA — ACCESS GRANTED"

@app.route("/admin")
def admin():
    return "ADMIN AREA — ACCESS GRANTED"

app.run(host="0.0.0.0", port=8080)
