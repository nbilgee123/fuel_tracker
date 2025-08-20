#!/usr/bin/env python3
"""
Test script to debug translation issues
"""
import os
from flask_babel import Babel, gettext
from flask import Flask, session

def test_translations():
    print("Testing Translation System")
    print("=" * 40)
    
    # Check if .mo files exist and their sizes
    translations_dir = 'app/translations'
    languages = ['en', 'mn', 'zh', 'ru', 'ar']
    
    for lang in languages:
        mo_file = os.path.join(translations_dir, lang, 'LC_MESSAGES', 'messages.mo')
        po_file = os.path.join(translations_dir, lang, 'LC_MESSAGES', 'messages.po')
        
        if os.path.exists(mo_file):
            size = os.path.getsize(mo_file)
            print(f"✓ {lang}: .mo file exists ({size} bytes)")
        else:
            print(f"✗ {lang}: .mo file MISSING")
            
        if os.path.exists(po_file):
            size = os.path.getsize(po_file)
            print(f"  {lang}: .po file exists ({size} bytes)")
        else:
            print(f"  {lang}: .po file MISSING")
    
    print("\n" + "=" * 40)
    
    # Test if Flask-Babel can actually load translations
    try:
        app = Flask(__name__)
        app.config['BABEL_DEFAULT_LOCALE'] = 'mn'
        app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'app/translations'
        
        babel = Babel()
        babel.init_app(app)
        
        with app.app_context():
            # Try to get a translated string
            translated = gettext('Fuel Tracker')
            print(f"Test translation 'Fuel Tracker' → '{translated}'")
            
            if translated == 'Fuel Tracker':
                print("❌ Translation failed - still showing English")
            else:
                print("✅ Translation working!")
                
    except Exception as e:
        print(f"❌ Error testing Flask-Babel: {e}")

if __name__ == '__main__':
    test_translations()
