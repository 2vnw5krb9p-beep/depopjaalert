import os
import json
import requests
from playwright.sync_api import sync_playwright

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

SEARCH_URL = "https://www.depop.com/search/?q=James%20Avery"

MEMORY_FILE = "seen_listings.json"


def send_telegram(message):
    response = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": message,
            "disable_web_page_preview": False,
        },
        timeout=20,
    )
    response.raise_for_status()


try:
    with open(MEMORY_FILE, "r") as f:
        seen = set(json.load(f))
except (FileNotFoundError, json.JSONDecodeError):
    seen = set()


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    page = browser.new_page(
        user_agent=(
            "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/18.0 Mobile/15E148 Safari/604.1"
        )
    )

    page.goto(SEARCH_URL, wait_until="domcontentloaded", timeout=60000)

    page.wait_for_timeout(5000)

    links = page.locator('a[href*="/products/"]').all()

    found = set()

    for link in links:
        href = link.get_attribute("href")

        if not href:
            continue

        if href.startswith("/"):
            href = "https://www.depop.com" + href

        href = href.split("?")[0].rstrip("/")

        found.add(href)

    browser.close()


send_telegram(
    "🧪 TEST\n"
    "Depop browser loaded successfully.\n"
    f"Product links found: {len(found)}"
)


for url in found:
    product_id = url.split("/products/")[-1]

    if not product_id or product_id in seen:
        continue

    message = (
        "🔔 NEW JAMES AVERY ON DEPOP!\n\n"
        f"🔗 {url}"
    )

    send_telegram(message)
    seen.add(product_id)


with open(MEMORY_FILE, "w") as f:
    json.dump(list(seen), f)
