# GitHub'a Manuel Yükleme Talimatları

Git kurulu olmadığı için **GitHub Web UI** ile yükleyebilirsiniz.

## Yöntem 1: GitHub Web UI ile Yükleme (Kolay)

### Adımlar:

1. **GitHub'da dosyaları yükleyin:**
   - https://github.com/canbmaj7/hepsiburada-scraper-webapp.git adresine gidin
   - Sağ üstte "uploading an existing file" seçeneğini bulun
   - veya boş repository'de "Add file" > "Upload files" tıklayın

2. **Yüklenecek dosyalar:**
   ```
   app.py
   hepsiburada.py
   chromedriver.exe
   create_icon.py
   app_icon.ico
   app_icon.png
   build_exe.bat
   env_template.txt
   requirements.txt
   README.md
   .gitignore
   GITHUB_SETUP.md
   GITHUB_UPLOAD_INSTRUCTIONS.md
   README_GOOGLE_SHEETS.md
   templates/
     ├── index.html
     └── login.html
   ```

3. **Commit mesajı:**
   ```
   Initial commit: Hepsiburada Toplu Ürün Arama Sistemi
   ```

4. **Commit butonuna tıklayın**

## Yöntem 2: GitHub Desktop (Eğer kurarsanız)

1. [GitHub Desktop](https://desktop.github.com/) indirin ve kurun
2. File > Clone Repository
3. URL: `https://github.com/canbmaj7/hepsiburada-scraper-webapp.git`
4. Clone butonuna tıklayın
5. Klasöre gidin ve tüm dosyaları kopyalayın
6. GitHub Desktop'ta "Changes" sekmesinde tüm dosyaları göreceksiniz
7. Commit message: `Initial commit: Hepsiburada Toplu Ürün Arama Sistemi`
8. "Commit to main" ve "Push origin" butonlarına tıklayın

## Yöntem 3: Git Kurup Komutla Yükleme

Eğer Git kurmayı tercih ederseniz:

### 1. Git İndirin:
https://git-scm.com/download/win

### 2. Terminal/Komut Satırından:

```bash
# Git config
git config --global user.name "Ahmet Can Otlu"
git config --global user.email "ahmetcanotlu@gmail.com"

# Repository'ye bağlan
cd "C:\Users\ahmet.otlu\Desktop\can\hepsiburada"
git init
git remote add origin https://github.com/canbmaj7/hepsiburada-scraper-webapp.git

# Dosyaları ekle
git add .

# Commit
git commit -m "Initial commit: Hepsiburada Toplu Ürün Arama Sistemi

- Web-based ürün arama sistemi
- Google Sheets entegrasyonu
- Excel export özelliği
- EXE build desteği
- Modern UI/UX"

# Push
git push -u origin main
```

## Repository Ayarları

### GitHub'da Şunları Ekleyin:

1. **About kısmı:**
   - Description: `🛒 Hepsiburada Toplu Ürün Arama ve Envanter Yönetim Sistemi`
   - Website: (opsiyonel)
   - Topics: `python`, `flask`, `selenium`, `web-scraping`, `e-commerce`, `hepsiburada`, `inventory-management`

2. **Settings > Pages:**
   - Source: None (uygulama Flask backend gerektirir)

## Dosyalar Özeti

✅ **Mutlaka dahil:**
- app.py (ana uygulama)
- templates/ klasörü
- README.md
- requirements.txt
- .gitignore
- build_exe.bat
- env_template.txt

✅ **Opsiyonel:**
- chromedriver.exe (büyük dosya, GitHub'a ekleyebilirsiniz)
- app_icon.ico, app_icon.png
- hepsiburada.py (CLI versiyonu)

❌ **Eklemeyin:**
- .env (güvenlik riski)
- __pycache__/
- build/, dist/
- *.xlsx dosyaları

## Tamamlandıktan Sonra

Repository link'i:
```
https://github.com/canbmaj7/hepsiburada-scraper-webapp
```

Clone için:
```bash
git clone https://github.com/canbmaj7/hepsiburada-scraper-webapp.git
```

