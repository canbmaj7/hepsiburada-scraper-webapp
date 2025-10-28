# 🛒 Hepsiburada Toplu Ürün Arama Sistemi

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![Selenium](https://img.shields.io/badge/Selenium-4.16.0-orange.svg)](https://selenium-python.readthedocs.io/)

Modern, hızlı ve kullanıcı dostu bir Hepsiburada toplu ürün arama ve envanter yönetim uygulaması.

**Geliştirici:** [Ahmet Can Otlu](mailto:ahmetcanotlu@gmail.com) | **Email:** ahmetcanotlu@gmail.com

## 📋 Özellikler

- ✅ **Barkod/Ürün Arama**: Barkod numarası veya ürün ismiyle arama yapın
- ✅ **Ürün Listeleme**: Bulunan ürünleri görselleriyle birlikte görüntüleyin
- ✅ **Sayfalama**: Her sayfada 16 ürün gösterilir, tüm sonuçlar listelenir
- ✅ **Miktar Yönetimi**: +/- butonları ile miktar ayarlayın
- ✅ **Sepet Yönetimi**: Ürünleri sepete ekleyin, çıkarın, miktar değiştirin
- ✅ **Toplu İşlemler**: Sepeti tamamen temizleyin
- ✅ **Excel Export**: Sepetteki ürünleri Excel formatında dışa aktarın
- ✅ **Arama Geçmişi**: Son arananları tek tıkla yeniden arayın
- ✅ **Şifre Koruma**: Google Sheets entegrasyonu ile dinamik şifre yönetimi
- ✅ **Tema Desteği**: Açık ve karanlık tema
- ✅ **Hızlı UI**: Modern, responsive ve hızlı arayüz

## 🚀 Kurulum

### Gereksinimler

- Python 3.8+
- Chrome tarayıcı
- İnternet bağlantısı

### Adımlar

1. **Repository'yi klonlayın:**
```bash
git clone https://github.com/ahmetcanotlu/hepsiburada-urun-arama.git
cd hepsiburada-urun-arama
```

2. **Bağımlılıkları yükleyin:**
```bash
pip install -r requirements.txt
```

3. **Google Sheets Yapılandırması:**
```bash
# .env dosyası oluşturun
copy env_template.txt .env

# .env dosyasını düzenleyin
# GOOGLE_SHEET_URL=your_google_sheets_csv_export_url
# DEVELOPMENT_MODE=False
```

4. **ChromeDriver:**
Proje `chromedriver.exe` içerir. Gerekirse [Selenium](https://www.selenium.dev/downloads/)'dan indirebilirsiniz.

5. **Uygulamayı çalıştırın:**
```bash
python app.py
```

Tarayıcı otomatik olarak http://127.0.0.1:5000 adresinde açılacaktır.

## 📦 EXE Oluşturma

Uygulamayı Windows'ta standalone EXE olarak derlemek için:

```bash
build_exe.bat
```

EXE dosyası `dist\HepsiburadaArama.exe` olarak oluşturulacaktır.

## 🎨 Kullanım

### Arama Yapma
1. Üst kısımdaki arama kutusuna barkod veya ürün ismi girin
2. "🔍 Ara" butonuna tıklayın
3. Sonuçlar listelenecektir

### Ürün Ekleme
1. Ürün kartında +/- butonları ile miktar seçin
2. "Sepete Ekle" butonuna tıklayın
3. Ürün sepete eklenecektir

### Sepet Yönetimi
- **+/- Butonları**: Miktarı artırın/azaltın
- **Sil Butonu**: Ürünü sepetten çıkarın
- **Sepeti Temizle**: Tüm ürünleri bir anda silin
- **Excel'e Aktar**: Sepeti Excel dosyası olarak indirin

### Son Aramalar
Sayfanın alt kısmında son yaptığınız 5 arama görünür. İstediğiniz aramaya tıklayarak hızlıca yeniden arayabilirsiniz.

## 🔐 Şifre Yönetimi

### Google Sheets Entegrasyonu

Uygulama, Google Sheets'teki B5 hücresinden şifre alır. Şifreyi değiştirdiğinizde, kullanıcılar bir sonraki login'de yeni şifreyi kullanırlar.

**Google Sheets Formatı:**
```
| A            | B        |
|--------------|----------|
| Örnek 1      | şifre1   |
| Örnek 2      | şifre2   |
| Örnek 3      | şifre3   |
| Örnek 4      | şifre4   |
| Örnek 5      | şifre5   |  ← B5 (Şifre buraya yazılır)
```

### CSV Export URL

Google Sheets'inizi CSV formatında export edebilirsiniz:
```
https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/export?format=csv
```

`.env` dosyasında `GOOGLE_SHEET_URL` olarak bu URL'yi ekleyin.

### Development Mode

Geliştirme yaparken şifre kontrolünü atlamak için:
```env
DEVELOPMENT_MODE=True
```

## 🛠️ Teknolojiler

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Web Scraping**: Selenium WebDriver
- **Veri İşleme**: Pandas, OpenPyXL
- **Export**: Excel (.xlsx)

## 📁 Proje Yapısı

```
hepsiburada-urun-arama/
├── app.py                      # Ana Flask uygulaması
├── hepsiburada.py              # CLI versiyonu
├── templates/
│   ├── index.html              # Ana UI
│   └── login.html              # Şifre ekranı
├── chromedriver.exe            # Chrome driver
├── build_exe.bat               # EXE build script
├── create_icon.py              # Icon oluşturucu
├── env_template.txt            # .env template
├── requirements.txt            # Python bağımlılıkları
└── README.md                   # Bu dosya
```

## ⚙️ Yapılandırma

### .env Dosyası

`.env` dosyasında şu değişkenleri ayarlayabilirsiniz:

```env
# Google Sheets CSV URL (zorunlu - production)
GOOGLE_SHEET_URL=https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/export?format=csv

# Geliştirme modu (şifre kontrolünü atla)
DEVELOPMENT_MODE=False
```

## 🎯 Kullanım Senaryoları

1. **Mağaza Envanter Yönetimi**: Ürünleri hızlıca arayın ve sepete ekleyin
2. **Fiyat Karşılaştırma**: Ürün fiyatlarını toplu halde karşılaştırın
3. **Stok Takibi**: Excel export ile stok takibi yapın
4. **Sipariş Hazırlama**: Sepet ile sipariş hazırlayın

## 🐛 Sorun Giderme

### ChromeDriver Hatası
Chrome sürümünüze uygun ChromeDriver indirin ve `chromedriver.exe` olarak değiştirin.

### Şifre Çalışmıyor
- `.env` dosyasını kontrol edin
- Google Sheets CSV URL'ini kontrol edin
- B5 hücresinde şifre olduğundan emin olun

### Ürün Bulunamıyor
- Barkod numarasını doğru girin
- İnternet bağlantınızı kontrol edin
- Hepsiburada.com erişilebilir mi kontrol edin

## 📝 Lisans

Bu proje kişisel kullanım için geliştirilmiştir.

## 👤 İletişim

**Geliştirici**: Ahmet Can Otlu
**Email**: ahmetcanotlu@gmail.com

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Commit yapın (`git commit -m 'Add some AmazingFeature'`)
4. Branch'i push edin (`git push origin feature/AmazingFeature`)
5. Pull Request açın

## 📊 Versiyon Geçmişi

### v1.0.0 (Mevcut)
- ✅ İlk stable sürüm
- ✅ Google Sheets entegrasyonu
- ✅ Sayfalama sistemi
- ✅ Excel export
- ✅ Şifre koruma
- ✅ EXE build desteği

## 💡 Gelecek Özellikler

- [ ] Mobil uyumluluk
- [ ] Favoriler listesi
- [ ] Bildirimler
- [ ] Database entegrasyonu
- [ ] Çoklu dil desteği

---

⭐ Projeyi beğendiyseniz yıldız vermeyi unutmayın!

