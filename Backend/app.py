from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)  # Allow frontend to talk to backend

DB = "game_scores.db"  # Path to your database file (adjust if needed)


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
    password = data.get("password")  # For now, just placeholder

    if not email or not password:
        return jsonify({"success": False, "message": "Please enter email and password"})

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT user_id, name, role FROM users WHERE email=?", (email,))
    user = c.fetchone()
    conn.close()

    if user:
        user_id, name, role = user
        return jsonify({"success": True, "user_id": user_id, "name": name, "role": role})
    else:
        return jsonify({"success": False, "message": "User not found"})


# -----------------------------
# REGISTER API (Optional)
# -----------------------------
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    role = data.get("role", "student")  # default role

    if not name or not email:
        return jsonify({"success": False, "message": "Name and email required"})

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (name, email, role) VALUES (?, ?, ?)", (name, email, role))
        conn.commit()
        user_id = c.lastrowid
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"success": False, "message": "Email already exists"})
    conn.close()

    return jsonify({"success": True, "message": "Registration successful", "user_id": user_id})


# -----------------------------
# DASHBOARD API
# Returns all games and user's highest score for each
# -----------------------------
@app.route("/dashboard/<int:user_id>", methods=["GET"])
def dashboard(user_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # Get all games
    c.execute("SELECT game_id, game_name, section FROM games")
    games = c.fetchall()

    result = []
    for g in games:
        game_id, game_name, section = g
        c.execute("SELECT MAX(score) FROM scores WHERE user_id=? AND game_id=?", (user_id, game_id))
        high_score = c.fetchone()[0]
        played = True if high_score else False
        result.append({
            "game_id": game_id,
            "game_name": game_name,
            "section": section,
            "played": played,
            "high_score": high_score if high_score else 0
        })

    conn.close()
    return jsonify(result)


# -----------------------------
# UPDATE SCORE API
# -----------------------------
@app.route("/update-score", methods=["POST"])
def update_score():
    data = request.json
    user_id = data.get("user_id")
    game_id = data.get("game_id")
    score = data.get("score")

    if not user_id or not game_id or score is None:
        return jsonify({"success": False, "message": "Missing data"})

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO scores (user_id, game_id, score) VALUES (?, ?, ?)", (user_id, game_id, score))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Score updated"})


# -----------------------------
# RUN SERVER
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
