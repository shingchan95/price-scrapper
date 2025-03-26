from flask import Flask, render_template, jsonify, request
from db import get_db_connection
from scraper import scrape_cex  # ✅ Import your scraper

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/api/gpu-prices')
def get_prices():
    gpu_name = request.args.get('gpu')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT date_tracked, sell_cash, sell_store, buy_price FROM gpu_prices WHERE gpu_name=%s ORDER BY date_tracked",
        (gpu_name,)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify([
        {
            'date': str(row[0]),
            'sell_cash': float(row[1]) if row[1] is not None else None,
            'sell_store': float(row[2]) if row[2] is not None else None,
            'buy_price': float(row[3])
        } for row in rows
    ])

# ✅ Add this route
@app.route('/run-scraper')
def run_scraper():
    scrape_cex()
    return "Scraper ran!"

@app.route('/api/gpu-list')
def get_gpu_list():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT gpu_name FROM gpu_prices ORDER BY gpu_name")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify([row[0] for row in rows])
