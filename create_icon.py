from PIL import Image, ImageDraw, ImageFont
import os
import math

def create_icon():
    """Hepsiburada gerçek logo tasarımı"""
    
    # 256x256 icon boyutu
    size = 256
    img = Image.new('RGB', (size, size), color='white')
    draw = ImageDraw.Draw(img)
    
    # Beyaz arka plan
    draw.rectangle([0, 0, size, size], fill='white')
    
    center_x = size // 2
    center_y = size // 2
    outer_radius = size * 0.42
    inner_radius = size * 0.32
    
    # Segmented circle - 5 renkli segment
    colors = [
        '#FF6000',  # Turuncu
        '#4ECDC4',  # Açık mavi
        '#5865F2',  # Mavi-mor
        '#00C9FF',  # Turkuaz
        '#FFD700'   # Sarı (Golden)
    ]
    
    # Her segment için açı hesapla
    segment_angle = 360 / len(colors)
    
    # Segmanları çiz
    for i, color in enumerate(colors):
        start_angle = i * segment_angle
        end_angle = (i + 1) * segment_angle
        
        # Segmanı çiz (büyük dış daire + küçük iç daire)
        points_outer = []
        points_inner = []
        
        # Dış daire noktaları
        for angle in range(int(start_angle * 10), int(end_angle * 10) + 1, 1):
            angle_rad = math.radians(angle / 10)
            x_outer = center_x + outer_radius * math.cos(angle_rad - math.pi/2)
            y_outer = center_y + outer_radius * math.sin(angle_rad - math.pi/2)
            points_outer.append((x_outer, y_outer))
        
        # İç daire noktaları (ters sırada)
        for angle in range(int(end_angle * 10), int(start_angle * 10) - 1, -1):
            angle_rad = math.radians(angle / 10)
            x_inner = center_x + inner_radius * math.cos(angle_rad - math.pi/2)
            y_inner = center_y + inner_radius * math.sin(angle_rad - math.pi/2)
            points_inner.append((x_inner, y_inner))
        
        # Segmanı doldur
        points = points_outer + points_inner
        if len(points) >= 3:
            draw.polygon(points, fill=color, outline=color)
    
    # İç beyaz daire
    white_radius = size * 0.31
    draw.ellipse(
        [center_x - white_radius, center_y - white_radius,
         center_x + white_radius, center_y + white_radius],
        fill='white', outline='white'
    )
    
    # "hepsi burada" TEXT - Kalın
    try:
        font_size = int(size * 0.13)
        # Bold font dene
        try:
            font_bold = ImageFont.truetype("arialbd.ttf", font_size)
        except:
            try:
                font_bold = ImageFont.truetype("arial.ttf", font_size)
            except:
                font_bold = ImageFont.load_default()
    except:
        try:
            font_bold = ImageFont.truetype("arial.ttf", 32)
        except:
            font_bold = ImageFont.load_default()
    
    # Yazıyı hafif kalın yapmak için stroke ekle
    stroke_width = 1
    
    # "hepsi" satırı
    text1 = "hepsi"
    try:
        bbox1 = draw.textbbox((0, 0), text1, font=font_bold)
        text1_width = bbox1[2] - bbox1[0]
        text1_height = bbox1[3] - bbox1[1]
    except:
        text1_width = 60
        text1_height = 30
    
    text1_x = center_x - text1_width // 2
    text1_y = center_y - text1_height
    
    # "hepsi" text - turuncu-kırmızımsı, kalın
    draw.text((text1_x, text1_y), text1, fill='#FF4500', font=font_bold, stroke_width=stroke_width, stroke_fill='#FF4500')
    
    # "burada" satırı
    text2 = "burada"
    try:
        bbox2 = draw.textbbox((0, 0), text2, font=font_bold)
        text2_width = bbox2[2] - bbox2[0]
    except:
        text2_width = 70
    
    text2_x = center_x - text2_width // 2
    text2_y = center_y + 5
    
    # "burada" text - kalın
    draw.text((text2_x, text2_y), text2, fill='#FF4500', font=font_bold, stroke_width=stroke_width, stroke_fill='#FF4500')
    
    # Kenarlık (ince siyah çerçeve)
    border_width = 2
    draw.rectangle([0, 0, size-1, size-1], outline='black', width=border_width)
    
    # ICO formatında kaydet
    img.save('app_icon.ico', format='ICO', sizes=[(256, 256), (128, 128), (96, 96), (64, 64), (48, 48), (32, 32), (16, 16)])
    print("✅ Hepsiburada logo oluşturuldu: app_icon.ico")
    
    # PNG formatında da kaydet
    img.save('app_icon.png', format='PNG')
    print("✅ Logo PNG formatında kaydedildi: app_icon.png")
    
    # Geçici dosyaları temizle
    for f in ['temp_icon_256x256.png', 'temp_icon_128x128.png', 'temp_icon_96x96.png', 
              'temp_icon_64x64.png', 'temp_icon_48x48.png', 'temp_icon_32x32.png', 
              'temp_icon_16x16.png']:
        try:
            if os.path.exists(f):
                os.remove(f)
        except:
            pass

if __name__ == '__main__':
    try:
        create_icon()
    except ImportError:
        print("❌ PIL (Pillow) kütüphanesi bulunamadı!")
        print("📦 Kurulum için: pip install Pillow")
        import subprocess
        subprocess.run(["pip", "install", "Pillow"], check=True)
        create_icon()
    except Exception as e:
        print(f"❌ Hata: {e}")
        import traceback
        traceback.print_exc()
