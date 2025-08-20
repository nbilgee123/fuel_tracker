#!/usr/bin/env python3
"""
Comprehensive debug script for Flask-Babel
"""
import os
from flask import Flask
from flask_babel import Babel, gettext

def debug_babel():
    print("Debugging Flask-Babel Configuration")
    print("=" * 50)
    
    # Create a minimal Flask app
    app = Flask(__name__)
    
    # Set Babel configuration
    app.config['BABEL_DEFAULT_LOCALE'] = 'mn'
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'app/translations'
    app.config['SECRET_KEY'] = 'test'
    
    print(f"Babel config: {app.config['BABEL_TRANSLATION_DIRECTORIES']}")
    print(f"Default locale: {app.config['BABEL_DEFAULT_LOCALE']}")
    
    # Check if translation directory exists
    trans_dir = os.path.join(os.getcwd(), 'app', 'translations')
    print(f"Translation directory: {trans_dir}")
    print(f"Directory exists: {os.path.exists(trans_dir)}")
    
    # Check .mo files
    for lang in ['en', 'mn', 'zh', 'ru', 'ar']:
        mo_file = os.path.join(trans_dir, lang, 'LC_MESSAGES', 'messages.mo')
        if os.path.exists(mo_file):
            size = os.path.getsize(mo_file)
            print(f"✓ {lang}: {mo_file} ({size} bytes)")
        else:
            print(f"✗ {lang}: {mo_file} MISSING")
    
    # Initialize Babel
    babel = Babel()
    babel.init_app(app)
    
    # Test locale selector
    def test_locale():
        return 'mn'
    
    babel.localeselector(test_locale)
    
    print("\n" + "=" * 50)
    print("Testing translations...")
    
    with app.app_context():
        try:
            # Try to get a translated string
            translated = gettext('Fuel Tracker')
            print(f"Translation of 'Fuel Tracker': '{translated}'")
            
            if translated == 'Fuel Tracker':
                print("❌ Translation failed - still showing English")
                
                # Try to force locale
                from flask_babel import refresh
                refresh()
                
                translated2 = gettext('Fuel Tracker')
                print(f"After refresh: '{translated2}'")
                
            else:
                print("✅ Translation working!")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    debug_babel()
