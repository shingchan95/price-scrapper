import requests
from db import supabase
import datetime

def scrape_cex():
    print("🔍 Scraping CEX using Algolia API...")

    url = "https://search.webuy.io/1/indexes/*/queries"
    headers = {
        "x-algolia-agent": "Algolia for JavaScript (4.24.0); Browser (lite)",
        "x-algolia-api-key": "bf79f2b6699e60a18ae330a1248b452c",
        "x-algolia-application-id": "LNNFEEWZVA",
        "Content-Type": "application/json"
    }

    page = 0
    hits = []
    while True:
        payload = {
            "requests": [
                {
                    "indexName": "products_uk",
                    "params": f"query=&hitsPerPage=100&page={page}&facetFilters=[[\"superCatName:COMPUTING\"],[\"categoryName:PCI-EXPRESS-GRAPHICS-CARDS\"]]"
                }
            ]
        }

        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        batch = data["results"][0]["hits"]

        print(f"📦 Page {page + 1}: {len(batch)} items")
        if not batch:
            break

        hits.extend(batch)
        page += 1

    all_data = []
    for item in hits:
        try:
            gpu_name = item.get("boxName")
            buy_price = float(item.get("price", 0))
            if not gpu_name or buy_price <= 0:
                continue

            all_data.append({
                "gpu_name": gpu_name,
                "buy_price": buy_price,
                "sell_cash": None,
                "sell_store": None,
                "date_tracked": str(datetime.date.today())
            })
        except Exception as e:
            print("⚠️ Error parsing item:", e)

    print(f"✅ Scraped {len(all_data)} GPUs. Sample:")
    for entry in all_data[:5]:
        print(entry)

    for entry in all_data:
        supabase.table("gpu_prices").insert(entry).execute()

    print("✅ Upload complete.")
