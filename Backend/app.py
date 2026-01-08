from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)   # Allows frontend (HTML/JS) to talk to backend

# -----------------------------
# TEST ROUTE
# -----------------------------
@app.route("/", methods=["GET"])
def home():
    return "Backend is running"

# -----------------------------
# LOGIN API
# -----------------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if email and password:
        return jsonify({
            "success": True,
            "message": "Login successful"
        })
    else:
        return jsonify({
            "success": False,
            "message": "Please enter email and password"
        })

# -----------------------------
# REGISTER API (Optional)
# -----------------------------
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    return jsonify({
        "success": True,
        "message": "Registration successful"
    })

# -----------------------------
# DASHBOARD API
# -----------------------------
@app.route("/dashboard", methods=["GET"])
def dashboard():
    return jsonify({
        "username": "Player1",
        "points": 20,
        "level": 1
    })

# -----------------------------
# UPDATE SCORE API
# -----------------------------
@app.route("/update-score", methods=["POST"])
def update_score():
    return jsonify({
        "points": 30,
        "level": 2
    })

# -----------------------------
# RUN SERVER
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
