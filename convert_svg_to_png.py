#!/usr/bin/env python3
"""
SVG icons-г PNG болгон хөрвүүлэх script
Pillow ашиглахгүйгээр энгийн PNG үүсгэх
"""

import os
import base64

def create_png_icons():
    """SVG-аас PNG icons үүсгэх (base64 ашиглах)"""
    
    icons_dir = 'app/static/icons'
    os.makedirs(icons_dir, exist_ok=True)
    
    # Simple PNG data (1x1 blue pixel)
    blue_pixel = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x00\x01\x00\x18\xdd\x8d\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    
    # Icon sizes
    sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    
    for size in sizes:
        # Simple PNG icon үүсгэх (blue square with white text)
        png_data = create_simple_png(size)
        
        png_path = os.path.join(icons_dir, f'icon-{size}x{size}.png')
        with open(png_path, 'wb') as f:
            f.write(png_data)
        print(f"✅ Created {png_path}")
    
    # Badge icon үүсгэх
    badge_data = create_simple_png(72, color=(220, 38, 127))  # Red
    badge_path = os.path.join(icons_dir, 'badge-72x72.png')
    with open(badge_path, 'wb') as f:
        f.write(badge_data)
    print(f"✅ Created {badge_path}")
    
    # Shortcut icons үүсгэх
    shortcuts = [
        ('shortcut-add.png', (34, 197, 94)),      # Green
        ('shortcut-history.png', (59, 130, 246)), # Blue
        ('shortcut-charts.png', (168, 85, 247))   # Purple
    ]
    
    for filename, color in shortcuts:
        shortcut_data = create_simple_png(96, color=color)
        shortcut_path = os.path.join(icons_dir, filename)
        with open(shortcut_path, 'wb') as f:
            f.write(shortcut_data)
        print(f"✅ Created {shortcut_path}")
    
    print("\n🎉 PNG icons амжилттай үүсгэгдлээ!")

def create_simple_png(size, color=(59, 130, 246)):
    """Энгийн PNG icon үүсгэх"""
    # PNG header
    png_header = b'\x89PNG\r\n\x1a\n'
    
    # IHDR chunk
    width = height = size
    bit_depth = 8
    color_type = 2  # RGB
    compression = 0
    filter_method = 0
    interlace = 0
    
    ihdr_data = width.to_bytes(4, 'big') + height.to_bytes(4, 'big') + \
                bit_depth.to_bytes(1, 'big') + color_type.to_bytes(1, 'big') + \
                compression.to_bytes(1, 'big') + filter_method.to_bytes(1, 'big') + \
                interlace.to_bytes(1, 'big')
    
    ihdr_crc = crc32(b'IHDR' + ihdr_data)
    ihdr_chunk = len(ihdr_data).to_bytes(4, 'big') + b'IHDR' + ihdr_data + ihdr_crc.to_bytes(4, 'big')
    
    # IDAT chunk (image data)
    # Simple blue square
    image_data = b''
    for y in range(height):
        # Filter type 0 (None)
        image_data += b'\x00'
        for x in range(width):
            # RGB values
            image_data += color[0].to_bytes(1, 'big')  # Red
            image_data += color[1].to_bytes(1, 'big')  # Green
            image_data += color[2].to_bytes(1, 'big')  # Blue
    
    # Compress image data (simple)
    compressed_data = image_data  # No compression for simplicity
    
    idat_crc = crc32(b'IDAT' + compressed_data)
    idat_chunk = len(compressed_data).to_bytes(4, 'big') + b'IDAT' + compressed_data + idat_crc.to_bytes(4, 'big')
    
    # IEND chunk
    iend_crc = crc32(b'IEND')
    iend_chunk = (0).to_bytes(4, 'big') + b'IEND' + iend_crc.to_bytes(4, 'big')
    
    return png_header + ihdr_chunk + idat_chunk + iend_chunk

def crc32(data):
    """Simple CRC32 calculation"""
    import zlib
    return zlib.crc32(data) & 0xffffffff

if __name__ == '__main__':
    create_png_icons()
