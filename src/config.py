class Config:
    SECRET_KEY = 'your_secret_key_here'  # Change this to a secure random key
    SQLALCHEMY_DATABASE_URI = 'sqlite:///domains.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Add other configuration variables here
