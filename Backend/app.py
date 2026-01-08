from flask import Flask, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "Backend running"

@app.route("/silde2")
def silde2():
    return send_from_directory("../frontend", "silde2.html")

if __name__ == "__main__":
    app.run(debug=True)

