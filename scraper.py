import requests
from bs4 import BeautifulSoup
from db import supabase  # ✅ Your Supabase client setup
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

        cards = soup.select('.wrapper-box')
        if not cards:
            print("No more items. Done scraping.")
            break

        for card in cards:
            try:
                name = card.select_one('.card-title a').get_text(strip=True)
                buy_price_tag = card.select_one('.product-main-price')
                buy_price = float(buy_price_tag.text.strip().replace('£', '')) if buy_price_tag else None

                # Prices like “WeBuy for Cash” and “WeBuy for Voucher” aren't in the new card layout
                # You’ll need to either:
                # 1. Scrape each product detail page individually (slower)
                # 2. Only store the main price (WeSell)

                # We'll just store WeSell for now
                if name and buy_price is not None:
                    all_data.append({
                        "gpu_name": name,
                        "sell_cash": None,
                        "sell_store": None,
                        "buy_price": buy_price,
                        "date_tracked": str(datetime.date.today())
                    })

            except Exception as e:
                print("Error parsing card:", e)

        page += 1

    print(f"Scraped {len(all_data)} GPUs. Sample data:")
    for entry in all_data[:5]:
        print(entry)

    # ✅ Insert into Supabase
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
