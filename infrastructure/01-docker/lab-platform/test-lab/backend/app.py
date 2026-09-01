from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "SHARED BASE IMAGE — WORKING\n"

app.run(host="0.0.0.0", port=8080)
