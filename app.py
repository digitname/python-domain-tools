from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, login_required, logout_user, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail
from flask_caching import Cache
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
import csv
import io
import openpyxl

from src.models import db, User, Domain
from src.auth import load_user, login_user_func
from src.domain_utils import extract_domains, validate_domain, categorize_domain, add_custom_rule, remove_custom_rule, custom_rules, load_custom_rules
from src.config import Config
from src.routes import register_routes
from src.utils import generate_excel, generate_csv

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.user_loader(load_user)

limiter = Limiter(app, key_func=get_remote_address)
mail = Mail(app)
cache = Cache(app)

register_routes(app)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
