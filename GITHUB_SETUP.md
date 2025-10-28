# GitHub'a Yükleme Adımları

## 1. Git Repository Oluşturun

GitHub'da yeni bir repository oluşturun:
- Repository name: `hepsiburada-urun-arama`
- Description: `Modern Hepsiburada ürün arama ve sepet yönetim uygulaması`
- Public veya Private seçin
- Initialize this repository with a README seçmeyin (zaten README.md var)

## 2. Terminal'den Commit ve Push Yapın

```bash
# Git'i başlatın (henüz yapmadıysanız)
git init

# Dosyaları ekleyin
git add .

# İlk commit
git commit -m "Initial commit: Hepsiburada Ürün Arama Sistemi"

# Remote ekleyin (GitHub'dan aldığınız URL)
git remote add origin https://github.com/YOUR_USERNAME/hepsiburada-urun-arama.git

# Branch'e push edin
git branch -M main
git push -u origin main
```

## 3. GitHub URL'i

Repository oluşturduktan sonra GitHub size şöyle bir URL verir:
```
https://github.com/YOUR_USERNAME/hepsiburada-urun-arama.git
```

Bu URL'yi yukarıdaki `git remote add origin` komutunda kullanın.

## 4. Sonraki Değişiklikler

Kodda değişiklik yaptığınızda:

```bash
git add .
git commit -m "Değişiklik açıklaması"
git push
```

## 5. Repository Ayarları (Opsiyonel)

GitHub repository sayfasında:
- **About** bölümüne açıklama ekleyin
- **Topics** bölümüne şunları ekleyin: `python`, `flask`, `selenium`, `web-scraping`, `hepsiburada`
- **Website** bölümüne `.env` dosyasındaki URL'i ekleyebilirsiniz

## 6. Dosya Yapısı Kontrolü

GitHub'a push edilmemesi gereken dosyalar `.gitignore` içinde:
- `.env` (güvenlik)
- `*.xlsx` (üretilen dosyalar)
- `build/`, `dist/` (derleme dosyaları)
- `__pycache__/` (Python cache)

## 7. GitHub Pages (Opsiyonel)

Eğer canlı demo yayınlamak isterseniz:
1. Repository Settings
2. Pages
3. Source: `main` branch seçin
4. Save

Ancak bu uygulama Flask backend gerektirdiği için Pages'te çalışmaz. Alternatif olarak:
- Heroku
- Railway
- PythonAnywhere

kullanabilirsiniz.

## 8. LICENSE Dosyası (Opsiyonel)

Proje root'una `LICENSE` dosyası ekleyebilirsiniz:

```bash
# GitHub'dan direkt LICENSE ekleyebilirsiniz
# veya https://choosealicense.com/ sitesinden seçebilirsiniz
```

## İletişim Bilgileri

README.md içinde zaten email adresiniz var:
- **Email**: ahmetcanotlu@gmail.com

## GitHub Profili İçin

Profile README oluşturmak isterseniz:
1. GitHub'da kendi profilinizde yeni bir repo oluşturun
2. Repo adı: `YOUR_USERNAME/YOUR_USERNAME` (kullanıcı adınızla aynı)
3. İçine `README.md` ekleyin
4. Profile sayfanızda görünecek

