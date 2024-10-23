from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

login_manager = LoginManager()

class User(UserMixin):
    def __init__(self, id, username, password, is_admin=False, two_factor_secret=None, email=None):
        self.id = id
        self.username = username
        self.password = password
        self.is_admin = is_admin
        self.two_factor_secret = two_factor_secret
        self.email = email

    @staticmethod
    def get(user_id):
        conn = sqlite3.connect('domains.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = c.fetchone()
        conn.close()
        if user:
            return User(user[0], user[1], user[2], user[3], user[4], user[5])
        return None

    @staticmethod
    def get_by_username(username):
        conn = sqlite3.connect('domains.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()
        if user:
            return User(user[0], user[1], user[2], user[3], user[4], user[5])
        return None

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def set_two_factor_secret(self, secret):
        conn = sqlite3.connect('domains.db')
        c = conn.cursor()
        c.execute("UPDATE users SET two_factor_secret = ? WHERE id = ?", (secret, self.id))
        conn.commit()
        conn.close()
        self.two_factor_secret = secret

    @staticmethod
    def create(username, password, email):
        conn = sqlite3.connect('domains.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                      (username, generate_password_hash(password), email))
            conn.commit()
            user_id = c.lastrowid
            conn.close()
            return User(user_id, username, generate_password_hash(password), False, None, email)
        except sqlite3.IntegrityError:
            conn.close()
            return None

def init_auth_db():
    conn = sqlite3.connect('domains.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  is_admin BOOLEAN NOT NULL DEFAULT 0,
                  two_factor_secret TEXT,
                  email TEXT UNIQUE NOT NULL)''')
    conn.commit()
    conn.close()

def add_user(username, password, is_admin=False):
    conn = sqlite3.connect('domains.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
              (username, generate_password_hash(password), is_admin))
    conn.commit()
    conn.close()

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)
