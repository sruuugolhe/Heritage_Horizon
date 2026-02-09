from flask import Flask, render_template, request, redirect, session, abort
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os

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
        role TEXT DEFAULT 'user'
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


# ---------------- HOME ----------------

@app.route("/")
def home():
    return redirect("/login")


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

# ---------------- FORGOT ----------------

@app.route("/forgot", methods=["GET", "POST"])
def forgot():

    if request.method == "POST":

        username = request.form["username"]
        new_pass = request.form["password"]

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()

        if user:

            conn.execute(
                "UPDATE users SET password=? WHERE username=?",
                (generate_password_hash(new_pass), username)
            )

            conn.commit()
            conn.close()

            return redirect("/login")

        conn.close()

        return render_template(
            "forgotaccount.html",
            error="User not found"
        )

    return render_template("forgotaccount.html")


# ---------------- USER PAGE ----------------

@app.route("/slide")
@login_required
def slide():
    return render_template("slide2.html")


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


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# ---------------- MAIN ----------------

if __name__ == "__main__":

    init_db()
    create_admin()   # 👈 ADD THIS

    app.run(debug=True)
