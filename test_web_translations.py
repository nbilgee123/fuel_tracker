#!/usr/bin/env python3
"""
Test translations in web request context
"""
from app import create_app, get_locale
from flask import session
from flask_babel import gettext

def test_web_translations():
    print("Testing Translations in Web Request Context")
    print("=" * 50)
    
    app = create_app()
    
    # Simulate a web request with session
    with app.test_request_context('/language/mn'):
        # Set language in session like the web interface does
        session['language'] = 'mn'
        
        print(f"Session language: {session.get('language')}")
        print(f"get_locale() returns: {get_locale()}")
        
        # Test translation
        translated = gettext('Fuel Tracker')
        print(f"Translation of 'Fuel Tracker': '{translated}'")
        
        if translated == 'Fuel Tracker':
            print("❌ Translation failed - still showing English")
        else:
            print("✅ Translation working!")
        
        # Test other languages
        for lang in ['zh', 'ru', 'ar']:
            session['language'] = lang
            current_locale = get_locale()
            translated = gettext('Fuel Tracker')
            print(f"Language '{lang}' -> Locale: {current_locale} -> Text: '{translated}'")

if __name__ == '__main__':
    test_web_translations()
