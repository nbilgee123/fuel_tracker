#!/usr/bin/env python3
"""
Энгийн PWA icons үүсгэх script
"""

import os

def create_simple_icons():
    """Энгийн PWA icons үүсгэх"""
    
    # Icons directory үүсгэх
    icons_dir = 'app/static/icons'
    os.makedirs(icons_dir, exist_ok=True)
    
    # Icon sizes
    sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    
    for size in sizes:
        # Simple SVG icon үүсгэх
        svg_content = f'''<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">
<rect width="{size}" height="{size}" fill="#3b82f6" rx="{size//8}"/>
<text x="{size//2}" y="{size//2 + size//8}" text-anchor="middle" fill="white" font-family="Arial, sans-serif" font-size="{size//3}" font-weight="bold">⛽</text>
</svg>'''
        
        svg_path = os.path.join(icons_dir, f'icon-{size}x{size}.svg')
        with open(svg_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        print(f"✅ Created {svg_path}")
    
    # Badge icon үүсгэх
    badge_svg = '''<svg width="72" height="72" viewBox="0 0 72 72" xmlns="http://www.w3.org/2000/svg">
<circle cx="36" cy="36" r="36" fill="#dc2626"/>
<text x="36" y="42" text-anchor="middle" fill="white" font-family="Arial, sans-serif" font-size="24" font-weight="bold">!</text>
</svg>'''
    
    badge_path = os.path.join(icons_dir, 'badge-72x72.svg')
    with open(badge_path, 'w', encoding='utf-8') as f:
        f.write(badge_svg)
    print(f"✅ Created {badge_path}")
    
    # Shortcut icons үүсгэх
    shortcuts = [
        ('shortcut-add.svg', '➕'),
        ('shortcut-history.svg', '📊'),
        ('shortcut-charts.svg', '📈')
    ]
    
    for filename, emoji in shortcuts:
        shortcut_svg = f'''<svg width="96" height="96" viewBox="0 0 96 96" xmlns="http://www.w3.org/2000/svg">
<rect width="96" height="96" fill="#3b82f6" rx="12"/>
<text x="48" y="56" text-anchor="middle" fill="white" font-family="Arial, sans-serif" font-size="32">{emoji}</text>
</svg>'''
        
        shortcut_path = os.path.join(icons_dir, filename)
        with open(shortcut_path, 'w', encoding='utf-8') as f:
            f.write(shortcut_svg)
        print(f"✅ Created {shortcut_path}")
    
    print("\n🎉 PWA icons амжилттай үүсгэгдлээ!")
    print("📝 SVG icons үүсгэгдлээ. Production дээр PNG болгон хөрвүүлэх хэрэгтэй.")

if __name__ == '__main__':
    create_simple_icons()
