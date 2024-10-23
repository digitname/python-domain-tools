from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    two_factor_secret = db.Column(db.String(16))
    is_admin = db.Column(db.Boolean, default=False)
    domains = db.relationship('Domain', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def set_two_factor_secret(self, secret):
        self.two_factor_secret = secret

    @classmethod
    def create(cls, username, password, email):
        user = cls(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

class Domain(db.Model):
    __tablename__ = 'domains'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    hashtags = Column(String(255), default='')
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    history = relationship('DomainHistory', backref='domain', lazy='dynamic')

class DomainHistory(db.Model):
    __tablename__ = 'domain_history'

    id = Column(Integer, primary_key=True)
    domain_id = Column(Integer, ForeignKey('domains.id'), nullable=False)
    whois_data = Column(JSON, nullable=False)
    nameservers = Column(JSON, nullable=False)
    created_at = Column(DateTime, nullable=False)
