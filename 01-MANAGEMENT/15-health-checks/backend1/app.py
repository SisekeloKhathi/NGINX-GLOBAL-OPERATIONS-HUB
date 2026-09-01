from flask import Flask
import itertools

app = Flask(__name__)
counter = itertools.count(1)

@app.route("/")
def home():
    n = next(counter)
    if n % 3 == 0:
        return "Backend 1 - FAIL\n", 500
    return "Backend 1 - Healthy\n"

app.run(host="0.0.0.0", port=8080)
