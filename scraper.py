import requests
from bs4 import BeautifulSoup
from db import supabase
import datetime

def scrape_cex():
    page = 1
    base_url = "https://uk.webuy.com/search?categoryIds=892&categoryName=Graphics%20Cards%20-%20PCI-E"
    all_data = []

    while True:
        print(f"Scraping page {page}...")
        url = f"{base_url}&page={page}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }

        response = requests.get(url, headers=headers)

        print("Status code:", response.status_code)
        print("Page length:", len(response.text))
        print("First 500 characters:\n", response.text[:500])

        if response.status_code != 200:
            print("Error loading page. Stopping.")
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        cards = soup.select('.searchRecord')

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
                    all_data.append({
                        "gpu_name": name,
                        "sell_cash": sell_cash,
                        "sell_store": sell_store,
                        "buy_price": buy_price,
                        "date_tracked": str(datetime.date.today())
                    })
            except Exception as e:
                print("Error parsing card:", e)

        page += 1

    print(f"Scraped {len(all_data)} GPUs. Sample data:")
    for i, entry in enumerate(all_data[:5]):
        print(entry)

    print("Inserting into Supabase...")

    for entry in all_data:
        supabase.table("gpu_prices").insert(entry).execute()

    print("Scraping complete.")


# import requests
# from bs4 import BeautifulSoup
# from db import supabase  # ✅ Updated import
# import datetime

# def scrape_cex():
#     page = 1
#     base_url = "https://uk.webuy.com/search?categoryIds=892&categoryName=Graphics%20Cards%20-%20PCI-E"
#     all_data = []

#     while True:
#         print(f"Scraping page {page}...")
#         url = f"{base_url}&page={page}"
#         headers = {'User-Agent': 'Mozilla/5.0'}
#         response = requests.get(url, headers=headers)
#         soup = BeautifulSoup(response.text, 'html.parser')

#         cards = soup.select('.searchRecord')
#         if not cards:
#             print("No more items. Done scraping.")
#             break

#         for card in cards:
#             try:
#                 name = card.select_one('.desc').get_text(strip=True)
#                 price_tags = card.select('.priceTxt')
#                 buy_price = sell_cash = sell_store = None

#                 for tag in price_tags:
#                     text = tag.get_text(strip=True)
#                     if 'WeSell for' in text:
#                         buy_price = float(text.replace('WeSell for £', '').strip())
#                     elif 'WeBuy for Cash' in text:
#                         sell_cash = float(text.replace('WeBuy for Cash £', '').strip())
#                     elif 'WeBuy for Voucher' in text:
#                         sell_store = float(text.replace('WeBuy for Voucher £', '').strip())

#                 if name and buy_price is not None:
#                     all_data.append({
#                         "gpu_name": name,
#                         "sell_cash": sell_cash,
#                         "sell_store": sell_store,
#                         "buy_price": buy_price,
#                         "date_tracked": str(datetime.date.today())
#                     })
#             except Exception as e:
#                 print("Error parsing card:", e)

#         page += 1

#     print(f"Scraped {len(all_data)} GPUs. Sample data:")
#     for i, entry in enumerate(all_data[:5]):  # Print first 5
#         print(entry)


#     # Insert into Supabase
#     for entry in all_data:
#         supabase.table("gpu_prices").insert(entry).execute()

#     print("Scraping complete.")
