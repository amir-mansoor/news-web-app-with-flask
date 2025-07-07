import sqlite3
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app

class User(UserMixin):
    def __init__(self, id,username,email,role):
        self.id = id
        self.username = username
        self.email = email
        self.role = role

# 🔧 Initialize DB (run once at app startup)
def init_db(app):
    with app.app_context():
        conn = sqlite3.connect(app.config['DATABASE'])
        c = conn.cursor()

        # Users table
        c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        );
    ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            image TEXT,
            author_id INTEGER,
            category_id INTEGER,
            view_count INTEGER DEFAULT 0,
            FOREIGN KEY(author_id) REFERENCES users(id),
            FOREIGN KEY(category_id) REFERENCES categories(id)
        )   
        ''')

        # Comments table
        c.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT,
            created_at TEXT,
            user_id INTEGER,
            news_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(news_id) REFERENCES news(id)
        )
        ''')


        # Likes table
        c.execute('''
        CREATE TABLE IF NOT EXISTS likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            news_id INTEGER,
            UNIQUE(user_id, news_id),
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(news_id) REFERENCES news(id)
        )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
        ''')
        conn.commit()
        conn.close()

def load_user(user_id):
    conn = sqlite3.connect(current_app.config['DATABASE'])
    c = conn.cursor()
    c.execute("SELECT id, username,email, role FROM users WHERE id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return User(*row)
    return None

def create_user(username, email,password, role='user'):
    hashed_pw = generate_password_hash(password)
    conn = sqlite3.connect(current_app.config['DATABASE'])
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username,email, password, role) VALUES (?, ?, ?,?)", (username,email, hashed_pw, role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def validate_user(email, password):
    conn = sqlite3.connect(current_app.config['DATABASE'])
    c = conn.cursor()
    c.execute("SELECT id,username, email, password, role FROM users WHERE email = ?", (email,))
    row = c.fetchone()

    conn.close()
    if row and check_password_hash(row[3], password):
        return User(row[0], row[1], row[2], row[4])
    return None