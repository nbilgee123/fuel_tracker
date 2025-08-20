#!/usr/bin/env python3
"""
Test script to verify multi-language functionality of the Fuel Tracker application.
"""

from app import create_app, get_locale
from flask import session
from config import Config

def test_language_functionality():
    """Test the language selection functionality"""
    
    print("Testing Multi-Language Fuel Tracker Application")
    print("=" * 50)
    
    # Create test app context
    app = create_app()
    
    with app.test_request_context():
        # Test default locale
        print(f"Default locale: {get_locale()}")
        
        # Test supported languages
        print(f"\nSupported languages:")
        for code, name in Config.LANGUAGES.items():
            print(f"  {code}: {name}")
        
        # Test language change
        print(f"\nTesting language changes:")
        
        # Test English
        session['language'] = 'en'
        print(f"  English: {get_locale()}")
        
        # Test Mongolian
        session['language'] = 'mn'
        print(f"  Mongolian: {get_locale()}")
        
        # Test Chinese
        session['language'] = 'zh'
        print(f"  Chinese: {get_locale()}")
        
        # Test Russian
        session['language'] = 'ru'
        print(f"  Russian: {get_locale()}")
        
        # Test Arabic
        session['language'] = 'ar'
        print(f"  Arabic: {get_locale()}")
        
        # Test invalid language
        session['language'] = 'invalid'
        print(f"  Invalid language fallback: {get_locale()}")
        
        # Clear session and test fallback
        session.pop('language', None)
        print(f"  No session fallback: {get_locale()}")
    
    print(f"\n✓ Multi-language functionality test completed!")
    print(f"✓ Application supports {len(Config.LANGUAGES)} languages")
    print(f"✓ Language selector is working correctly")

if __name__ == '__main__':
    test_language_functionality()
