from flask import Flask
import time

app = Flask(__name__)

@app.route("/")
def home():
    time.sleep(30)
    return "BACKEND FINALLY RESPONDED\n", 200

app.run(host="0.0.0.0", port=8080)
