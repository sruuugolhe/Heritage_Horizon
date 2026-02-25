from flask import Flask, render_template, request, redirect, session, abort, url_for, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
import random
from datetime import datetime, timedelta

# ---------------- Helper ----------------
def get_ist_time():
    """Return current India Standard Time as datetime object"""
    return datetime.utcnow() + timedelta(hours=5, minutes=30)

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





@app.route("/mystery_reward")
@login_required
def mystery_reward():

    import random

    rewards = [10, 20, 50, 0, 100, 30]
    reward = random.choice(rewards)

    conn = get_db()
    conn.execute(
        "UPDATE users SET coins = coins + ? WHERE id = ?",
        (reward, session['user_id'])
    )
    conn.commit()
    conn.close()

    return {"reward": reward}
# ---------------- DASHBOARD ----------------

@app.route('/dashboard')
@login_required
def dashboard():

    conn = get_db()

    # Get user basic info INCLUDING login_streak
    user = conn.execute(
        "SELECT username, coins, level, login_streak FROM users WHERE id=?",
        (session['user_id'],)
    ).fetchone()

    # Total games played
    total_games_played = conn.execute(
        "SELECT COUNT(*) FROM scores WHERE user_id=?",
        (session['user_id'],)
    ).fetchone()[0]

    # Total score
    total_score = conn.execute(
        "SELECT SUM(score) FROM scores WHERE user_id=?",
        (session['user_id'],)
    ).fetchone()[0]

    if total_score is None:
        total_score = 0

    # =============================
    # LEVEL SYSTEM (1 to 12)
    # =============================
    level = (total_score // 500) + 1

    if level > 12:
        level = 12

    # =============================
    # BADGE SYSTEM
    # =============================
    if level <= 3:
        badge = "🥉 Beginner"
    elif level <= 6:
        badge = "🥈 Explorer"
    elif level <= 9:
        badge = "🥇 Master"
    else:
        badge = "👑 Legend"

    # Update level in database
    conn.execute(
        "UPDATE users SET level=? WHERE id=?",
        (level, session['user_id'])
    )
    conn.commit()

    conn.close()

    return render_template(
        "dashboard.html",
        user=user,
        total_score=total_score,
        total_games_played=total_games_played,
        login_streak=user["login_streak"],
        level=level,
        badge=badge
    )
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
            session["username"] = user["username"]

            conn = get_db()

            # Get streak data
            streak_data = conn.execute(
                "SELECT login_streak, last_streak_date FROM users WHERE id=?",
                (user["id"],)
            ).fetchone()

            current_streak = streak_data["login_streak"] or 0
            last_date = streak_data["last_streak_date"]

            today = datetime.now().date()
            reward_message = ""

            if last_date:
                last_login_date = datetime.strptime(last_date, "%Y-%m-%d").date()
                difference = (today - last_login_date).days

                if difference == 1:
                    current_streak += 1

                elif difference > 1:
                    current_streak = 1

                elif difference == 0:
                    session["reward_message"] = ""

                    conn.close()

                    if user["role"] == "admin":
                        return redirect("/admin")
                    return redirect("/slide")
            else:
                current_streak = 1

            # 🎯 Check 7th day bonus
            if current_streak == 7:
                conn.execute(
                    "UPDATE users SET coins = coins + 50 WHERE id=?",
                    (user["id"],)
                )
                reward_message = "🔥 7-Day Streak Completed! +50 Coins!"
                current_streak = 0
            else:
                reward_message = f"🔥 Streak Day {current_streak}/7"

            # Update streak + last login
            conn.execute(
                "UPDATE users SET login_streak=?, last_streak_date=?, last_login=? WHERE id=?",
                (
                    current_streak,
                    today.strftime("%Y-%m-%d"),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    user["id"]
                )
            )

            conn.commit()
            conn.close()

            session["reward_message"] = reward_message

            if user["role"] == "admin":
                return redirect("/admin")

            return redirect("/slide")

        return render_template("FSLOGIN.html", error="Invalid Login")

    return render_template("FSLOGIN.html")


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("titlepage"))

# ---------------- COMPLETE GAME ----------------

@app.route("/update_score", methods=["POST"])
@login_required
def update_score():
    data = request.get_json()
    score = int(data.get("score", 0))
    attempt_id = data.get("attempt_id") or session.get("attempt_id")

    if not attempt_id:
        return jsonify({"error": "No active game"}), 400

    ist_time = get_ist_time().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db()
    conn.execute("""
        UPDATE scores
        SET score=?, played_at=?
        WHERE id=?
    """, (score, ist_time, attempt_id))
    conn.commit()
    conn.close()

    return jsonify({"message": "Score updated", "score": score})

 #      start game
@app.route("/start_game", methods=["POST"])
@login_required
def start_game():
    game_name = request.form.get("game_name")
    conn = get_db()

    # Get game_id
    game = conn.execute("SELECT id FROM games WHERE game_name=?", (game_name,)).fetchone()
    if not game:
        conn.close()
        return "Game not found", 404

    # IST timestamp
    ist_time = get_ist_time().strftime("%Y-%m-%d %H:%M:%S")

    # Insert score
    cursor = conn.execute("""
        INSERT INTO scores (user_id, game_id, score, status, played_at)
        VALUES (?, ?, 0, 'incomplete', ?)
    """, (session["user_id"], game["id"], ist_time))

    conn.commit()
    attempt_id = cursor.lastrowid
    session["attempt_id"] = attempt_id
    conn.close()

    # Return attempt_id to JS
    return str(attempt_id)

# finish game
@app.route("/finish_game", methods=["POST"])
@login_required
def finish_game():
    attempt_id = session.get("attempt_id")
    if not attempt_id:
        return jsonify({"error": "No active game"}), 400

    ist_time = get_ist_time().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db()
    conn.execute("""
        UPDATE scores
        SET status='completed', played_at=?
        WHERE id=?
    """, (ist_time, attempt_id))
    conn.commit()
    conn.close()

    session.pop("attempt_id", None)  # clear session
    return jsonify({"message": "Game finished"})
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

    users = conn.execute("""
        SELECT id, username, role, last_login
        FROM users
        ORDER BY id DESC
    """).fetchall()

    scores = conn.execute("""
    SELECT u.username, g.game_name, g.section, s.score, s.played_at
    FROM scores s
    JOIN users u ON s.user_id = u.id
    JOIN games g ON s.game_id = g.id
    ORDER BY s.played_at DESC
""").fetchall()


    conn.close()

    return render_template(
        "admin_dashboard.html",
        users=users,
        scores=scores
    )


# ---------------- FORGOT / RESET PASSWORD ----------------

@app.route("/forgot", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        username = request.form.get("username")
        new_password = request.form.get("password")

        conn = get_db()
        user = conn.execute(
            "SELECT id FROM users WHERE username=?",
            (username,)
        ).fetchone()

        if user:
            # Hash the new password
            hashed = generate_password_hash(new_password)

            # Update password in database
            conn.execute(
                "UPDATE users SET password=? WHERE id=?",
                (hashed, user["id"])
            )
            conn.commit()
            conn.close()

            # Success message via query param or redirect to login
            return redirect("/login")
        else:
            conn.close()
            return render_template("forgotaccount.html", error="Username not found")

    return render_template("forgotaccount.html")

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
   
    create_admin()
    app.run(debug=True)
