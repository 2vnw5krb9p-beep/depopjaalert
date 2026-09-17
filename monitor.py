import os
import json
import requests
from bs4 import BeautifulSoup

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

SEARCH_URL = "https://www.depop.com/search/?q=James%20Avery"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/18.0 Mobile/15E148 Safari/604.1"
    )
}

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

response = requests.get(
    SEARCH_URL,
    headers=HEADERS,
    timeout=30,
)

response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

print("Depop response length:", len(response.text))
print("Product links found in HTML:", response.text.count("/products/"))

print(response.text[:2000])

found = set()

for link in soup.find_all("a", href=True):
    href = link["href"]

    if "/products/" not in href:
        continue

    if href.startswith("/"):
        href = "https://www.depop.com" + href

    href = href.split("?")[0].rstrip("/")

    found.add(href)

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
