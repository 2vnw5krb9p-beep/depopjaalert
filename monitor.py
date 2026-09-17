import os
import json
import requests

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

SEARCH_URL = "https://www.depop.com/presentation/api/v1/search/products/"

headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X)"
}

params = {
    "what": "James Avery",
    "limit": 100,
    "country": "us",
    "currency": "USD",
    "from": "in_country_search",
    "include_like_count": "true",
}

response = requests.get(
    SEARCH_URL,
    params=params,
    headers=headers,
    timeout=30
)

response.raise_for_status()
data = response.json()

products = data.get("products", [])

# Remember listings we've already alerted you about.
memory_file = "seen_listings.json"

try:
    with open(memory_file, "r") as f:
        seen = set(json.load(f))
except:
    seen = set()

for item in products:
    product_id = str(
        item.get("id")
        or item.get("productId")
        or item.get("product_id")
        or ""
    )

    if not product_id or product_id in seen:
        continue

    title = item.get("title") or item.get("name") or "James Avery item"

    price = item.get("price", "Unknown")

    if isinstance(price, dict):
        price = price.get("amount") or price.get("current") or "Unknown"

    slug = item.get("slug")

    if slug:
        url = f"https://www.depop.com/products/{slug}/"
    else:
        url = "https://www.depop.com/search/?q=James+Avery"

    message = (
        "🔔 NEW JAMES AVERY ON DEPOP!\n\n"
        f"🏷️ {title}\n"
        f"💰 ${price}\n\n"
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
