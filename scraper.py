import requests
from bs4 import BeautifulSoup
from db import supabase
import datetime

def scrape_cex():
    page = 1
    base_url = "https://uk.webuy.com/search?categoryIds=892&categoryName=Graphics%20Cards%20-%20PCI-E"
    all_data = []

    while True:
        print(f"🔍 Scraping page {page}...")
        url = f"{base_url}&page={page}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        cards = soup.select('.wrapper-box')
        if not cards:
            print("✅ No more items. Done scraping.")
            break

        for card in cards:
            try:
                name_elem = card.select_one('.card-title a')
                price_elem = card.select_one('.product-main-price')

                if not name_elem or not price_elem:
                    continue

                name = name_elem.get_text(strip=True)
                price_text = price_elem.get_text(strip=True)
                buy_price = float(price_text.replace('£', '').strip())

                all_data.append({
                    "gpu_name": name,
                    "sell_cash": None,
                    "sell_store": None,
                    "buy_price": buy_price,
                    "date_tracked": str(datetime.date.today())
                })
            except Exception as e:
                print("⚠️ Error parsing card:", e)

        page += 1

    print(f"📦 Scraped {len(all_data)} GPUs. Sample:")
    for entry in all_data[:5]:
        print(entry)

    for entry in all_data:
        supabase.table("gpu_prices").insert(entry).execute()

    print("✅ Scraping complete.")
