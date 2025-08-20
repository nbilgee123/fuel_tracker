import os
from datetime import timedelta

class Config:
    # Database configuration
    SQLALCHEMY_DATABASE_URI = 'sqlite:///fuel_tracker.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Secret key for forms
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Flask-Babel configuration for internationalization
    BABEL_DEFAULT_LOCALE = 'mn'
    BABEL_DEFAULT_TIMEZONE = 'UTC'
    BABEL_TRANSLATION_DIRECTORIES = 'app/translations'
    LANGUAGES = {
        'mn': 'Монгол'
    }