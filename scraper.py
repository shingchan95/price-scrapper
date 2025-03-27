import requests
from db import supabase
import datetime

def scrape_cex():
    print("🔍 Scraping CEX using Algolia API...")

    url = "https://search.webuy.io/1/indexes/*/queries"
    headers = {
        "x-algolia-agent": "Algolia for JavaScript (4.24.0); Browser (lite); instantsearch.js (4.75.6); Vue (3.5.13); Vue InstantSearch (4.19.12); JS Helper (3.22.6)",
        "x-algolia-api-key": "bf79f2b6699e60a18ae330a1248b452c",
        "x-algolia-application-id": "LNNFEEWZVA",
        "Content-Type": "application/json"
    }

    all_data = []
    today = str(datetime.date.today())

    payload = {
        "requests": [{
            "indexName": "prod_cex_uk",
            "params": (
                "attributesToRetrieve=boxName,sellPrice,cashPrice,exchangePrice&"
                "clickAnalytics=true&"
                "facets=%5B%22*%22%5D&"
                "filters=boxVisibilityOnWeb=1 AND boxSaleAllowed=1 AND categoryId:892&"
                "hitsPerPage=1000&"
                "maxValuesPerFacet=1000&"
                "page=0&"
                "query="
            )
        }]
    }

    response = requests.post(url, headers=headers, json=payload)
    data = response.json()

    if "results" not in data or not data["results"]:
        print("❌ API response missing 'results':", data)
        return

    hits = data["results"][0].get("hits", [])
    if not hits:
        print("✅ No items found. Done scraping.")
        return

    print(f"📄 API returned {len(hits)} items")

    inserted = 0
    duplicates = 0
    missing_price = 0

    for item in hits:
        try:
            name = item.get("boxName", "Unknown")
            price = item.get("sellPrice") or item.get("cashPrice") or item.get("exchangePrice")

            if not price:
                missing_price += 1
                continue

            entry = {
                "gpu_name": name,
                "sell_cash": item.get("cashPrice"),
                "sell_store": item.get("exchangePrice"),
                "buy_price": price,
                "date_tracked": today
            }

            try:
                supabase.table("gpu_prices").insert(entry).execute()
                inserted += 1
            except Exception as e:
                duplicates += 1
        except Exception as e:
            print("⚠️ Error parsing item:", e)

    # Summary
    print("📦 Scraping Summary:")
    print(f"• Total from API     : {len(hits)}")
    print(f"• Inserted to DB     : {inserted}")
    print(f"• Duplicates skipped : {duplicates}")
    print(f"• Missing price      : {missing_price}")
    print("✅ Scraping complete.")
