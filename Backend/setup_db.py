import sqlite3

conn = sqlite3.connect('game_scores.db')
c = conn.cursor()

# Users
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    role TEXT NOT NULL
)
''')

# Games
c.execute('''
CREATE TABLE IF NOT EXISTS games (
    game_id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_name TEXT UNIQUE NOT NULL,
    section TEXT NOT NULL
)
''')

# Scores
c.execute('''
CREATE TABLE IF NOT EXISTS scores (
    score_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    game_id INTEGER NOT NULL,
    score INTEGER NOT NULL,
    date_played DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(game_id) REFERENCES games(game_id)
)
''')

games = [
    ('Heritage Quiz', 'heritage'),
    ('Word Puzzle', 'heritage'),
    ('Memory Game', 'heritage'),
    ('Maze Puzzle', 'heritage'),
    ('Universe Quiz', 'universe'),
    ('Word Puzzle 2', 'universe'),
    ('Asteroids Dodge', 'universe'),
    ('Solar Crush', 'universe')
]

c.executemany(
    'INSERT OR IGNORE INTO games (game_name, section) VALUES (?, ?)',
    games
)

conn.commit()
conn.close()

print("Database setup complete!")
