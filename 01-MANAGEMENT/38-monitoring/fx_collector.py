#!/usr/bin/env python3
import requests
import psycopg2
import time
from datetime import datetime

import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME", "ops_db"),
    "user": os.getenv("DB_USER", "admin"),
    "password": os.getenv("DB_PASSWORD"),
}

def collect_fx():
    try:
        url = "http://localhost:8118/api/fx/v6/latest/USD"
        response = requests.get(url)
        data = response.json()
        
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        pairs = [("USD","ZAR"), ("USD","EUR"), ("USD","GBP"), ("USD","JPY"), ("USD","CHF")]
        print(f"\n--- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
        
        for base, target in pairs:
            if target in data["rates"]:
                rate = data["rates"][target]
                cur.execute(
                    "INSERT INTO fx_rates (base_currency, target_currency, rate) VALUES (%s, %s, %s)",
                    (base, target, rate)
                )
                print(f"{base}/{target}: {rate:.4f}")
        
        conn.commit()
        cur.close()
        conn.close()
        print("✅ FX rates stored successfully")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Starting FX Rate Collector...")
    while True:
        collect_fx()
        time.sleep(60)
