from flask import Flask, jsonify, render_template, request
from db import supabase
from scraper import scrape_cex
import os

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
    response = supabase.table("gpu_prices").select("gpu_name").execute()
    names = {entry['gpu_name'] for entry in response.data}
    return jsonify(sorted(list(names)))

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
