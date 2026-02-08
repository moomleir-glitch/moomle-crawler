import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# سایت‌های شروع (Seed)
SEED_SITES = [
    "https://fa.wikipedia.org",
    "https://www.isna.ir",
    "https://www.mehrnews.com",
]

visited = set()
found_links = set()

def crawl(url, max_links=20):
    print(f"\n🌐 Crawling: {url}")

    try:
        r = requests.get(url, timeout=10, headers={
            "User-Agent": "MoomleBot/0.1"
        })
    except Exception as e:
        print("❌ خطا:", e)
        return

    soup = BeautifulSoup(r.text, "lxml")

    for a in soup.find_all("a", href=True):
        link = a["href"]

        # تبدیل لینک نسبی به کامل
        link = urljoin(url, link)

        # فقط http / https
        if not link.startswith("http"):
            continue

        # حذف تکراری
        if link in visited:
            continue

        # حذف فایل‌ها
        if any(link.lower().endswith(ext) for ext in [".jpg",".png",".pdf",".zip"]):
            continue

        visited.add(link)
        found_links.add(link)

        print("🔗", link)

        if len(found_links) >= max_links:
            break


if __name__ == "__main__":
    for site in SEED_SITES:
        crawl(site)

    print("\n✅ پایان تست")
    print(f"📊 تعداد لینک کشف‌شده: {len(found_links)}")
