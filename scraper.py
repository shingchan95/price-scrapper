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
    page = 0
    today = str(datetime.date.today())

    while True:
        payload = {
            "requests": [{
                "indexName": "prod_cex_uk",
                "params": (
                    "attributesToRetrieve=boxName,sellPrice,cashPrice,exchangePrice&"
                    "clickAnalytics=true&"
                    "facets=%5B%22*%22%5D&"
                    "filters=boxVisibilityOnWeb=1 AND boxSaleAllowed=1 AND categoryId:892&"
                    "hitsPerPage=30&"
                    "maxValuesPerFacet=1000&"
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
                price = item.get("sellPrice") or item.get("cashPrice") or item.get("exchangePrice")

                if name and price:
                    entry = {
                        "gpu_name": name,
                        "sell_cash": item.get("cashPrice"),
                        "sell_store": item.get("exchangePrice"),
                        "buy_price": price,
                        "date_tracked": today
                    }
                    all_data.append(entry)

                    # Insert with duplicate prevention
                    try:
                        supabase.table("gpu_prices").insert(entry).execute()
                        print(f"✅ Inserted {entry['gpu_name']}")
                    except Exception as e:
                        print(f"⏩ Skipped {entry['gpu_name']} (likely duplicate): {e}")
            except Exception as e:
                print("⚠️ Error parsing item:", e)

        page += 1

    print(f"📦 Scraped {len(all_data)} GPUs. Sample:")
    for entry in all_data[:5]:
        print(entry)
        try:
            supabase.table("gpu_prices").insert(entry).execute()
            print(f"✅ Inserted {entry['gpu_name']}")
        except Exception as e:
            print(f"⏩ Skipped {entry['gpu_name']} (likely duplicate):", str(e))

    print("✅ Scraping complete.")
