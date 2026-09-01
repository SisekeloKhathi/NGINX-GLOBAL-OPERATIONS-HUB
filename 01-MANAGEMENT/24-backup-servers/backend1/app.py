from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "PRIMARY BACKEND 1\n", 200

app.run(host="0.0.0.0", port=8080)
