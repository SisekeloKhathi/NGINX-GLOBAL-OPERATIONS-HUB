from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "RATE LIMIT BACKEND — SUCCESS\n"

app.run(host="0.0.0.0", port=8080)
