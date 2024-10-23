from flask_login import login_user
from werkzeug.security import check_password_hash
from src.models import User

def load_user(user_id):
    return User.query.get(int(user_id))

def login_user_func(username, password):
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        login_user(user)
        return True
    return False
