from flask import Flask, render_template, request, redirect, url_for, session, abort
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os

# ---------------- CONFIG ----------------
app = Flask(
    __name__,
    template_folder="../frontend",
    static_folder="../frontend"
)

app.secret_key = "super_secret_key_change_later"
DB_NAME = "game_scores.db"


# ---------------- DATABASE ----------------
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    # USERS TABLE
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            last_login TIMESTAMP
        )
    """)

    # SCORES TABLE
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


# ---------------- AUTH DECORATORS ----------------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        if "user_id" not in session:
            return redirect(url_for("login"))

        conn = get_db()
        user = conn.execute(
            "SELECT role FROM users WHERE id=?",
            (session["user_id"],)
        ).fetchone()
        conn.close()

        if user["role"] != "admin":
            abort(403)

        return f(*args, **kwargs)

    return decorated


# ---------------- ROUTES ----------------

@app.route("/")
def title():
    return render_template("titlepage.html")


@app.route("/slide")
def slide():
    return render_template("slide2.html")


# ---------------- SIGNUP ----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        hashed = generate_password_hash(password)

        try:
            conn = get_db()

            conn.execute("""
                INSERT INTO users (username, password)
                VALUES (?, ?)
            """, (username, hashed))

            conn.commit()
            conn.close()

            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            return render_template(
                "createaccount.html",
                error="Username already exists"
            )

    return render_template("createaccount.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()

        if user and check_password_hash(user["password"], password):

            # Update last login
            conn.execute(
                "UPDATE users SET last_login=CURRENT_TIMESTAMP WHERE id=?",
                (user["id"],)
            )

            conn.commit()
            conn.close()

            # Save session
            session["user_id"] = user["id"]
            session["username"] = user["username"]

            # Redirect admin
            if user["role"] == "admin":
                return redirect(url_for("admin"))

            return redirect(url_for("dashboard"))

        conn.close()

        return render_template("FSLOGIN.html", error="Invalid username or password")

    return render_template("FSLOGIN.html")



# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------------- ADMIN DASHBOARD ----------------
@app.route("/admin")
@admin_required
def admin_dashboard():

    conn = get_db()

    users = conn.execute("""
        SELECT id, username, role, last_login
        FROM users
        ORDER BY last_login DESC
    """).fetchall()

    scores = conn.execute("""
        SELECT u.username, q.quiz_name, q.score, q.created_at
        FROM quiz_scores q
        JOIN users u ON q.user_id = u.id
        ORDER BY q.created_at DESC
    """).fetchall()

    conn.close()

    return render_template(
        "admin_dashboard.html",
        users=users,
        scores=scores
    )


# ---------------- USER DASHBOARD ----------------
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


# ---------------- GAME ROUTES ----------------

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
    return render_template("InFINALCARD.html")


# ---------------- QUIZ SAVE ----------------

@app.route("/solarquiz", methods=["GET", "POST"])
@login_required
def solarquiz():

    if request.method == "POST":

        score = request.form.get("score", 0)

        conn = get_db()

        conn.execute("""
            INSERT INTO quiz_scores (user_id, quiz_name, score)
            VALUES (?, ?, ?)
        """, (session["user_id"], "solarquiz", score))

        conn.commit()
        conn.close()

    return render_template("solarquiz.html")


@app.route("/finalquiz", methods=["GET", "POST"])
@login_required
def finalquiz():

    if request.method == "POST":

        score = request.form.get("score", 0)

        conn = get_db()

        conn.execute("""
            INSERT INTO quiz_scores (user_id, quiz_name, score)
            VALUES (?, ?, ?)
        """, (session["user_id"], "finalquiz", score))

        conn.commit()
        conn.close()

    return render_template("IND_FinalQuiz.html")


# ---------------- OTHER PAGES ----------------

@app.route("/solarasteroid")
@login_required
def solarasteroid():
    return render_template("solaraseroid.html")


@app.route("/solarcrush")
@login_required
def solarcrush():
    return render_template("solarcrush.html")


@app.route("/DoYouKnowSpace")
@login_required
def DoYouKnowSpace():
    return render_template("DoYouKnowSpace.html")


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


# ---------------- ERROR ----------------
@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404 - Page Not Found</h1>", 404


# ---------------- MAIN ----------------
if __name__ == "__main__":

    if not os.path.exists(DB_NAME):
        init_db()
        print("Database created")

    app.run(debug=True)
