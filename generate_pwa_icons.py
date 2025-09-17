#!/usr/bin/env python3
"""
PWA icons үүсгэх script
SVG icon-аас янз бүрийн хэмжээтэй PNG icons үүсгэх
"""

import os
from PIL import Image, ImageDraw
import io

def create_pwa_icons():
    """PWA icons үүсгэх"""
    
    # Icons directory үүсгэх
    icons_dir = 'app/static/icons'
    os.makedirs(icons_dir, exist_ok=True)
    
    # Icon sizes
    sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    
    for size in sizes:
        # SVG icon үүсгэх (fuel pump icon)
        svg_content = f'''
        <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">
            <rect width="{size}" height="{size}" fill="#3b82f6" rx="{size//8}"/>
            <g fill="white" transform="translate({size//4}, {size//4})">
                <!-- Fuel pump base -->
                <rect x="{size//8}" y="{size//3}" width="{size//6}" height="{size//3}" rx="2"/>
                <!-- Fuel pump handle -->
                <rect x="{size//8 + size//12}" y="{size//6}" width="{size//24}" height="{size//6}" rx="1"/>
                <!-- Fuel pump nozzle -->
                <rect x="{size//8 + size//12 + size//24}" y="{size//6 + size//12}" width="{size//12}" height="{size//24}" rx="1"/>
                <!-- Fuel drops -->
                <circle cx="{size//8 + size//4}" cy="{size//2}" r="{size//32}"/>
                <circle cx="{size//8 + size//3}" cy="{size//2 + size//16}" r="{size//32}"/>
                <circle cx="{size//8 + size//2.5}" cy="{size//2 - size//16}" r="{size//32}"/>
            </g>
            <!-- Text -->
            <text x="{size//2}" y="{size - size//8}" text-anchor="middle" fill="white" font-family="Arial, sans-serif" font-size="{size//8}" font-weight="bold">⛽</text>
        </svg>
        '''
        
        # PNG file path
        png_path = os.path.join(icons_dir, f'icon-{size}x{size}.png')
        
        # Simple PNG icon үүсгэх (SVG-г PNG болгон хөрвүүлэхгүйгээр)
        img = Image.new('RGBA', (size, size), (59, 130, 246, 255))  # Blue background
        draw = ImageDraw.Draw(img)
        
        # Draw fuel pump icon
        margin = size // 8
        pump_width = size // 4
        pump_height = size // 2
        
        # Fuel pump base
        draw.rectangle([
            (size//2 - pump_width//2, size//2 - pump_height//4),
            (size//2 + pump_width//2, size//2 + pump_height//2)
        ], fill=(255, 255, 255, 255))
        
        # Fuel pump handle
        handle_width = size // 24
        handle_height = size // 6
        draw.rectangle([
            (size//2 - handle_width//2, size//2 - pump_height//2),
            (size//2 + handle_width//2, size//2 - pump_height//2 + handle_height)
        ], fill=(255, 255, 255, 255))
        
        # Fuel pump nozzle
        nozzle_width = size // 12
        nozzle_height = size // 24
        draw.rectangle([
            (size//2 + pump_width//2, size//2 - pump_height//4 + size//16),
            (size//2 + pump_width//2 + nozzle_width, size//2 - pump_height//4 + size//16 + nozzle_height)
        ], fill=(255, 255, 255, 255))
        
        # Fuel drops
        drop_size = size // 32
        draw.ellipse([
            (size//2 + pump_width//2 + size//16, size//2),
            (size//2 + pump_width//2 + size//16 + drop_size*2, size//2 + drop_size*2)
        ], fill=(255, 255, 255, 255))
        
        # Save PNG
        img.save(png_path, 'PNG')
        print(f"✅ Created {png_path}")
    
    # Badge icon үүсгэх
    badge_size = 72
    badge_img = Image.new('RGBA', (badge_size, badge_size), (220, 38, 127, 255))  # Red background
    badge_draw = ImageDraw.Draw(badge_img)
    
    # Draw notification badge
    badge_draw.ellipse([
        (badge_size//4, badge_size//4),
        (badge_size*3//4, badge_size*3//4)
    ], fill=(255, 255, 255, 255))
    
    badge_path = os.path.join(icons_dir, 'badge-72x72.png')
    badge_img.save(badge_path, 'PNG')
    print(f"✅ Created {badge_path}")
    
    # Shortcut icons үүсгэх
    shortcut_icons = [
        ('shortcut-add.png', '➕'),
        ('shortcut-history.png', '📊'),
        ('shortcut-charts.png', '📈')
    ]
    
    for filename, emoji in shortcut_icons:
        shortcut_img = Image.new('RGBA', (96, 96), (59, 130, 246, 255))
        shortcut_draw = ImageDraw.Draw(shortcut_img)
        
        # Draw emoji (simplified as circle)
        shortcut_draw.ellipse([
            (96//4, 96//4),
            (96*3//4, 96*3//4)
        ], fill=(255, 255, 255, 255))
        
        shortcut_path = os.path.join(icons_dir, filename)
        shortcut_img.save(shortcut_path, 'PNG')
        print(f"✅ Created {shortcut_path}")
    
    print("\n🎉 PWA icons амжилттай үүсгэгдлээ!")

if __name__ == '__main__':
    try:
        from PIL import Image, ImageDraw
        create_pwa_icons()
    except ImportError:
        print("❌ PIL (Pillow) суулгах хэрэгтэй:")
        print("pip install Pillow")
        print("\nЭсвэл энгийн icons үүсгэх:")
        create_simple_icons()

def create_simple_icons():
    """PIL байхгүй үед энгийн icons үүсгэх"""
    icons_dir = 'app/static/icons'
    os.makedirs(icons_dir, exist_ok=True)
    
    # Placeholder icons үүсгэх
    sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    
    for size in sizes:
        # Simple HTML file үүсгэх (icon болгон ашиглах)
        html_content = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    width: {size}px;
                    height: {size}px;
                    background: #3b82f6;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: {size//3}px;
                    color: white;
                    font-family: Arial, sans-serif;
                }}
            </style>
        </head>
        <body>⛽</body>
        </html>
        '''
        
        html_path = os.path.join(icons_dir, f'icon-{size}x{size}.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ Created {html_path}")
    
    print("\n⚠️ HTML icons үүсгэгдлээ. PNG icons үүсгэхийн тулд Pillow суулгана уу.")
