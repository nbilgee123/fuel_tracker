#!/usr/bin/env python3
"""
Test translations within the actual Flask app
"""
from app import create_app, get_locale
from flask import session
from flask_babel import gettext

def test_app_translations():
    print("Testing Translations in Actual Flask App")
    print("=" * 50)
    
    app = create_app()
    
    with app.test_request_context():
        # Test locale selector
        print(f"Default locale: {get_locale()}")
        
        # Test setting language in session
        session['language'] = 'mn'
        print(f"After setting session['language'] = 'mn': {get_locale()}")
        
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
    test_app_translations()
