#!/usr/bin/env python3
"""
Debug Flask app configuration for Flask-Babel
"""
import os
from app import create_app
from flask_babel import gettext

def debug_app_config():
    print("Debugging Flask App Configuration")
    print("=" * 50)
    
    app = create_app()
    
    print(f"App config BABEL_TRANSLATION_DIRECTORIES: {app.config.get('BABEL_TRANSLATION_DIRECTORIES')}")
    print(f"App config BABEL_DEFAULT_LOCALE: {app.config.get('BABEL_DEFAULT_LOCALE')}")
    
    # Check if translation directory exists from app perspective
    trans_dir = app.config.get('BABEL_TRANSLATION_DIRECTORIES')
    if trans_dir:
        full_path = os.path.join(os.getcwd(), trans_dir)
        print(f"Full translation path: {full_path}")
        print(f"Directory exists: {os.path.exists(full_path)}")
        
        # Check .mo files
        for lang in ['en', 'mn', 'zh', 'ru', 'ar']:
            mo_file = os.path.join(full_path, lang, 'LC_MESSAGES', 'messages.mo')
            if os.path.exists(mo_file):
                size = os.path.getsize(mo_file)
                print(f"✓ {lang}: {mo_file} ({size} bytes)")
            else:
                print(f"✗ {lang}: {mo_file} MISSING")
    
    print("\n" + "=" * 50)
    print("Testing with app context...")
    
    with app.app_context():
        from flask_babel import get_locale
        try:
            # Try to get current locale
            current_locale = get_locale()
            print(f"Current Babel locale: {current_locale}")
            
            # Try to get a translated string
            translated = gettext('Fuel Tracker')
            print(f"Translation of 'Fuel Tracker': '{translated}'")
            
            if translated == 'Fuel Tracker':
                print("❌ Translation failed - still showing English")
            else:
                print("✅ Translation working!")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    debug_app_config()
