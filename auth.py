from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

login_manager = LoginManager()

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    @staticmethod
    def get(user_id):
        conn = sqlite3.connect('domains.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = c.fetchone()
        conn.close()
        if user:
            return User(user[0], user[1], user[2])
        return None

def init_auth_db():
    conn = sqlite3.connect('domains.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL)''')
    conn.commit()
    conn.close()

def add_user(username, password):
    conn = sqlite3.connect('domains.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
              (username, generate_password_hash(password)))
    conn.commit()
    conn.close()

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)
