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
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept-Language': 'en-GB,en;q=0.9'
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        cards = soup.select('.wrapper-box')
        print(f"🧪 Found {len(cards)} cards on page {page}")

        if not cards:
            print("✅ No more items. Done scraping.")
            break

        for card in cards:
            try:
                name_elem = card.select_one('.card-title a')
                price_elem = card.select_one('.product-main-price')

                # Debug log
                print("🔎 Card Found:", {
                    "name": name_elem.get_text(strip=True) if name_elem else None,
                    "price": price_elem.get_text(strip=True) if price_elem else None
                })

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

    print(f"\n📦 Scraped {len(all_data)} GPUs. Sample data:")
    for entry in all_data[:5]:
        print(entry)

    # Upload to Supabase
    for entry in all_data:
        supabase.table("gpu_prices").insert(entry).execute()

    print("✅ Scraping complete.")
