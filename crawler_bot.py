import requests
import time
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# ================= CONFIG =================
MOOMLE_API = "https://moomle.ir/api/add-url.php"
API_TOKEN = "CHANGE_ME_SECRET"

SEED_SITES = [
    "https://fa.wikipedia.org",
    "https://www.isna.ir",
    "https://www.mehrnews.com",
    "https://www.zoomit.ir",
    "https://www.tabnak.ir",
]

MAX_LINKS_PER_SITE = 50
DELAY = 2  # ثانیه بین درخواست‌ها
# ==========================================


def is_persian(text: str) -> bool:
    return bool(re.search(r'[\u0600-\u06FF]', text))


def looks_like_article(url: str) -> bool:
    bad_words = ["login", "register", "tag", "category", "author", "search"]
    return (
        len(url) > 30
        and any(char.isdigit() for char in url)
        and not any(b in url for b in bad_words)
    )


def extract_links(base_url: str) -> list[str]:
    links = set()

    try:
        r = requests.get(base_url, timeout=15, headers={
            "User-Agent": "MoomleBot/0.1"
        })
        r.raise_for_status()
    except Exception as e:
        print(f"⚠️ خطا در دریافت {base_url}: {e}")
        return []

    soup = BeautifulSoup(r.text, "lxml")

    text = soup.get_text(" ", strip=True)
    if not is_persian(text):
        print(f"⛔ غیر فارسی: {base_url}")
        return []

    for a in soup.find_all("a", href=True):
        url = urljoin(base_url, a["href"])
        parsed = urlparse(url)

        if parsed.scheme not in ("http", "https"):
            continue

        url = parsed.scheme + "://" + parsed.netloc + parsed.path

        if looks_like_article(url):
            links.add(url)

        if len(links) >= MAX_LINKS_PER_SITE:
            break

    return list(links)


def send_to_moomle(url: str):
    try:
        r = requests.post(
            MOOMLE_API,
            json={"url": url, "token": API_TOKEN},
            timeout=10
        )
        if r.status_code == 200:
            print(f"✅ ارسال شد: {url}")
        else:
            print(f"❌ رد شد: {url} ({r.status_code})")
    except Exception as e:
        print(f"⚠️ خطا ارسال {url}: {e}")


def main():
    print("🚀 شروع ربات مومل")

    for site in SEED_SITES:
        print(f"\n🌐 بررسی سایت: {site}")
        links = extract_links(site)

        if not links:
            print("⛔ لینکی پیدا نشد")
            continue

        for link in links:
            send_to_moomle(link)
            time.sleep(1)

        time.sleep(DELAY)

    print("\n🎯 پایان اجرا")


if __name__ == "__main__":
    main()
