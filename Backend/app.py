from flask import Flask, render_template, request, redirect, url_for, session, abort
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os

# ---------------- CONFIG ----------------
app = Flask(
    __name__,
    template_folder="FRONTEND",
    static_folder="FRONTEND"
)

app.secret_key = "super_secret_key_change_later"
DB_NAME = "app.db"

# ---------------- DATABASE ----------------
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS quiz_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            quiz_name TEXT,
            score INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

# ---------------- AUTH DECORATOR ----------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# ---------------- ROUTES ----------------

@app.route("/")
def title():
    return render_template("titlepage.html")

@app.route("/slide")
def slide():
    return render_template("slide2.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))

        return render_template("FSLOGIN.html", error="Invalid credentials")

    return render_template("FSLOGIN.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

# ---------------- GAME / CONTENT ROUTES ----------------

@app.route("/optionsspace")
@login_required
def optionsspace():
    return render_template("optionsspace.html")

@app.route("/maze")
@login_required
def maze():
    return render_template("IND_FinalMaze1.html")

@app.route("/option")
@login_required
def option():
    return render_template("IND_FinalOption.html")

@app.route("/finalcard")
@login_required
def finalcard():
    return render_template("INFINALCARD.html")

@app.route("/solarquiz", methods=["GET", "POST"])
@login_required
def solarquiz():
    if request.method == "POST":
        score = request.form.get("score", 0)
        conn = get_db()
        conn.execute(
            "INSERT INTO quiz_scores (user_id, quiz_name, score) VALUES (?, ?, ?)",
            (session["user_id"], "solarquiz", score)
        )
        conn.commit()
        conn.close()
    return render_template("solarquiz.html")

@app.route("/finalquiz", methods=["GET", "POST"])
@login_required
def finalquiz():
    if request.method == "POST":
        score = request.form.get("score", 0)
        conn = get_db()
        conn.execute(
            "INSERT INTO quiz_scores (user_id, quiz_name, score) VALUES (?, ?, ?)",
            (session["user_id"], "finalquiz", score)
        )
        conn.commit()
        conn.close()
    return render_template("IND_finalQuiz.html")

@app.route("/solarasteroid")
@login_required
def solarasteroid():
    return render_template("solaraseroid.html")

@app.route("/solarcrush")
@login_required
def solarcrush():
    return render_template("solarcrush.html")

@app.route("/solardoyouknow")
@login_required
def solardoyouknow():
    return render_template("solardoyouknow.html")

@app.route("/solarpuzzle")
@login_required
def solarpuzzle():
    return render_template("solarpuzzle.html")

@app.route("/solarwordpuzzle")
@login_required
def solarwordpuzzle():
    return render_template("solarwordpuzzle.html")

@app.route("/wordpuzzle")
@login_required
def wordpuzzle():
    return render_template("wordpuzzle.html")

# ---------------- ERROR HANDLING ----------------
@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404 - Page Not Found</h1>", 404

# ---------------- MAIN ----------------
if __name__ == "__main__":
    if not os.path.exists(DB_NAME):
        init_db()
        print("Database created")

    app.run(debug=True)