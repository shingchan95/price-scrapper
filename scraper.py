import requests
import datetime
from db import supabase

def scrape_cex():
    print("🔍 Scraping CEX using Algolia API...")

    url = "https://search.webuy.io/1/indexes/*/queries"
    headers = {
        "x-algolia-agent": "Algolia for JavaScript (4.24.0); Browser (lite); instantsearch.js (4.75.6); Vue (3.5.13); Vue InstantSearch (4.19.12); JS Helper (3.22.6)",
        "x-algolia-api-key": "bf79f2b6699e60a18ae330a1248b452c",
        "x-algolia-application-id": "LNNFEEWZVA",
        "Content-Type": "application/json"
    }

    payload = {
        "requests": [
            {
                "indexName": "prod_cex_uk",
                "params": (
                    'attributesToRetrieve=["boxBuyAllowed","boxName","boxSaleAllowed","boxWebBuyAllowed",'
                    '"boxWebSaleAllowed","cannotBuy","cashPrice","categoryFriendlyName","categoryName",'
                    '"collectionQuantity","ecomQuantity","exchangePrice","imageUrls","isNewBox","masterBoxId",'
                    '"masterBoxName","outOfEcomStock","superCatFriendlyName","superCatName","boxId",'
                    '"outOfStock","sellPrice","exchangePerc","cashBuyPrice","scId","discontinued","new",'
                    '"cashPriceCalculated","exchangePriceCalculated","rating","ecomQuantityOnHand",'
                    '"priceLastChanged","isImageTypeInternal","imageNames","Grade"]'
                    '&clickAnalytics=true'
                    '&facets=["*"]'
                    '&filters=boxVisibilityOnWeb=1 AND boxSaleAllowed=1 AND categoryId:892'
                    '&hitsPerPage=100'
                    '&page=0'
                    '&query='
                    '&userToken=3d5b71cd143d45d0a95c548ab24fa6df'
                )
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()

        if "results" not in data or not data["results"]:
            print(f"❌ API response missing 'results': {data}")
            return

        hits = data["results"][0].get("hits", [])
        print(f"📦 Found {len(hits)} GPUs.")

        all_data = []

        for item in hits:
            try:
                name = item["boxName"]
                buy_price = float(item["sellPrice"])
                all_data.append({
                    "gpu_name": name,
                    "buy_price": buy_price,
                    "sell_cash": item.get("cashPrice"),
                    "sell_store": item.get("exchangePrice"),
                    "date_tracked": str(datetime.date.today())
                })
            except Exception as e:
                print("⚠️ Error parsing item:", e)

        for entry in all_data:
            supabase.table("gpu_prices").insert(entry).execute()

        print("✅ Scraping complete.")
    except Exception as e:
        print("❌ Scraping failed:", e)
