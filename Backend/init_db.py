import sqlite3
import os

DB = "game_scores.db"

def init_db():
    """Initialize the database with required tables"""
    
    # Remove existing database for fresh setup (optional)
    if os.path.exists(DB):
        os.remove(DB)
    
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    
    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role TEXT DEFAULT 'student',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create games table
    c.execute('''
        CREATE TABLE IF NOT EXISTS games (
            game_id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_name TEXT NOT NULL,
            section TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create scores table
    c.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            score_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            game_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (game_id) REFERENCES games(game_id)
        )
    ''')
    
    # Create progress table (for tracking game progress)
    c.execute('''
        CREATE TABLE IF NOT EXISTS progress (
            progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            game_id INTEGER NOT NULL,
            level INTEGER DEFAULT 1,
            status TEXT DEFAULT 'in_progress',
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (game_id) REFERENCES games(game_id),
            UNIQUE(user_id, game_id)
        )
    ''')
    
    conn.commit()
    print(f"✓ Database '{DB}' initialized successfully")
    
    # Insert sample games (based on frontend files)
    sample_games = [
        ("Asteroid Solar System", "Space", "Explore the solar system with asteroids"),
        ("Candy Crush", "Games", "Classic match-3 puzzle game"),
        ("Do You Know Space?", "Quiz", "Space knowledge quiz"),
        ("Final Maze", "Puzzle", "Navigate through challenging mazes"),
        ("MCQ Quiz", "Quiz", "Multiple choice questions"),
        ("Word Puzzle", "Puzzle", "Solve word puzzles"),
        ("Solar System Quiz", "Quiz", "Test your solar system knowledge")
    ]
    
    for game_name, section, desc in sample_games:
        try:
            c.execute("INSERT INTO games (game_name, section, description) VALUES (?, ?, ?)", 
                     (game_name, section, desc))
        except sqlite3.IntegrityError:
            pass
    
    # Insert sample user
    try:
        c.execute("INSERT INTO users (name, email, role) VALUES (?, ?, ?)", 
                 ("Demo User", "demo@heritage.com", "student"))
    except sqlite3.IntegrityError:
        pass
    
    conn.commit()
    conn.close()
    print("✓ Sample data inserted")

if __name__ == "__main__":
    init_db()
