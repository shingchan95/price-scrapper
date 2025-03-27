from flask import Flask, jsonify, render_template, request
from db import supabase
from scraper import scrape_cex
import os
import pandas as pd
import numpy as np

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'),
    static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'),
    static_url_path='/static'
)
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/api/gpu-list')
def get_gpu_list():
    response = supabase.table("gpu_prices")\
        .select("gpu_name, buy_price, sell_cash, sell_store, date_tracked")\
        .order("date_tracked", desc=False)\
        .execute()

    rows = response.data
    df = pd.DataFrame(rows)

    if df.empty:
        return jsonify([])

    df = df.sort_values("date_tracked")

    price_summary = (
        df.groupby("gpu_name")
          .agg(
              first_price=("buy_price", "first"),
              last_price=("buy_price", "last"),
              last_buy_price=("buy_price", "last"),
              sell_cash=("sell_cash", "last"),
              sell_store=("sell_store", "last"),
          )
          .reset_index()
    )

    price_summary["change"] = price_summary["last_price"] - price_summary["first_price"]

    # ✅ Convert NaN to None for safe JSON output
    price_summary = price_summary.replace({np.nan: None})

    return jsonify(price_summary.to_dict(orient="records"))



@app.route('/api/gpu-prices')
def get_prices():
    gpu_name = request.args.get('gpu')
    response = supabase.table("gpu_prices")\
        .select("date_tracked, sell_cash, sell_store, buy_price")\
        .eq("gpu_name", gpu_name)\
        .order("date_tracked", desc=False)\
        .execute()

    return jsonify([
        {
            'date': row['date_tracked'],
            'sell_cash': row['sell_cash'],
            'sell_store': row['sell_store'],
            'buy_price': row['buy_price']
        }
        for row in response.data
    ])

@app.route('/run-scraper')
def run_scraper():
    scrape_cex()
    return "Scraper ran!"


@app.route('/test-insert')
def test_insert():
    from db import supabase
    response = supabase.table("gpu_prices").insert({
        "gpu_name": "TEST GPU",
        "sell_cash": 100.0,
        "sell_store": 110.0,
        "buy_price": 200.0,
        "date_tracked": "2025-03-26"
    }).execute()
    return str(response)

if __name__ == "__main__":
    import os
    is_local = os.environ.get("FLASK_ENV") == "development"

    if is_local:
        app.run(debug=True)
