import requests
from db import supabase
import datetime

def scrape_cex():
    print("🔍 Scraping CEX using Algolia API...")

    url = (
        "https://search.webuy.io/1/indexes/*/queries"
        "?x-algolia-agent=Algolia%20for%20JavaScript%20(4.24.0)%3B%20Browser%20(lite)"
        "%3B%20instantsearch.js%20(4.75.6)%3B%20Vue%20(3.5.13)%3B%20Vue%20InstantSearch"
        "%20(4.19.12)%3B%20JS%20Helper%20(3.22.6)"
        "&x-algolia-api-key=bf79f2b6699e60a18ae330a1248b452c"
        "&x-algolia-application-id=LNNFEEWZVA"
    )

    headers = {
        "Content-Type": "application/json",
        "Referer": "https://uk.webuy.com",
        "Origin": "https://uk.webuy.com",
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Mobile Safari/537.36"
    }

    payload = {
        "requests": [
            {
                "indexName": "prod_uk_products_price_desc",
                "params": "query=&hitsPerPage=30&page=0&facetFilters=%5B%5B%22superCatName%3ACOMPUTING%22%5D%2C%5B%22categoryName%3APCI-EXPRESS-GRAPHICS-CARDS%22%5D%5D"
            }
        ]
    }

    response = requests.post(url, headers=headers, json=payload)
    data = response.json()

    if "results" not in data:
        print("❌ API response missing 'results':", data)
        return

    batch = data["results"][0]["hits"]
    all_data = []

    for item in batch:
        try:
            name = item.get("boxTitle") or item.get("title")
            buy_price = float(item["price"]["value"])
            all_data.append({
                "gpu_name": name,
                "sell_cash": None,
                "sell_store": None,
                "buy_price": buy_price,
                "date_tracked": str(datetime.date.today())
            })
        except Exception as e:
            print("⚠️ Error parsing item:", e)

    print(f"📦 Scraped {len(all_data)} GPUs. Sample:")
    for entry in all_data[:5]:
        print(entry)

    for entry in all_data:
        supabase.table("gpu_prices").insert(entry).execute()

    print("✅ Scraping complete.")
