import sqlite3
import os
from werkzeug.security import generate_password_hash

DB = "game_scores.db"

def init_db():

    # Delete old DB for fresh start
    if os.path.exists(DB):
        os.remove(DB)

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # ================= USERS =================
    c.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'student',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ================= GAMES =================
    c.execute("""
        CREATE TABLE games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_name TEXT UNIQUE NOT NULL,
            section TEXT NOT NULL,
            description TEXT
        )
    """)

    # ================= SCORES =================
    c.execute("""
        CREATE TABLE scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            game_id INTEGER,
            score INTEGER,
            played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(game_id) REFERENCES games(id)
        )
    """)

    # ================= PROGRESS =================
    c.execute("""
        CREATE TABLE progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            game_id INTEGER,
            level INTEGER DEFAULT 1,
            status TEXT DEFAULT 'in_progress',
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            UNIQUE(user_id, game_id),
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(game_id) REFERENCES games(id)
        )
    """)

    # ================= QUIZ SCORES =================
    c.execute("""
        CREATE TABLE quiz_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            quiz_name TEXT,
            score INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ================= DEMO USER =================
    demo_password = generate_password_hash("1234")

    c.execute("""
        INSERT INTO users (username, password)
        VALUES (?, ?)
    """, ("demo", demo_password))


    # ================= SAMPLE GAMES =================
    games = [
        ("Asteroid Solar System", "Space", "Explore the solar system"),
        ("Candy Crush", "Games", "Match 3 puzzle"),
        ("Do You Know Space", "Quiz", "Space quiz"),
        ("Final Maze", "Puzzle", "Maze game"),
        ("Solar Quiz", "Quiz", "Solar system quiz"),
        ("Word Puzzle", "Puzzle", "Word game"),
        ("Solar Crush", "Games", "Arcade game")
    ]

    for game in games:
        try:
            c.execute("""
                INSERT INTO games (game_name, section, description)
                VALUES (?, ?, ?)
            """, game)
        except:
            pass


    conn.commit()
    conn.close()

    print("✅ Database created successfully")
    print("👉 Login: demo / 1234")


if __name__ == "__main__":
    init_db()
