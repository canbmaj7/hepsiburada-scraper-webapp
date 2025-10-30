import re
import sys
import argparse
import requests
from typing import List

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def parse_google_titles(html: str) -> List[str]:
    """Google SERP HTML içinden başlıkları çıkarır.
    Birden fazla selector ile daha dayanıklı hale getirildi.
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
        print(f"Parse hatası: {e}", file=sys.stderr)
        return []


def parse_duck_titles(html: str) -> List[str]:
    try:
        titles = re.findall(r'<a[^>]*class="[^\"]*result__a[^\"]*"[^>]*>(.*?)</a>', html, re.DOTALL)
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
        print(f"Duck parse hatası: {e}", file=sys.stderr)
        return []


def parse_bing_titles(html: str) -> List[str]:
    try:
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
        print(f"Bing parse hatası: {e}", file=sys.stderr)
        return []


def google_search(query: str) -> tuple[List[str], str]:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
        'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Referer': 'https://www.google.com/'
    }
    urls = [
        f"https://www.google.com/search?q={query}&hl=tr&gl=tr&pws=0&num=20&udm=14",
        f"https://www.google.com/search?client=firefox-b-d&q={query}&hl=tr&gl=tr&num=20&pws=0",
        f"https://www.google.com/search?q={query}&hl=tr&gl=tr&pws=0&num=20&gbv=1&nfpr=1&filter=0",
    ]

    session = requests.Session()
    session.headers.update(headers)
    session.cookies.set('CONSENT', 'YES+1', domain='.google.com')

    for url in urls:
        try:
            resp = session.get(url, timeout=12)
            print(f"GET {url} -> {resp.status_code}")
            if resp.status_code == 200 and len(resp.text) > 500:
                if 'consent.google.com' in resp.text.lower():
                    print("Consent sayfası algılandı, diğer varyanta geçiliyor...")
                    continue
                titles = parse_google_titles(resp.text)
                if titles:
                    return titles, 'google'
        except requests.RequestException as e:
            print(f"İstek hatası: {e}", file=sys.stderr)

    # Google 0 dönerse DuckDuckGo HTML dene
    try:
        ddg_resp = session.post('https://html.duckduckgo.com/html/', data={'q': query}, timeout=12)
        print(f"POST https://html.duckduckgo.com/html/ -> {ddg_resp.status_code}")
        if ddg_resp.status_code == 200:
            titles = parse_duck_titles(ddg_resp.text)
            if titles:
                return titles, 'duckduckgo'
    except requests.RequestException as e:
        print(f"DDG istek hatası: {e}", file=sys.stderr)

    # Son olarak Bing
    try:
        bing_resp = session.get(f'https://www.bing.com/search?q={query}', timeout=12)
        print(f"GET https://www.bing.com/search?q=... -> {bing_resp.status_code}")
        if bing_resp.status_code == 200:
            titles = parse_bing_titles(bing_resp.text)
            if titles:
                return titles, 'bing'
    except requests.RequestException as e:
        print(f"Bing istek hatası: {e}", file=sys.stderr)

    return [], ''


def selenium_google_search(query: str) -> List[str]:
    """Selenium ile Google sonuç başlıklarını getirir."""
    try:
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1280,800")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

        service = Service('chromedriver.exe')
        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.set_page_load_timeout(15)

        url = f"https://www.google.com/search?q={query}&hl=tr&gl=tr&pws=0"
        driver.get(url)

        wait = WebDriverWait(driver, 8)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        # Kısa kaydırmalar
        driver.execute_script("window.scrollTo(0, 600);")
        driver.execute_script("window.scrollTo(0, 1200);")

        html = driver.page_source
        titles = parse_google_titles(html)
        driver.quit()
        return titles
    except Exception as e:
        print(f"Selenium hatası: {e}", file=sys.stderr)
        try:
            driver.quit()
        except Exception:
            pass
        return []


def main():
    parser = argparse.ArgumentParser(description='Google başlık testi (HTML parse)')
    parser.add_argument('query', nargs='+', help='Arama terimi')
    parser.add_argument('--selenium', action='store_true', help='Google sonuçlarını Selenium ile çek')
    args = parser.parse_args()
    query = '+'.join(args.query)

    if args.selenium:
        titles = selenium_google_search(query)
        engine = 'google-selenium' if titles else ''
    else:
        titles, engine = google_search(query)
    if not titles:
        print("❌ Sonuç bulunamadı veya engellendi.")
        sys.exit(2)

    print(f"✅ {len(titles)} başlık bulundu (kaynak: {engine}):\n")
    for i, t in enumerate(titles, 1):
        print(f"{i:02d}. {t}")


if __name__ == '__main__':
    main()


