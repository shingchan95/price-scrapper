import requests
from bs4 import BeautifulSoup
from db import get_db_connection
import datetime

def scrape_cex():
    url = "https://uk.webuy.com/search?categoryIds=892&categoryName=Graphics%20Cards%20-%20PCI-E"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    items = soup.select('.searchRecord')

    conn = get_db_connection()
    cursor = conn.cursor()

    for item in items:
        name = item.select_one('.desc').get_text(strip=True)

        # Price tags
        price_tags = item.select('.priceTxt')

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
            cursor.execute(
                "INSERT INTO gpu_prices (gpu_name, sell_cash, sell_store, buy_price, date_tracked) VALUES (%s, %s, %s, %s, %s)",
                (name, sell_cash, sell_store, buy_price, datetime.date.today())
            )

    conn.commit()
    cursor.close()
    conn.close()
