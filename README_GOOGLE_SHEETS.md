# Google Sheets Entegrasyonu

## Kurulum

### 1. `.env` Dosyası Oluşturun

Projenin ana dizininde `.env` dosyası oluşturun:

```env
# Google Sheets URL (CSV formatında)
GOOGLE_SHEET_URL=https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/export?format=csv

# Geliştirme Modu (şifre kontrolünü atla)
DEVELOPMENT_MODE=False
```

### 2. Google Sheets Hazırlığı

Google Sheets'inizde şu formatta veri olmalı:

| A              | B           |
|----------------|-------------|
| Örnek 1        | şifre1      |
| Örnek 2        | şifre2      |
| Örnek 3        | şifre3      |
| Örnek 4        | şifre4      |
| Örnek 5        | şifre5      |

**Not:** B5 hücresindeki değer (son satır) şifre olarak kullanılacak.

### 3. CSV Export URL'si

Google Sheets'inizi CSV olarak export etmek için URL formatı:

```
https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/export?format=csv
```

Veya gid parametresi varsa:

```
https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/export?format=csv&gid=0
```

### 4. Kullanım

#### Geliştirme Modu (Şifre Yok):
```env
DEVELOPMENT_MODE=True
```

#### Production Modu (Şifre Gerekli):
```env
DEVELOPMENT_MODE=False
GOOGLE_SHEET_URL=https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/export?format=csv
```

## Önemli Notlar

- `.env` dosyası **asla** git'e commit edilmemeli
- `env_template.txt` dosyası template olarak kullanılır
- EXE'yi oluştururken `.env` dosyasını da içine ekleyin (gerekirse)
- Google Sheets'te B5 hücresindeki değer şifre olarak kullanılır

## Test

```bash
python app.py
```

Şifre doğru çalışıp çalışmadığını kontrol edin. Konsolda şu mesajı görmelisiniz:

```
✅ Şifre Google Sheets'ten alındı: [şifre]
```

