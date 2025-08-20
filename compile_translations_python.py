#!/usr/bin/env python3
"""
Python script to compile translations directly without pybabel command line tool.
"""
import os
import polib
from babel.messages.pofile import read_po
from babel.messages.mofile import write_mo

def compile_translations():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    translations_dir = os.path.join(base_dir, 'app', 'translations')
    languages = ['en', 'mn', 'zh', 'ru', 'ar']

    for lang in languages:
        po_file = os.path.join(translations_dir, lang, 'LC_MESSAGES', 'messages.po')
        mo_file = os.path.join(translations_dir, lang, 'LC_MESSAGES', 'messages.mo')
        
        if os.path.exists(po_file):
            try:
                # Read the .po file
                with open(po_file, 'r', encoding='utf-8') as f:
                    catalog = read_po(f, locale=lang)
                
                # Write the .mo file
                with open(mo_file, 'wb') as f:
                    write_mo(f, catalog)
                
                print(f"✓ Successfully compiled {lang} translations")
            except Exception as e:
                print(f"✗ Error compiling {lang} translations: {e}")
        else:
            print(f"⚠ No .po file found for {lang}")
    
    print("\nTranslation compilation completed!")

if __name__ == '__main__':
    compile_translations()
