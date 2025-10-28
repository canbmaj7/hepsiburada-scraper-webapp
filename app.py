from flask import Flask, render_template, request, jsonify, send_file
import re
import time
import sys
from typing import List, Dict
from datetime import datetime
import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# .env dosyasını yükle
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__)
app.secret_key = 'hepsiburada_secret_key_2024'

# Google Sheets ayarları (.env'den oku)
GOOGLE_SHEET_URL = os.getenv('GOOGLE_SHEET_URL', '')
DEVELOPMENT_MODE = os.getenv('DEVELOPMENT_MODE', 'False').lower() == 'true'

def get_password_from_sheet():
    """Google Sheets'ten B5 hücresindeki şifreyi al"""
    if DEVELOPMENT_MODE:
        return None
    
    if not GOOGLE_SHEET_URL:
        print("⚠️ GOOGLE_SHEET_URL bulunamadı, .env dosyasını kontrol edin")
        return None  # Varsayılan şifre
    
    try:
        # CSV olarak export URL
        csv_url = GOOGLE_SHEET_URL.replace('/edit?gid=', '/export?format=csv&gid=')
        if 'gid=' not in GOOGLE_SHEET_URL:
            csv_url = GOOGLE_SHEET_URL.replace('/edit', '/export?format=csv')
        
        # CSV okumayı dene
        df = pd.read_csv(csv_url)
        
        # B5 hücresi için veri kontrolü
        # CSV'de header varsa index 0'dan başlar, B5 = 5. satır = index 4
        # Satır sayısı kontrolü: en az 5 satır olmalı
        if len(df) >= 4 and len(df.columns) >= 2:
            # 4. satır (index 3) = B4 değil, B5 için 5. satır gerekli
            # En son satırı al (B5 varsa)
            if len(df) >= 5:
                password = df.iloc[4, 1]  # Satır 4 (5. satır = B5)
            else:
                # Satır yoksa son satırı al
                password = df.iloc[len(df)-1, 1]
            print(f"✅ Şifre Google Sheets'ten alındı: {password}")
            return str(password).strip()
        else:
            print(f"⚠️ Google Sheets formatı beklenmiyor (satır: {len(df)}, sütun: {len(df.columns)})")
            return None
    except Exception as e:
        print(f"❌ Google Sheets hatası: {e}")
        return None  # Hata durumunda varsayılan

# NOT: CORRECT_PASSWORD kullanılmıyor, her login'de dinamik olarak alınıyor

class HepsiburadaScraper:
    """Hepsiburada scraper - Web için"""
    
    def __init__(self):
        self.driver = None
        self._setup_driver()
    
    def _setup_driver(self):
        """Chrome driver'ı kur - Hızlandırılmış ve optimize edilmiş"""
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-images")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--window-size=1280,800")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        # Hızlandırma için yeni eklemeler
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=IsolateOrigins,site-per-process")
        options.add_argument("--disable-site-isolation-trials")
        options.add_argument("--disable-remote-fonts")
        options.add_argument("--disable-smooth-scrolling")
        options.add_argument("--disable-css-animations")
        
        try:
            # EXE içinde dosya yolu sorunu için düzeltme
            if getattr(sys, 'frozen', False):
                # EXE modda
                chromedriver_path = os.path.join(sys._MEIPASS, 'chromedriver.exe')
            else:
                # Normal modda
                chromedriver_path = 'chromedriver.exe'
            
            service = Service(chromedriver_path)
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.set_page_load_timeout(15)  # EXE için daha uzun timeout
            self.driver.implicitly_wait(3)  # EXE için implicit wait
            print("✅ Chrome driver hazırlandı (optimize edilmiş)")
        except Exception as e:
            print(f"Driver hatası: {e}")
            self.driver = None

    def get_html_content(self, search_term: str) -> str:
        """Hepsiburada'dan arama yapıp HTML içeriğini al - EXE için optimize"""
        max_retries = 3  # EXE için daha fazla deneme
        
        for attempt in range(max_retries):
            try:
                if not self.driver:
                    print("❌ Driver bulunamadı")
                    return ""
                
                search_url = f"https://www.hepsiburada.com/ara?q={search_term}"
                print(f"🔍 Deneme {attempt + 1}/{max_retries}: {search_url}")
                
                self.driver.get(search_url)

                # Sayfanın tamamen yüklenmesini bekle
                wait = WebDriverWait(self.driver, 8)
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                
                # Ürün kartlarının yüklenmesi için bekle
                time.sleep(1)
                
                # Sayfayı kaydır - JavaScript ile yüklenen içerik için
                self.driver.execute_script("window.scrollTo(0, 500);")
                time.sleep(0.3)
                
                self.driver.execute_script("window.scrollTo(0, 1000);")
                time.sleep(0.3)
                
                html_content = self.driver.page_source
                
                if len(html_content) > 1000:  # HTML içerik yeterli
                    print(f"✅ HTML başarıyla alındı: {len(html_content)} karakter")
                    return html_content
                else:
                    print(f"⚠️ HTML içeriği çok kısa: {len(html_content)} karakter")
                    
            except Exception as e:
                print(f"❌ Hata (Deneme {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    print(f"🔄 {2} saniye bekleyip tekrar deneniyor...")
                    time.sleep(2)
                else:
                    print(f"❌ Tüm denemeler başarısız oldu")
                    return ""
        
        return ""

    def clean_stock_code(self, stock_code: str) -> str:
        """Stok kodunu temizle - sadece % işaretine kadar olan kısmı al"""
        if not stock_code or stock_code == "Bulunamadı":
            return stock_code
        
        # URL encoding'i decode et
        if '%' in stock_code:
            stock_code = stock_code.split('%')[0]
        
        return stock_code

    def parse_products(self, html_content: str) -> List[Dict]:
        """HTML içeriğinden ürün bilgilerini parse et"""
        products = []

        selectors = [
            r'<article class="productCard-module_article__[^"]*"[^>]*>(.*?)</article>',
            r'<article[^>]*class="[^"]*productCard[^"]*"[^>]*>(.*?)</article>',
            r'<div[^>]*class="[^"]*product-card[^"]*"[^>]*>(.*?)</div>',
            r'<li[^>]*class="[^"]*product[^"]*"[^>]*>(.*?)</li>'
        ]

        product_cards = []
        for selector in selectors:
            cards = re.findall(selector, html_content, re.DOTALL)
            if cards:
                product_cards = cards
                print(f"🔍 Bulunan ürün kartı sayısı: {len(product_cards)}")
                break

        if not product_cards:
            print("❌ Ürün kartı bulunamadı")
            return products

        for card_html in product_cards:
            product = {}

            # Ürün adı
            title_match = re.search(r'title="([^"]*?)"', card_html)
            if title_match:
                product_name = title_match.group(1)
                product_name = product_name.replace('&amp;', '&').replace('&quot;', '"').replace('&lt;', '<').replace('&gt;', '>')
                product['name'] = product_name.strip()

            # Stok kodu
            href_match = re.search(r'href="([^"]*?)"', card_html)
            if href_match:
                href = href_match.group(1)
                
                stock_code_patterns = [
                    r'-pm-(HBC[^/?]*)',
                    r'-p-(HBC[^/?]*)',
                    r'(HBCV\d+[^%]*)',  # HBCV ile başlayan ve % işaretinden önce duran
                    r'(HBC\d+[^%]*)',  # HBC ile başlayan ve % işaretinden önce duran
                ]
                
                stock_code = "Bulunamadı"
                for pattern in stock_code_patterns:
                    stock_code_match = re.search(pattern, href)
                    if stock_code_match:
                        stock_code = stock_code_match.group(1)
                        break
                
                # Stok kodunu temizle
                product['stock_code'] = self.clean_stock_code(stock_code)

            # Görsel URL
            img_match = re.search(r'<img[^>]*src="([^"]*)"[^>]*>', card_html)
            if img_match:
                product['image_url'] = img_match.group(1)
            else:
                product['image_url'] = ""

            if product.get('name'):
                products.append(product)

        return products

    def close(self):
        """Tarayıcıyı kapat"""
        if self.driver:
            self.driver.quit()


# Global scraper instance
scraper = HepsiburadaScraper()
found_products = []
cache = {}  # Barkod cache'i

# Kullanıcı oturum takibi
authenticated_users = {}

def check_auth():
    """Şifre kontrolü - Geliştirme modunda atla"""
    if DEVELOPMENT_MODE:
        return True
    
    session_id = request.cookies.get('session_id')
    if session_id and session_id in authenticated_users:
        return True
    
    return False

@app.route('/')
def index():
    # Şifre kontrolü
    if not check_auth():
        return render_template('login.html')
    return render_template('index.html')

@app.route('/api/login', methods=['POST'])
def login():
    """Şifre ile giriş yap - Her seferinde Google Sheets'ten şifreyi al"""
    data = request.json
    password = data.get('password', '')
    
    if DEVELOPMENT_MODE:
        # Geliştirme modunda: Şifreyi atla
        import uuid
        session_id = str(uuid.uuid4())
        authenticated_users[session_id] = True
        response = jsonify({'success': True, 'redirect': '/'})
        response.set_cookie('session_id', session_id)
        return response
    
    # Her login'de şifreyi Google Sheets'ten tekrar al
    current_password = get_password_from_sheet()
    
    if password == current_password:
        import uuid
        session_id = str(uuid.uuid4())
        authenticated_users[session_id] = True
        response = jsonify({'success': True, 'redirect': '/'})
        response.set_cookie('session_id', session_id)
        return response
    else:
        print(f"❌ Yanlış şifre girildi. Beklenen: {current_password}")
        return jsonify({'success': False, 'error': 'Yanlış şifre!'}), 401

@app.route('/api/search', methods=['POST'])
def search():
    data = request.json
    barcode = data.get('barcode', '')
    
    if not barcode:
        return jsonify({'error': 'Arama terimi boş olamaz'}), 400
    
    # Cache kontrolü
    if barcode in cache:
        print(f"✅ Cache'den alındı: {barcode}")
        return jsonify({'products': cache[barcode], 'cached': True})
    
    html_content = scraper.get_html_content(barcode)
    
    if not html_content:
        return jsonify({'error': 'HTML içeriği alınamadı'}), 500
    
    print(f"DEBUG: HTML uzunluğu: {len(html_content)}")
    
    products = scraper.parse_products(html_content)
    
    # Cache'e kaydet
    cache[barcode] = products
    print(f"💾 Cache'e kaydedildi: {barcode}")
    
    print(f"DEBUG: Bulunan ürün sayısı: {len(products)}")
    
    return jsonify({'products': products, 'cached': False})

@app.route('/api/add', methods=['POST'])
def add_product():
    data = request.json
    barcode = data.get('barcode')
    product = data.get('product')
    quantity = data.get('quantity', 1)
    
    # Aynı stok kodlu ürün var mı kontrol et
    existing_index = None
    for i, item in enumerate(found_products):
        if item.get('stock_code') == product['stock_code'] and item.get('barcode') == barcode:
            existing_index = i
            break
    
    if existing_index is not None:
        # Mevcut ürünün adetini artır
        found_products[existing_index]['quantity'] += quantity
        updated_qty = found_products[existing_index]['quantity']
        
        # Ürün adını güncelle
        if updated_qty == 1:
            found_products[existing_index]['name'] = product['name']
        else:
            found_products[existing_index]['name'] = f"{product['name']} * {updated_qty} Adet"
        
        print(f"✅ Ürün adeti artırıldı: {product['name']} - {updated_qty} adet")
        return jsonify({'success': True, 'product': found_products[existing_index], 'updated': True})
    else:
        # Yeni ürün ekle
        if quantity == 1:
            product_name = product['name']
        else:
            product_name = f"{product['name']} * {quantity} Adet"
        
        new_product = {
            'barcode': barcode,
            'stock_code': product['stock_code'],
            'name': product_name,
            'image_url': product.get('image_url', ''),
            'price': product.get('price', ''),
            'quantity': quantity
        }
        
        found_products.append(new_product)
        print(f"➕ Yeni ürün eklendi: {product['name']} - {quantity} adet")
        return jsonify({'success': True, 'product': new_product, 'updated': False})

@app.route('/api/products', methods=['GET'])
def get_products():
    return jsonify({'products': found_products})

@app.route('/api/delete/<int:index>', methods=['DELETE'])
def delete_product(index):
    if 0 <= index < len(found_products):
        deleted = found_products.pop(index)
        return jsonify({'success': True, 'deleted': deleted})
    return jsonify({'error': 'Geçersiz index'}), 400

@app.route('/api/update-quantity', methods=['POST'])
def update_quantity():
    data = request.json
    index = data.get('index')
    quantity = data.get('quantity', 1)
    
    if not (0 <= index < len(found_products)):
        return jsonify({'error': 'Geçersiz index'}), 400
    
    # Mevcut ürünü al
    product = found_products[index]
    
    # Yeni adet ile ürün ismini güncelle
    if quantity == 1:
        product_name = product['name'].split(' * ')[0]  # Sadece ürün adını al
    else:
        base_name = product['name'].split(' * ')[0]  # Temel ürün adı
        product_name = f"{base_name} * {quantity} Adet"
    
    # Güncelle
    found_products[index]['quantity'] = quantity
    found_products[index]['name'] = product_name
    
    return jsonify({'success': True, 'product': found_products[index]})

@app.route('/api/export', methods=['GET'])
def export_excel():
    if not found_products:
        return jsonify({'error': 'Export edilecek ürün yok'}), 400
    
    try:
        # Sepetteki ürünleri dataframe'e çevir
        export_data = []
        for p in found_products:
            # barcode alanı yoksa boş bırak
            barcode = p.get('barcode', '')
            export_data.append({
                'StokKodu': p.get('stock_code', ''),
                'Ürünİsmi': p.get('name', ''),
                'Adet': p.get('quantity', 1)
            })
        
        df = pd.DataFrame(export_data)
        
        # Geçici dosya oluştur
        filename = f"bulunanlar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        # Temp dizin kullan (EXE için)
        import tempfile
        temp_dir = tempfile.gettempdir()
        filepath = os.path.join(temp_dir, filename)
        
        df.to_excel(filepath, index=False, engine='openpyxl')
        
        return send_file(filepath, as_attachment=True, download_name=filename)
        
    except Exception as e:
        print(f"❌ Export hatası: {str(e)}")
        return jsonify({'error': f'Export hatası: {str(e)}'}), 500

@app.route('/api/shutdown', methods=['POST'])
def shutdown():
    """Uygulamayı kapat - Temiz bir şekilde"""
    
    def cleanup():
        """Temizlik işlemleri"""
        try:
            # Chrome driver'ı kapat
            if scraper and scraper.driver:
                scraper.driver.quit()
        except:
            pass
        
        # System exit
        import os
        os._exit(0)
    
    # 0.5 saniye bekle ve temizle
    import threading
    threading.Timer(0.5, cleanup).start()
    return jsonify({'success': True})

if __name__ == '__main__':
    import webbrowser
    import threading
    import sys
    import ctypes
    
    # Konsolu gizle (Windows'ta)
    if sys.platform == 'win32':
        try:
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        except:
            pass
    
    # Tarayıcıyı ayrı bir thread'de aç
    def open_browser():
        time.sleep(1.5)  # Sunucunun başlaması için bekle
        webbrowser.open('http://127.0.0.1:5000')
    
    threading.Thread(target=open_browser).start()
    app.run(debug=False, port=5000, use_reloader=False)
