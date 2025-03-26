import requests
from bs4 import BeautifulSoup
from db import get_db_connection
import datetime

def scrape_cex():
    page = 1
    base_url = "https://uk.webuy.com/search?categoryIds=892&categoryName=Graphics%20Cards%20-%20PCI-E"

    all_data = []

    while True:
        print(f"Scraping page {page}...")
        url = f"{base_url}&page={page}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        cards = soup.select('.searchRecord')

        # Stop if no more items found
        if not cards:
            print("No more items. Done scraping.")
            break

        for card in cards:
            try:
                name = card.select_one('.desc').get_text(strip=True)

                price_tags = card.select('.priceTxt')
                buy_price = sell_cash = sell_store = None

                for tag in price_tags:
                    text = tag.get_text(strip=True)
                    if 'WeSell for' in text:
                        buy_price = float(text.replace('WeSell for £', '').strip())
                    elif 'WeBuy for Cash' in text:
                        sell_cash = float(text.replace('WeBuy for Cash £', '').strip())
                    elif 'WeBuy for Voucher' in text:
                        sell_store = float(text.replace('WeBuy for Voucher £', '').strip())

                if name and buy_price is not None:
                    all_data.append((name, sell_cash, sell_store, buy_price))
            except Exception as e:
                print("Error parsing card:", e)

        page += 1

    # Insert all data into DB
    print(f"Inserting {len(all_data)} items into DB...")
    conn = get_db_connection()
    cursor = conn.cursor()

    for model, sell_cash, sell_store, buy_price in all_data:
        cursor.execute(
            "INSERT INTO gpu_prices (gpu_name, sell_cash, sell_store, buy_price, date_tracked) VALUES (%s, %s, %s, %s, %s)",
            (model, sell_cash, sell_store, buy_price, datetime.date.today())
        )

    conn.commit()
    cursor.close()
    conn.close()
    print("Scraping complete.")
