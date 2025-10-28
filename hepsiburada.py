import re
import time
from typing import List, Dict
from datetime import datetime
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class HepsiburadaScraper:
    """Hepsiburada scraper - tek tarayıcı oturumu ile"""
    
    def __init__(self):
        self.driver = None
        self.found_products = []  # Bulunan ürünler listesi
        self._setup_driver()
    
    def _setup_driver(self):
        """Chrome driver'ı kur - Optimize edilmiş"""
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-images")  # Resimleri yükleme
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--window-size=1280,800")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

        service = Service("chromedriver.exe")
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Timeout'ları azalt
        self.driver.set_page_load_timeout(10)
        self.driver.implicitly_wait(0)  # Implicit wait'i kapat
        
        print("🌐 Tarayıcı başlatıldı (Optimize)")

    def get_html_content(self, search_term: str) -> str:
        """Hepsiburada'dan arama yapıp HTML içeriğini al"""
        try:
            print(f"🔍 '{search_term}' araması yapılıyor...")

            search_url = f"https://www.hepsiburada.com/ara?q={search_term}"
            self.driver.get(search_url)

            # Timeout'u azalt
            wait = WebDriverWait(self.driver, 3)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            # Scroll bekleme süresini azalt
            self.driver.execute_script("window.scrollTo(0, 300);")
            time.sleep(0.2)

            return self.driver.page_source

        except Exception as e:
            print(f"❌ HTML alma hatası: {e}")
            return ""

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

            title_match = re.search(r'title="([^"]*?)"', card_html)
            if title_match:
                product_name = title_match.group(1)
                product_name = product_name.replace('&amp;', '&').replace('&quot;', '"').replace('&lt;', '<').replace('&gt;', '>')
                product['name'] = product_name.strip()

            href_match = re.search(r'href="([^"]*?)"', card_html)
            if href_match:
                href = href_match.group(1)
                
                stock_code_patterns = [
                    r'-pm-(HBC[^/?]*)',
                    r'-p-(HBC[^/?]*)',
                ]
                
                stock_code = "Bulunamadı"
                for pattern in stock_code_patterns:
                    stock_code_match = re.search(pattern, href)
                    if stock_code_match:
                        stock_code = stock_code_match.group(1)
                        break
                
                product['stock_code'] = stock_code

            if product.get('name'):
                products.append(product)

        return products

    def save_to_excel(self, barcode: str, product: Dict, quantity: int = 1):
        """Ürün bilgisini Excel dosyasına kaydet"""
        filename = "bulunanlar.xlsx"
        
        # Ürün ismini adet bilgisiyle birleştir
        if quantity == 1:
            product_name_with_qty = product['name']
        else:
            product_name_with_qty = f"{product['name']} * {quantity} Adet"
        
        # Yeni veri
        new_data = {
            'BarkodNo': [barcode],
            'StokKodu': [product['stock_code']],
            'Ürünİsmi': [product_name_with_qty]
        }
        
        # Excel dosyası varsa oku, yoksa yeni oluştur
        try:
            df_existing = pd.read_excel(filename)
            df_new = pd.DataFrame(new_data)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        except FileNotFoundError:
            df_combined = pd.DataFrame(new_data)
        
        # Excel'e kaydet
        df_combined.to_excel(filename, index=False, engine='openpyxl')
        print(f"✅ Excel'e kaydedildi: {filename} ({quantity} adet)")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.found_products.append({
            'barcode': barcode,
            'stock_code': product['stock_code'],
            'name': product_name_with_qty,
            'quantity': quantity,
            'timestamp': timestamp
        })

    def delete_product(self, index: int):
        """Ürünü listeden ve Excel'den sil"""
        if not (0 <= index < len(self.found_products)):
            return False
        
        try:
            # Listedeki ürünü kaldır
            deleted_product = self.found_products.pop(index)
            
            # Excel dosyasını yeniden yaz
            filename = "bulunanlar.xlsx"
            if len(self.found_products) > 0:
                # Kalan ürünleri Excel'e yaz
                data = {
                    'BarkodNo': [p['barcode'] for p in self.found_products],
                    'StokKodu': [p['stock_code'] for p in self.found_products],
                    'Ürünİsmi': [p['name'] for p in self.found_products]
                }
                df = pd.DataFrame(data)
                df.to_excel(filename, index=False, engine='openpyxl')
            else:
                # Dosyayı sil
                import os
                if os.path.exists(filename):
                    os.remove(filename)
            
            print(f"✅ Silindi: {deleted_product['name']}")
            return True
            
        except Exception as e:
            print(f"❌ Silme hatası: {e}")
            return False

    def close(self):
        """Tarayıcıyı kapat"""
        if self.driver:
            self.driver.quit()
            print("🔚 Tarayıcı kapatıldı")


def main():
    print("🚀 Hepsiburada Barkod Arama")
    print("=" * 60)
    print("Komutlar:")
    print("  • Barkod numarası girin")
    print("  • 'list' - Bulunan ürünleri listele")
    print("  • 'delete' - Ürün sil")
    print("  • 'exit' - Çıkış")
    print("-" * 60)

    scraper = HepsiburadaScraper()

    try:
        while True:
            try:
                search_term = input("\n🔍 Barkod: ").strip()

                if not search_term:
                    print("❌ Boş olamaz!")
                    continue

                if search_term.lower() == 'exit':
                    print("👋 Program sonlandırılıyor...")
                    break

                if search_term.lower() == 'list':
                    if scraper.found_products:
                        print(f"\n📋 Bulunan {len(scraper.found_products)} ürün:")
                        for i, product in enumerate(scraper.found_products, 1):
                            print(f"{i}. {product['name']}")
                            print(f"   Barkod: {product['barcode']} | Stok Kodu: {product['stock_code']}")
                    else:
                        print("❌ Henüz ürün bulunmadı")
                    continue

                if search_term.lower() == 'delete':
                    if not scraper.found_products:
                        print("❌ Silinecek ürün bulunamadı")
                        continue
                    
                    print(f"\n📋 Silmek için bir ürün seçin (Toplam {len(scraper.found_products)} ürün):")
                    for i, product in enumerate(scraper.found_products, 1):
                        print(f"{i}. {product['name']}")
                        print(f"   Barkod: {product['barcode']} | Stok Kodu: {product['stock_code']}")
                    
                    while True:
                        try:
                            choice = input("\nSilmek istediğiniz ürün numarasını girin (0=iptal): ").strip()
                            if choice == '0':
                                print("❌ İptal edildi")
                                break
                            
                            choice_num = int(choice)
                            if 1 <= choice_num <= len(scraper.found_products):
                                scraper.delete_product(choice_num - 1)
                                break
                            else:
                                print(f"❌ Geçersiz seçim! Lütfen 1-{len(scraper.found_products)} arasında bir sayı girin.")
                        except ValueError:
                            print("❌ Lütfen geçerli bir sayı girin!")
                    continue

                html_content = scraper.get_html_content(search_term)

                if not html_content:
                    print("❌ HTML içeriği alınamadı!")
                    continue

                products = scraper.parse_products(html_content)

                if not products:
                    print("❌ Ürün bulunamadı")
                    continue

                # Tek ürün varsa direkt ekle
                if len(products) == 1:
                    print(f"✅ 1 ürün bulundu")
                    print(f"📦 Ürün: {products[0]['name']}")
                    print(f"📋 Stok Kodu: {products[0]['stock_code']}")
                    while True:
                        try:
                            qty_input = input("Adet girin (varsayılan: 1): ").strip()
                            if not qty_input:
                                quantity = 1
                            else:
                                quantity = int(qty_input)
                                if quantity <= 0:
                                    print("❌ Adet 0'dan büyük olmalı!")
                                    continue
                            break
                        except ValueError:
                            print("❌ Lütfen geçerli bir sayı girin!")
                    
                    scraper.save_to_excel(search_term, products[0], quantity)
                    
                # Birden fazla ürün varsa ilk 10'unu listele ve seçim sun
                else:
                    display_products = products[:10]
                    print(f"\n✅ {len(products)} ürün bulundu (İlk 10 tanesi listeleniyor):")
                    print("=" * 50)

                    for i, product in enumerate(display_products, 1):
                        print(f"{i}. {product['name']}")
                        print(f"   Stok Kodu: {product['stock_code']}")
                        print()
                    
                    while True:
                        try:
                            choice = input("Hangi ürünü eklemek istersiniz? (1-10, 0=iptal): ").strip()
                            
                            if choice == '0':
                                print("❌ İptal edildi")
                                break
                            
                            choice_num = int(choice)
                            if 1 <= choice_num <= len(display_products):
                                selected_product = display_products[choice_num - 1]
                                
                                # Adet sor
                                while True:
                                    try:
                                        qty_input = input("Adet girin (varsayılan: 1): ").strip()
                                        if not qty_input:
                                            quantity = 1
                                        else:
                                            quantity = int(qty_input)
                                            if quantity <= 0:
                                                print("❌ Adet 0'dan büyük olmalı!")
                                                continue
                                        break
                                    except ValueError:
                                        print("❌ Lütfen geçerli bir sayı girin!")
                                
                                scraper.save_to_excel(search_term, selected_product, quantity)
                                break
                else:
                                print("❌ Geçersiz seçim! Lütfen 1-10 arasında bir sayı girin.")
                        except ValueError:
                            print("❌ Lütfen geçerli bir sayı girin!")

            except KeyboardInterrupt:
                print("\n👋 Program sonlandırılıyor...")
                break
            except Exception as e:
                print(f"❌ Hata: {e}")
                continue

    finally:
        scraper.close()


if __name__ == "__main__":
    main()
