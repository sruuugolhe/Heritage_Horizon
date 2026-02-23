import sqlite3
from werkzeug.security import generate_password_hash

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE_DIR, "game_scores.db")

def init_db():

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # ================= USERS =================
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'student',
        coins INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1,
        last_login TEXT,
        last_spin TEXT
    )
    """)

    # ================= ADMIN USER =================
    admin_pass = generate_password_hash("admin123")

    c.execute("""
    INSERT OR IGNORE INTO users (username, password, role)
    VALUES (?, ?, ?)
    """, ("admin", admin_pass, "admin"))

    # ================= GAMES =================
    c.execute("""
    CREATE TABLE IF NOT EXISTS games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_name TEXT UNIQUE NOT NULL,
        section TEXT NOT NULL,
        description TEXT
    )
    """)

    games_list = [
        ("Heritage Quiz", "Heritage", "Quiz about Indian heritage"),
        ("Heritage Maze", "Heritage", "Maze challenge"),
        ("Heritage Word Puzzle", "Heritage", "Word game"),
        ("Heritage Cards", "Heritage", "Memory cards"),
        ("Solar Quiz", "Solar", "Quiz about space"),
        ("Solar Puzzle", "Solar", "Word puzzle"),
        ("Solar Crush", "Solar", "Match game"),
        ("Solar Asteriod", "Solar", "Asteroid dodging game")
    ]

    for g in games_list:
        c.execute("""
            INSERT OR IGNORE INTO games (game_name, section, description)
            VALUES (?, ?, ?)
        """, g)

    # ================= SCORES =================
    c.execute("""
    CREATE TABLE IF NOT EXISTS scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        game_id INTEGER,
        score INTEGER,
        played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(game_id) REFERENCES games(id)
    )
    """)

    conn.commit()
    conn.close()

    print("✅ Database created successfully")
    print("👉 Admin login: admin / admin123")


if __name__ == "__main__":
    init_db()
