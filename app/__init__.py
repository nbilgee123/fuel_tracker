from flask import Flask, request, session
from flask_babel import Babel, gettext
from config import Config
from flask_migrate import Migrate
from flask_login import LoginManager

# Import db from models to avoid circular imports
from app.models import db

babel = Babel()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'main.login'

def get_locale():
    # Force Mongolian locale for the entire application
    return 'mn'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    # Ensure session permanence
    app.config.setdefault('SESSION_PERMANENT', True)
    
    # FIX: Set locale selector BEFORE initializing Babel
    babel.locale_selector = get_locale
    
    # Initialize extensions
    db.init_app(app)
    babel.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Make functions available in templates
    app.jinja_env.globals['get_locale'] = get_locale
    app.jinja_env.globals['config'] = app.config
    app.jinja_env.globals['_'] = gettext

    
    # Import and register routes
    from app.routes import main
    app.register_blueprint(main)
    
    # Import models AFTER db is initialized to avoid circular imports
    from app import models
    
    # Import commands
    from app.commands import init_app
    init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))
    
    return app