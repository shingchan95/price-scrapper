import requests
from db import supabase
import datetime
import os

def scrape_cex():
    print("🔍 Scraping ...")

    url = os.environ.get("API_URL")
    headers = {
        os.environ.get("HEADER_1_KEY"): os.environ.get("HEADER_1_VALUE"),
        os.environ.get("HEADER_2_KEY"): os.environ.get("HEADER_2_VALUE"),
        os.environ.get("HEADER_3_KEY"): os.environ.get("HEADER_3_VALUE"),
        os.environ.get("HEADER_4_KEY"): os.environ.get("HEADER_4_VALUE")
    }

    all_data = []
    page = 0
    today = str(datetime.date.today())

    while True:
        payload = {
            "requests": [{
                "indexName": "prod_cex_uk",
                "params": (
                    "attributesToRetrieve=cashPriceCalculated,exchangePriceCalculated,boxName,sellPrice&"
                    "clickAnalytics=true&"
                    "facets=%5B%22*%22%5D&"
                    "filters=boxVisibilityOnWeb=1 AND boxSaleAllowed=1 AND categoryId:892&"
                    "hitsPerPage=1000&"  # Maximize per page
                    f"page={page}&"
                    "query="
                )
            }]
        }

        response = requests.post(url, headers=headers, json=payload)
        data = response.json()

        if "results" not in data or not data["results"]:
            print("❌ API response missing 'results':", data)
            break

        hits = data["results"][0].get("hits", [])
        if not hits:
            print("✅ No more items. Done scraping.")
            break

        print(f"📄 Page {page + 1}: Found {len(hits)} items")

        for item in hits:
            try:
                name = item.get("boxName", "Unknown")
                sell_cash = item.get("cashPriceCalculated")
                sell_store = item.get("exchangePriceCalculated")
                buy_price = item.get("sellPrice") or sell_cash or sell_store

                if name and buy_price:
                    entry = {
                        "gpu_name": name,
                        "sell_cash": sell_cash,
                        "sell_store": sell_store,
                        "buy_price": buy_price,
                        "date_tracked": today
                    }
                    all_data.append(entry)
            except Exception as e:
                print("⚠️ Error parsing item:", e)

        page += 1

    print(f"📦 Scraped {len(all_data)} GPUs. Sample:")
    for entry in all_data[:5]:
        print(f"🧾 {entry['gpu_name']}: sell_cash={entry['sell_cash']}, sell_store={entry['sell_store']}, buy_price={entry['buy_price']}")

    if all_data:
        try:
            supabase.table("gpu_prices").insert(all_data).execute()
            print(f"✅ Inserted {len(all_data)} entries")
        except Exception as e:
            print(f"⏩ Some entries may be duplicates or failed: {e}")

    print("✅ Scraping complete.")
