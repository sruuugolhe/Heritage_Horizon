from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return jsonify({"message": "Backend is running!"})

@app.route("/score", methods=["POST"])
def score():
    data = request.json
    return jsonify({
        "status": "success",
        "score": data.get("score")
    })

if __name__ == "__main__":
    app.run(debug=True)
