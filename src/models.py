from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    is_admin = Column(Boolean, default=False)

    domains = relationship("Domain", backref="owner", lazy="dynamic")

class Domain(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    user_id = Column(Integer, db.ForeignKey("user.id"), nullable=False)
