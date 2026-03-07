import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///insurance_fraud.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False