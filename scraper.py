import requests
from db import supabase
import datetime

def scrape_cex():
    print("🔍 Scraping CEX using Algolia API...")

    url = "https://search.webuy.io/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.24.0)%3B%20Browser%20(lite)%3B%20instantsearch.js%20(4.75.6)%3B%20Vue%20(3.5.13)%3B%20Vue%20InstantSearch%20(4.19.12)%3B%20JS%20Helper%20(3.22.6)&x-algolia-api-key=bf79f2b6699e60a18ae330a1248b452c&x-algolia-application-id=LNNFEEWZVA"
    headers = {
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Origin": "https://uk.webuy.com",
        "Referer": "https://uk.webuy.com/search?categoryIds=892&categoryName=Graphics+Cards+-+PCI-E",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    }

    payload = {
        "requests": [{
            "indexName": "prod_cex_uk",
            "params": (
                "attributesToRetrieve=[\"boxBuyAllowed\",\"boxName\",\"boxSaleAllowed\",\"boxWebBuyAllowed\"," \
                "\"boxWebSaleAllowed\",\"cannotBuy\",\"cashPrice\",\"categoryFriendlyName\",\"categoryName\"," \
                "\"collectionQuantity\",\"ecomQuantity\",\"exchangePrice\",\"imageUrls\",\"isNewBox\"," \
                "\"masterBoxId\",\"masterBoxName\",\"outOfEcomStock\",\"superCatFriendlyName\"," \
                "\"superCatName\",\"boxId\",\"outOfStock\",\"sellPrice\",\"exchangePerc\",\"cashBuyPrice\"," \
                "\"scId\",\"discontinued\",\"new\",\"cashPriceCalculated\",\"exchangePriceCalculated\"," \
                "\"rating\",\"ecomQuantityOnHand\",\"priceLastChanged\",\"isImageTypeInternal\"," \
                "\"imageNames\",\"Grade\"]&"
                "clickAnalytics=true&"
                "facets=[\"*\"]&"
                "filters=boxVisibilityOnWeb=1 AND boxSaleAllowed=1 AND categoryId:892&"
                "hitsPerPage=1000&"
                "maxValuesPerFacet=1000&"
                "page=0&"
                "query=&"
                "userToken=5e7e5203af5c462d81fcf912757a588e"
            )
        }]
    }

    today = str(datetime.date.today())
    all_data = []

    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()

        if "results" not in data or not data["results"]:
            print("❌ API response missing 'results':", data)
            return

        hits = data["results"][0].get("hits", [])
        if not hits:
            print("✅ No GPUs found in response.")
            return

        print(f"📄 Retrieved {len(hits)} items")

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

                    try:
                        supabase.table("gpu_prices").insert(entry).execute()
                        print(f"✅ Inserted {entry['gpu_name']}")
                    except Exception as e:
                        print(f"⏩ Skipped {entry['gpu_name']} (likely duplicate): {e}")
            except Exception as e:
                print("⚠️ Error parsing item:", e)

    except Exception as e:
        print("❌ Request or parsing failed:", e)

    print(f"📦 Total scraped: {len(all_data)}")
    print("✅ Scraping complete.")
