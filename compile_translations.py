#!/usr/bin/env python3
"""
Script to compile translation files for the Fuel Tracker application.
This script compiles .po files to .mo files for all supported languages.
"""

import os
import subprocess
import sys

def compile_translations():
    """Compile all translation files from .po to .mo format"""
    
    # Get the directory where this script is located
    base_dir = os.path.dirname(os.path.abspath(__file__))
    translations_dir = os.path.join(base_dir, 'app', 'translations')
    
    if not os.path.exists(translations_dir):
        print("Translations directory not found. Please run the application first to create it.")
        return
    
    # Languages to compile
    languages = ['en', 'mn', 'zh', 'ru', 'ar']
    
    for lang in languages:
        lang_dir = os.path.join(translations_dir, lang, 'LC_MESSAGES')
        po_file = os.path.join(lang_dir, 'messages.po')
        mo_file = os.path.join(lang_dir, 'messages.mo')
        
        if os.path.exists(po_file):
            try:
                # Compile .po to .mo using pybabel
                cmd = [
                    'pybabel', 'compile',
                    '-d', translations_dir,
                    '-l', lang
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=base_dir)
                
                if result.returncode == 0:
                    print(f"✓ Successfully compiled {lang} translations")
                else:
                    print(f"✗ Error compiling {lang} translations:")
                    print(f"  {result.stderr}")
                    
            except Exception as e:
                print(f"✗ Error compiling {lang} translations: {e}")
        else:
            print(f"⚠ No .po file found for {lang}")
    
    print("\nTranslation compilation completed!")

if __name__ == '__main__':
    compile_translations()
