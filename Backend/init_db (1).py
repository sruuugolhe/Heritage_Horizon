"""
Initialize SQLite Database with all required tables and sample data
Run this once to set up your database
"""

import sqlite3
from werkzeug.security import generate_password_hash

DB = "game_scores.db"

def init_database():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # Drop tables if they exist (for fresh start)
    c.execute("DROP TABLE IF EXISTS scores")
    c.execute("DROP TABLE IF EXISTS games")
    c.execute("DROP TABLE IF EXISTS users")

    # CREATE USERS TABLE
    c.execute("""
    CREATE TABLE users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT,
        role TEXT DEFAULT 'student',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # CREATE GAMES TABLE
    c.execute("""
    CREATE TABLE games (
        game_id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_name TEXT NOT NULL,
        game_type TEXT NOT NULL,
        section TEXT NOT NULL,
        max_score INTEGER DEFAULT 100
    )
    """)

    # CREATE SCORES TABLE
    c.execute("""
    CREATE TABLE scores (
        score_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        game_id INTEGER NOT NULL,
        score INTEGER NOT NULL,
        level INTEGER DEFAULT 1,
        completion_time INTEGER,
        date_completed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(user_id),
        FOREIGN KEY(game_id) REFERENCES games(game_id)
    )
    """)

    # INSERT SAMPLE USERS
    users = [
        ("John Doe", "john@example.com", "password123", "student"),
        ("Jane Smith", "jane@example.com", "password123", "student"),
        ("Admin User", "admin@example.com", "admin123", "admin"),
    ]

    for name, email, password, role in users:
        hashed_password = generate_password_hash(password)
        c.execute(
            "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
            (name, email, hashed_password, role)
        )

    # INSERT GAMES (based on your frontend files)
    games = [
        ("MCQ Quiz", "quiz", "Knowledge Assessment", 100),
        ("Final Maze", "maze", "Spatial Reasoning", 100),
        ("Word Puzzle", "puzzle", "Vocabulary", 100),
        ("Do You Know Space", "trivia", "Space Knowledge", 100),
        ("Slide Show", "presentation", "Learning Materials", 0),
    ]

    for game_name, game_type, section, max_score in games:
        c.execute(
            "INSERT INTO games (game_name, game_type, section, max_score) VALUES (?, ?, ?, ?)",
            (game_name, game_type, section, max_score)
        )

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")
    print("📊 Tables created: users, games, scores")
    print("👥 Sample users created")
    print("🎮 Sample games registered")

if __name__ == "__main__":
    init_database()
    # Add functions to:
# - create user
# - validate login
# - save game score
# - fetch user scores
# Use SQLite and game_scores.db

