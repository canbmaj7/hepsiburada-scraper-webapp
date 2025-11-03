from flask import Flask, render_template, request, jsonify, send_file
import re
import time
import sys
from typing import List, Dict
import socket
from datetime import datetime
import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# .env dosyasını yükle (PyInstaller uyumlu)
try:
    from dotenv import load_dotenv
    base_dirs = [
        os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.getcwd(),
        getattr(sys, '_MEIPASS', ''),
        os.getcwd(),
    ]
    loaded = False
    for base in base_dirs:
        if not base:
            continue
        env_path = os.path.join(base, '.env')
        if os.path.exists(env_path):
            load_dotenv(env_path)
            loaded = True
            break
    if not loaded:
        load_dotenv()
except ImportError:
    pass

app = Flask(__name__)
app.secret_key = 'hepsiburada_secret_key_2024'

# Google Sheets ayarları (.env'den oku)
GOOGLE_SHEET_URL = os.getenv('GOOGLE_SHEET_URL', '')
DEVELOPMENT_MODE = os.getenv('DEVELOPMENT_MODE', 'False').lower() == 'true'

def get_password_from_sheet():
    """Google Sheets'ten B5 hücresindeki şifreyi al (EXE uyumlu ve dayanıklı)."""
    if DEVELOPMENT_MODE:
        return None

    sheet_id = os.getenv('SHEET_ID', '').strip()
    sheet_url = os.getenv('GOOGLE_SHEET_URL', '').strip()

    # CSV URL oluştur
    csv_url = ''
    if sheet_url:
        if '/export?format=csv' in sheet_url:
            csv_url = sheet_url
        else:
            csv_url = sheet_url.replace('/edit?gid=', '/export?format=csv&gid=')
            csv_url = csv_url.replace('/edit#gid=', '/export?format=csv&gid=')
            if 'export?format=csv' not in csv_url:
                csv_url = sheet_url.rstrip('/') + '/export?format=csv'
    elif sheet_id:
        csv_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv'
    else:
        print('⚠️ Ne GOOGLE_SHEET_URL ne de SHEET_ID tanımlı.')
        return None

    # requests ile CSV çek (EXE'de daha stabil)
    try:
        import requests, csv, io
        resp = requests.get(csv_url, timeout=8)
        resp.raise_for_status()
        reader = csv.reader(io.StringIO(resp.text))
        rows = list(reader)
        if not rows:
            print('⚠️ Sheets CSV boş döndü')
            return None
        # B5 (5. satır, 2. sütun) yoksa son satırın 2. sütunu
        if len(rows) >= 5 and len(rows[4]) >= 2:
            password = rows[4][1]
        else:
            last = rows[-1]
            password = last[1] if len(last) >= 2 else ''
        password = (password or '').strip().strip('"')
        if not password:
            print('⚠️ Sheets B sütununda şifre bulunamadı')
            return None
        print('✅ Şifre Google Sheets\'ten alındı')
        return password
    except Exception as e:
        print(f'❌ Google Sheets isteği başarısız: {e}')
        return None

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
                stock_code = self.extract_stock_code_from_url(href)
                product['stock_code'] = stock_code

            # Görsel URL
            img_match = re.search(r'<img[^>]*src="([^"]*)"[^>]*>', card_html)
            if img_match:
                product['image_url'] = img_match.group(1)
            else:
                product['image_url'] = ""

            if product.get('name'):
                products.append(product)

        return products

    def extract_stock_code_from_url(self, url: str) -> str:
        """Hepsiburada ürün URL'sinden stok kodunu çıkarır ve UPPERCASE döner.
        Öncelik: HBV/HBCV -> pm-/p- sonrası kod -> yol sonu bloğu.
        """
        try:
            from urllib.parse import urlparse, unquote
            parsed = urlparse(url or '')
            path = unquote(parsed.path or '')

            # 1) HB varyantları (case-insensitive)
            m = re.search(r'(HBCV[0-9A-Z]+)', path, re.IGNORECASE)
            if not m:
                m = re.search(r'(HBV[0-9A-Z]+)', path, re.IGNORECASE)
            if not m:
                m = re.search(r'(HBC[0-9A-Z]+)', path, re.IGNORECASE)
            if m:
                code = m.group(1)
                code = re.sub(r'[^0-9A-Z]', '', code.upper())
                return code[:24]

            # 2) pm-/p- sonrası alfasayısal blok
            m = re.search(r'/(?:pm|p)-([a-z0-9]+)', path, re.IGNORECASE)
            if m:
                code = m.group(1)
                code = re.sub(r'[^0-9A-Z]', '', code.upper())
                return code[:24]

            # 3) Yol sonu bloğu: en sondaki '-' sonrası 6+ uzun alfasayısal
            last_seg = (path.split('/')[-1]) if path else ''
            m = re.search(r'-([a-z0-9]{6,})$', last_seg, re.IGNORECASE)
            if m:
                code = m.group(1)
                code = re.sub(r'[^0-9A-Z]', '', code.upper())
                return code[:24]

            return "Bulunamadı"
        except Exception:
            return "Bulunamadı"

    def close(self):
        """Tarayıcıyı kapat"""
        if self.driver:
            self.driver.quit()


# Global scraper instance
scraper = HepsiburadaScraper()
found_products = []

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

def is_port_in_use(port: int) -> bool:
    """Belirtilen port dinlemede mi?"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.3)
            return s.connect_ex(('127.0.0.1', port)) == 0
    except Exception:
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
    
    html_content = scraper.get_html_content(barcode)
    
    if not html_content:
        return jsonify({'error': 'HTML içeriği alınamadı'}), 500
    
    print(f"DEBUG: HTML uzunluğu: {len(html_content)}")
    
    products = scraper.parse_products(html_content)
    
    print(f"DEBUG: Bulunan ürün sayısı: {len(products)}")
    
    return jsonify({'products': products, 'cached': False})

@app.route('/api/search-hb', methods=['POST'])
def search_hb():
    data = request.json
    term = data.get('barcode', '').strip()
    if not term:
        return jsonify({'error': 'Arama terimi boş olamaz'}), 400

    # Selenium ile ara
    html = scraper.get_html_content(term)
    if not html:
        return jsonify({'products': []})
    products: List[Dict] = scraper.parse_products(html)

    return jsonify({'products': products, 'cached': False})

# (Kaldırıldı) cache-clear / driver-status / driver-restart uç noktaları

# --- Yeni: Google arama (yalnızca Selenium) ---
def parse_google_titles(html: str) -> List[str]:
    """Google sonuç sayfasından başlıkları çıkar.
    Birden fazla selector ile dayanıklı parse.
    """
    try:
        patterns = [
            r'<h3[^>]*>(.*?)</h3>',
            r'<div[^>]*class="[^\"]*(?:LC20lb|vvjwJb|FCUp0c)[^\"]*"[^>]*>(.*?)</div>',
            r'<span[^>]*role="text"[^>]*>(.*?)</span>'
        ]
        raw: List[str] = []
        for pat in patterns:
            found = re.findall(pat, html, re.DOTALL)
            raw.extend(found)

        clean: List[str] = []
        for t in raw:
            text = re.sub(r'<[^>]+>', '', t)
            text = re.sub(r'\s+', ' ', text).strip()
            if text:
                clean.append(text)

        # Benzersiz ve anlamlı uzunlukta olanları topla
        seen = set()
        uniq: List[str] = []
        for t in clean:
            if len(t) < 3:
                continue
            if t not in seen:
                seen.add(t)
                uniq.append(t)
        return uniq[:20]
    except Exception as e:
        print(f"Google parse hatası: {e}")
        return []

def get_google_titles_with_selenium(query: str) -> List[str]:
    try:
        if not scraper.driver:
            # Driver yoksa yeniden kurmayı dene
            try:
                scraper._setup_driver()
            except Exception as _:
                return []

        url = f"https://www.google.com/search?q={query}&hl=tr&gl=tr&pws=0"
        scraper.driver.get(url)
        wait = WebDriverWait(scraper.driver, 8)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        scraper.driver.execute_script("window.scrollTo(0, 600);")
        scraper.driver.execute_script("window.scrollTo(0, 1200);")
        html = scraper.driver.page_source
        return parse_google_titles(html)
    except Exception as e:
        print(f"Google Selenium hatası: {e}")
        return []

def parse_duck_titles(html: str) -> List[str]:
    """DuckDuckGo HTML sonuçlarından başlıkları çıkar."""
    try:
        # html.duckduckgo.com/html çıktısında result__a linkleri var
        titles = re.findall(r'<a[^>]*class="[^\"]*result__a[^\"]*"[^>]*>(.*?)</a>', html, re.DOTALL)
        clean: List[str] = []
        for t in titles:
            text = re.sub(r'<[^>]+>', '', t)
            text = re.sub(r'\s+', ' ', text).strip()
            if text:
                clean.append(text)
        # Eşsiz ilk 20
        seen, uniq = set(), []
        for t in clean:
            if t not in seen:
                seen.add(t)
                uniq.append(t)
        return uniq[:20]
    except Exception as e:
        print(f"Duck parse hatası: {e}")
        return []

def parse_bing_titles(html: str) -> List[str]:
    """Bing sonuçlarından başlıkları çıkar."""
    try:
        # b_algo li içindeki <h2><a> başlıkları
        titles = re.findall(r'<li[^>]*class="[^\"]*b_algo[^\"]*"[^>]*>.*?<h2>\s*<a[^>]*>(.*?)</a>', html, re.DOTALL)
        clean: List[str] = []
        for t in titles:
            text = re.sub(r'<[^>]+>', '', t)
            text = re.sub(r'\s+', ' ', text).strip()
            if text:
                clean.append(text)
        seen, uniq = set(), []
        for t in clean:
            if t not in seen:
                seen.add(t)
                uniq.append(t)
        return uniq[:20]
    except Exception as e:
        print(f"Bing parse hatası: {e}")
        return []

@app.route('/api/search-google', methods=['POST'])
def search_google():
    data = request.json
    query = data.get('query', '').strip()
    if not query:
        return jsonify({'error': 'Arama terimi boş olamaz'}), 400

    try:
        titles = get_google_titles_with_selenium(query)
        products = [{'name': t, 'stock_code': '', 'image_url': ''} for t in titles]
        return jsonify({'products': products})
    except Exception as e:
        print(f"Google Selenium genel hata: {e}")
        return jsonify({'products': []})

@app.route('/api/manual-add', methods=['POST'])
def manual_add():
    data = request.json
    name = (data.get('name') or '').strip()
    barcode = (data.get('barcode') or '').strip()
    quantity = int(data.get('quantity') or 1)
    if not name or quantity < 1:
        return jsonify({'error': 'Geçersiz veri'}), 400
    if barcode and not barcode.isdigit():
        return jsonify({'error': 'Barkod sadece sayı olabilir'}), 400

    new_product = {
        'barcode': barcode,
        'stock_code': barcode if barcode else '',
        'name': name if quantity == 1 else f"{name} * {quantity} Adet",
        'image_url': '',
        'price': '',
        'quantity': quantity,
        'source': 'manual'
    }
    found_products.append(new_product)
    return jsonify({'success': True, 'product': new_product})

@app.route('/api/add', methods=['POST'])
def add_product():
    data = request.json
    barcode = data.get('barcode')
    product = data.get('product')
    quantity = data.get('quantity', 1)
    replace_existing = data.get('replace_existing', False)
    source = (data.get('source') or '').strip().lower() or ('google' if replace_existing else 'hb')
    
    # Aynı stok kodlu ürün var mı kontrol et
    existing_index = None
    for i, item in enumerate(found_products):
        if item.get('stock_code') == product['stock_code'] and item.get('barcode') == barcode:
            existing_index = i
            break
    
    if existing_index is not None:
        # HB: her zaman adet artır
        if not replace_existing:
            found_products[existing_index]['quantity'] += quantity
            updated_qty = found_products[existing_index]['quantity']
            base_incoming = (product.get('name') or '').split(' * ')[0]
            found_products[existing_index]['name'] = base_incoming if updated_qty == 1 else f"{base_incoming} * {updated_qty} Adet"
            if not found_products[existing_index].get('source'):
                found_products[existing_index]['source'] = source
            print(f"✅ (HB) Adet artırıldı: {base_incoming} - {updated_qty} adet")
            return jsonify({'success': True, 'product': found_products[existing_index], 'updated': True})
        
        # Google: isim aynıysa adet artır, farklıysa değiştir (adet=1)
        existing_base = (found_products[existing_index].get('name') or '').split(' * ')[0].strip()
        incoming_base = (product.get('name') or '').split(' * ')[0].strip()
        if existing_base.lower() == incoming_base.lower():
            found_products[existing_index]['quantity'] += quantity
            updated_qty = found_products[existing_index]['quantity']
            found_products[existing_index]['name'] = existing_base if updated_qty == 1 else f"{existing_base} * {updated_qty} Adet"
            if not found_products[existing_index].get('source'):
                found_products[existing_index]['source'] = source
            print(f"✅ (Google) Aynı isim, adet artırıldı: {existing_base} - {updated_qty} adet")
            return jsonify({'success': True, 'product': found_products[existing_index], 'updated': True, 'replaced': False})
        else:
            # Değiştir - adedi 1'e çek ve adı güncelle
            found_products[existing_index]['quantity'] = 1
            found_products[existing_index]['name'] = incoming_base
            if product.get('stock_code'):
                found_products[existing_index]['stock_code'] = product['stock_code']
            found_products[existing_index]['image_url'] = product.get('image_url', found_products[existing_index].get('image_url', ''))
            found_products[existing_index]['price'] = product.get('price', found_products[existing_index].get('price', ''))
            found_products[existing_index]['source'] = source
            print(f"♻️ (Google) Farklı isim, ürün değiştirildi: {incoming_base}")
            return jsonify({'success': True, 'product': found_products[existing_index], 'updated': True, 'replaced': True})
    else:
        # Yeni ürün ekle
        base_name = product.get('name', '')
        product_name = base_name if quantity == 1 else f"{base_name} * {quantity} Adet"
        stock_code = product.get('stock_code') or barcode or ''
        
        new_product = {
            'barcode': barcode,
            'stock_code': stock_code,
            'name': product_name,
            'image_url': product.get('image_url', ''),
            'price': product.get('price', ''),
            'quantity': quantity,
            'source': source
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

@app.route('/api/edit-product', methods=['POST'])
def edit_product():
    data = request.json
    index = data.get('index')
    name = (data.get('name') or '').strip()
    barcode = (data.get('barcode') or '').strip()
    if index is None or not (0 <= index < len(found_products)):
        return jsonify({'error': 'Geçersiz index'}), 400
    if not name:
        return jsonify({'error': 'İsim boş olamaz'}), 400
    if barcode and not barcode.isdigit():
        return jsonify({'error': 'Barkod sadece sayı olabilir'}), 400

    product = found_products[index]
    qty = product.get('quantity', 1)
    base_name = name
    product_name = base_name if qty == 1 else f"{base_name} * {qty} Adet"
    product['name'] = product_name
    product['barcode'] = barcode
    # Google kaynaklı ürünlerde düzenleme sonrası barkod ve stok kodu eşitlensin
    if barcode:
        if (product.get('source') or '').lower() == 'google':
            product['stock_code'] = barcode
        elif not product.get('stock_code'):
            product['stock_code'] = barcode
    else:
        # Barkod silindiğinde stok kodunu da sil
        product['stock_code'] = ''
    found_products[index] = product
    return jsonify({'success': True, 'product': product})

@app.route('/api/export', methods=['GET'])
def export_excel():
    if not found_products:
        return jsonify({'error': 'Export edilecek ürün yok'}), 400
    
    try:
        # Barkod doğrulama: sadece rakam
        invalid = []
        for idx, p in enumerate(found_products):
            bc = str(p.get('barcode') or '').strip()
            if bc and not bc.isdigit():
                invalid.append({'index': idx, 'name': p.get('name', ''), 'barcode': bc})
        if invalid:
            return jsonify({'error': 'Lütfen barkodları sadece sayı olacak şekilde düzenleyin.', 'invalid': invalid}), 400

        weekday_map = {0:'Pazartesi',1:'Salı',2:'Çarşamba',3:'Perşembe',4:'Cuma',5:'Cumartesi',6:'Pazar'}
        today_day = weekday_map[datetime.now().weekday()]
        
        export_data = []
        for p in found_products:
            export_data.append({
                'BarkodNo': p.get('barcode', ''),
                'StokKodu': p.get('stock_code', ''),
                'Ürünİsmi': p.get('name', ''),
                'GÜN': today_day
            })
        
        df = pd.DataFrame(export_data)
        
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
    
    # Tekil instance kontrolü: mutex ve port
    try:
        existing_running = False
        if sys.platform == 'win32':
            try:
                kernel32 = ctypes.windll.kernel32
                kernel32.SetLastError(0)
                mutex = kernel32.CreateMutexW(None, True, 'HB_SINGLETON_MUTEX')
                already = ctypes.GetLastError() == 183
                if already or is_port_in_use(5001):
                    existing_running = True
            except Exception:
                if is_port_in_use(5001):
                    existing_running = True
        else:
            if is_port_in_use(5001):
                existing_running = True

        if existing_running:
            try:
                webbrowser.open('http://127.0.0.1:5001')
            finally:
                sys.exit(0)
    except Exception:
        # Beklenmedik durumda normal akışa devam et
        pass
    
    # Konsolu gizle (Windows'ta)
    if sys.platform == 'win32':
        try:
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        except:
            pass
    
    # Tarayıcıyı ayrı bir thread'de aç
    def open_browser():
        time.sleep(1.5)  # Sunucunun başlaması için bekle
        webbrowser.open('http://127.0.0.1:5001')
    
    threading.Thread(target=open_browser).start()
    app.run(debug=False, port=5001, use_reloader=False)
