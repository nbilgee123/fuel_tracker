#!/usr/bin/env python3
"""
Debug script to test locale selector and session handling
"""
from app import create_app, get_locale
from flask import session
from config import Config

def debug_locale():
    print("Debugging Locale Selector")
    print("=" * 40)
    
    app = create_app()
    
    with app.test_request_context():
        print(f"Default locale: {get_locale()}")
        print(f"Session contents: {dict(session)}")
        
        # Test setting language in session
        session['language'] = 'mn'
        print(f"After setting session['language'] = 'mn': {get_locale()}")
        
        # Test with different languages
        for lang in ['zh', 'ru', 'ar']:
            session['language'] = lang
            print(f"Session language '{lang}': get_locale() returns '{get_locale()}'")
        
        # Test clearing session
        session.pop('language', None)
        print(f"After clearing session: {get_locale()}")
        
        print("\n" + "=" * 40)
        print("Testing Flask-Babel integration...")
        
        # Test if Flask-Babel is actually using our locale selector
        from flask_babel import gettext
        
        # Set language and test translation
        session['language'] = 'mn'
        current_locale = get_locale()
        print(f"Current locale: {current_locale}")
        
        # Try to get a translated string
        translated = gettext('Fuel Tracker')
        print(f"Translation of 'Fuel Tracker': '{translated}'")
        
        if translated == 'Fuel Tracker':
            print("❌ Translation failed - Flask-Babel not using our locale selector")
        else:
            print("✅ Translation working with locale selector!")

if __name__ == '__main__':
    debug_locale()
