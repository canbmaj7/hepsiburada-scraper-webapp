@echo off
echo ====================================
echo Hepsiburada Arama - EXE Olusturma
echo ====================================
echo.

REM Eski build dosyalarını temizle
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist HepsiburadaArama.spec del HepsiburadaArama.spec

echo.
echo [1/3] Icon olusturuluyor...
python create_icon.py

echo.
echo [2/3] EXE olusturuluyor (bu biraz zaman alabilir)...
python -m PyInstaller --onefile ^
    --name "HepsiburadaArama" ^
    --icon="app_icon.ico" ^
    --runtime-tmpdir "%LOCALAPPDATA%\HBAppRuntime" ^
    --add-data "chromedriver.exe;." ^
    --add-data "templates;templates" ^
    --add-data ".env;." ^
    --hidden-import=flask ^
    --hidden-import=selenium ^
    --hidden-import=pandas ^
    --hidden-import=openpyxl ^
    --hidden-import=webbrowser ^
    --hidden-import=threading ^
    --hidden-import=ctypes ^
    --hidden-import=dotenv ^
    --hidden-import=requests ^
    --hidden-import=urllib3 ^
    --hidden-import=certifi ^
    --hidden-import=charset_normalizer ^
    --collect-all=selenium ^
    --collect-all=flask ^
    app.py

echo.
echo [3/3] Kontrol...
if exist dist\HepsiburadaArama.exe (
    echo.
    echo ====================================
    echo ✅ BASARILI!
    echo ====================================
    echo.
    echo EXE dosyasi: dist\HepsiburadaArama.exe
    echo.
    echo Dosyayi calistirmak icin:
    echo   dist\HepsiburadaArama.exe
    echo.
) else (
    echo.
    echo ====================================
    echo ❌ HATA!
    echo ====================================
    echo.
    echo EXE olusturulamadi!
    echo.
)

pause

