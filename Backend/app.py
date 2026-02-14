from flask import Flask, render_template, request, redirect, session, abort, url_for, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
import random
from datetime import datetime

# ---------------- APP ----------------

app = Flask(
    __name__,
    template_folder="../frontend",
    static_folder="../frontend"
)

app.secret_key = "secret123"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "game_scores.db")

# ---------------- DATABASE ----------------

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT DEFAULT 'user',
        coins INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1,
        last_spin TEXT,
        last_login TEXT
    )
    """)

    conn.commit()
    conn.close()

# ---------------- AUTH ----------------

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return wrap


def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")

        conn = get_db()
        user = conn.execute(
            "SELECT role FROM users WHERE id=?",
            (session["user_id"],)
        ).fetchone()
        conn.close()

        if not user or user["role"] != "admin":
            abort(403)

        return f(*args, **kwargs)
    return wrap

# ---------------- SIGNUP ----------------

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        u = request.form["username"]
        e = request.form["email"]
        p = generate_password_hash(request.form["password"])

        try:
            conn = get_db()
            conn.execute("""
            INSERT INTO users(username,email,password)
            VALUES(?,?,?)
            """, (u, e, p))
            conn.commit()
            conn.close()
            return redirect("/login")

        except:
            return render_template(
                "createaccount.html",
                error="User already exists",
                username=u,
                email=e
            )

    return render_template("createaccount.html")

# ---------------- HOME ----------------

@app.route("/")
def titlepage():
    return render_template("titlepage.html")

# ---------------- DASHBOARD ----------------

@app.route('/dashboard')
@login_required
def dashboard():

    conn = get_db()

    user = conn.execute(
        "SELECT username, coins, level FROM users WHERE id=?",
        (session['user_id'],)
    ).fetchone()

    total_games = 8

    completed_games = conn.execute(
        "SELECT COUNT(DISTINCT game_name) FROM progress WHERE user_id=? AND completed=1",
        (session['user_id'],)
    ).fetchone()[0]

    progress_percent = int((completed_games / total_games) * 100) if total_games > 0 else 0

    conn.close()

    return render_template(
        "dashboard.html",
        user=user,
        progress_percent=progress_percent,
        completed_games=completed_games,
        total_games=total_games
    )

# ---------------- DAILY SPIN ----------------

@app.route('/spin')
@login_required
def spin():

    conn = get_db()

    user = conn.execute(
        "SELECT last_spin FROM users WHERE id=?",
        (session['user_id'],)
    ).fetchone()

    today = datetime.now().strftime("%Y-%m-%d")

    if user["last_spin"] == today:
        conn.close()
        return jsonify({"message": "You already spun today!", "reward": 0})

    rewards = [10, 20, 30, 50, 100]
    reward = random.choice(rewards)

    conn.execute(
        "UPDATE users SET coins = coins + ?, last_spin=? WHERE id=?",
        (reward, today, session['user_id'])
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "You won!", "reward": reward})

# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        u = request.form["username"]
        p = request.form["password"]

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE username=?",
            (u,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(user["password"], p):

            session.clear()
            session["user_id"] = user["id"]
            session["role"] = user["role"]

            if user["role"] == "admin":
                return redirect("/admin")

            return redirect("/slide")

        return render_template(
            "FSLOGIN.html",
            error="Invalid Login"
        )

    return render_template("FSLOGIN.html")

# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("titlepage"))

# ---------------- COMPLETE GAME ----------------

@app.route('/complete_game', methods=['POST'])
@login_required
def complete_game():

    user_id = session['user_id']
    game_name = request.form['game_name']
    score = int(request.form['score'])

    conn = get_db()

    conn.execute(
        "INSERT INTO progress (user_id, game_name, score, completed) VALUES (?, ?, ?, 1)",
        (user_id, game_name, score)
    )

    conn.execute(
        "UPDATE users SET coins = coins + 50 WHERE id=?",
        (user_id,)
    )

    coins = conn.execute(
        "SELECT coins FROM users WHERE id=?",
        (user_id,)
    ).fetchone()[0]

    if coins >= 500:
        conn.execute(
            "UPDATE users SET level=2 WHERE id=?",
            (user_id,)
        )

    conn.commit()
    conn.close()

    return redirect('/student_dashboard')

# ---------------- SLIDE ----------------

@app.route("/slide")
@login_required
def slide():
    return render_template("slide2.html")


@app.route("/heritage")
def heritage():
    return render_template("IND_FinalOption.html")  # or your first heritage page

@app.route("/heritage/facts")
def heritage_dyk():
    return render_template("IND_FinalDoYouKnow.html")


@app.route("/heritage/wordpuzzle")
def heritage_wordpuzzle():
    return render_template("wordpuzzleH.html")

@app.route("/heritage/maze")
def heritage_maze():
    return render_template("IND_FinalMaze1.html")


@app.route("/heritage/quiz")
def heritage_quiz():
    return render_template("IND_finalQuiz.html")


@app.route("/heritage/cards")
def heritage_final():
    return render_template("InFINALCARD.html")



@app.route("/solar")
def solar():
    return render_template("optionsspace.html")  # or your first solar page


@app.route('/solar/quiz')
def solar_doyouknow():
    return render_template("solarquiz.html")


@app.route('/solar/asteriod')
def solar_asteriod():
    return render_template("asteriodssolar.html")


@app.route('/solar/puzzle')
def solar_puzzle():
    return render_template("wordpuzzlesolar.html")


@app.route('/solar/crush')
def solar_cards():
    return render_template("candycrush.html")


@app.route('/solar/facts')
def solar_facts():
    return render_template("DoYouKnowSpace.html")


# ---------------- ADMIN ----------------

@app.route("/admin")
@admin_required
def admin():

    conn = get_db()
    users = conn.execute("SELECT * FROM users").fetchall()
    conn.close()

    return render_template(
        "admin_dashboard.html",
        users=users
    )

# ---------------- CREATE ADMIN ----------------

def create_admin():

    conn = get_db()

    admin = conn.execute(
        "SELECT * FROM users WHERE username='admin'"
    ).fetchone()

    if not admin:
        password = generate_password_hash("admin123")
        conn.execute("""
        INSERT INTO users(username,email,password,role)
        VALUES(?,?,?,?)
        """, ("admin", "admin@gmail.com", password, "admin"))
        conn.commit()
        print("Admin created: username=admin | password=admin123")

    conn.close()

# ---------------- MAIN ----------------

if __name__ == "__main__":
    init_db()
    create_admin()
    app.run(debug=True)
