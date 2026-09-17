import os
import json
import re
import requests

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

URL = "https://www.depop.com/brands/james-avery/"

headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1"
}

response = requests.get(URL, headers=headers, timeout=30)
response.raise_for_status()

html = response.text

# Find Depop product URLs contained in the public page.
urls = set(
    re.findall(
        r'https://www\.depop\.com/products/[^"\\?]+',
        html
    )
)

memory_file = "seen_listings.json"

try:
    with open(memory_file, "r") as f:
        seen = set(json.load(f))
except:
    seen = set()

for url in urls:
    url = url.rstrip("/")

    product_id = url.split("/products/")[-1]

    if not product_id or product_id in seen:
        continue

    message = (
        "🔔 NEW JAMES AVERY ON DEPOP!\n\n"
        f"🔗 {url}"
    )

    telegram_url = (
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    )

    requests.post(
        telegram_url,
        data={
            "chat_id": CHAT_ID,
            "text": message,
            "disable_web_page_preview": False,
        },
        timeout=20,
    ).raise_for_status()

    seen.add(product_id)

with open(memory_file, "w") as f:
    json.dump(list(seen), f)
