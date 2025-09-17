import os
from datetime import timedelta

class Config:
    # Paths
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    INSTANCE_DIR = os.path.join(BASEDIR, 'instance')

    # Ensure instance dir exists (safe if it already exists)
    try:
        os.makedirs(INSTANCE_DIR, exist_ok=True)
    except Exception:
        pass

    # Database configuration
    # PostgreSQL (production) эсвэл SQLite (development)
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        # PostgreSQL (Render.com дээр)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # SQLite (local development)
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(INSTANCE_DIR, 'fuel_tracker.db')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Secret key for forms
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Session/remember-me configuration
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    SESSION_PERMANENT = True

    # Flask-Babel configuration for internationalization
    BABEL_DEFAULT_LOCALE = 'mn'
    BABEL_DEFAULT_TIMEZONE = 'UTC'
    BABEL_TRANSLATION_DIRECTORIES = 'app/translations'
    LANGUAGES = {
        'mn': 'Монгол'
    }