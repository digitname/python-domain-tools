from flask import Flask
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail
from flask_caching import Cache
from flask_migrate import Migrate
import logging
import socket

from models import db, User, Domain
from domain_utils import extract_domains, validate_domain, categorize_domain, add_custom_rule, remove_custom_rule, load_custom_rules
import api_routes
import app_routes
# from api import register_api_routes
from auth import login_manager, load_user

def find_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    port = s.getsockname()[1]
    print(port)
    s.close()
    return port

def create_app():
    app = Flask(__name__, template_folder='../templates')
    app.secret_key = 'your_secret_key_here'  # Change this to a secure random key
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///domains.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Email configuration
    app.config['MAIL_SERVER'] = 'smtp.example.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'your_email@example.com'
    app.config['MAIL_PASSWORD'] = 'your_email_password'
    app.config['MAIL_DEFAULT_SENDER'] = 'your_email@example.com'

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.user_loader(load_user)  # Register the load_user function with the login_manager
    migrate = Migrate(app, db)
    mail = Mail(app)
    cache = Cache(app, config={'CACHE_TYPE': 'simple'})
    limiter = Limiter(app, key_func=get_remote_address)

    # Set up logging
    logging.basicConfig(filename='app.log', level=logging.INFO)

    # Register routes
    app_routes.register_routes(app, mail, cache, limiter)
    api_routes.register_routes(app, mail, cache, limiter)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    #port = find_free_port()
    port = 5001
    app.run(debug=True, port=port)
