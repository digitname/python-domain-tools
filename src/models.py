from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from auth import login_manager

db = SQLAlchemy()

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

class Domain(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    hashtags = db.Column(db.String(255))

    user = db.relationship('User', backref=db.backref('domains', lazy=True))

    def __repr__(self):
        return f'<Domain {self.name}>'


def init_auth_db():
    # This function is no longer needed with SQLAlchemy
    pass

def add_user(username, password, email, is_admin=False):
    new_user = User(username=username, email=email, is_admin=is_admin)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return new_user

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))