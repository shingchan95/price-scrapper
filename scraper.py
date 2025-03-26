from requests_html import HTMLSession
from db import supabase  # your Supabase client setup
import datetime

def scrape_cex(upload_to_db=True):
    session = HTMLSession()
    page = 1
    base_url = "https://uk.webuy.com/search?categoryIds=892&categoryName=Graphics%20Cards%20-%20PCI-E"
    all_data = []

    while True:
        print(f"🔍 Scraping page {page}...")
        url = f"{base_url}&page={page}"
        response = session.get(url)

        try:
            response.html.render(timeout=20, sleep=2)
        except Exception as e:
            print("❌ Error rendering page:", e)
            break

        cards = response.html.find('.wrapper-box')
        if not cards:
            print("✅ No more items. Done scraping.")
            break

        for card in cards:
            try:
                name = card.find('.card-title a', first=True).text
                price_text = card.find('.product-main-price', first=True).text
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

    print(f"\n📦 Scraped {len(all_data)} GPUs. Sample:")
    for entry in all_data[:5]:
        print(entry)

    if upload_to_db:
        print("\n⬆️ Uploading to Supabase...")
        for entry in all_data:
            supabase.table("gpu_prices").insert(entry).execute()
        print("✅ Upload complete.")

    print("🚀 Scraping finished.")

# Only run if script is executed directly
if __name__ == "__main__":
    scrape_cex()
