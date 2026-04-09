#!/usr/bin/env python3
"""Bot - Rapid product scraping against Juice Shop."""

import requests
import json
import sys
import time

TARGET = "http://juice-shop:3000"

def main():
    print("[*] Bot Scraper PoC")
    print(f"[*] Target: {TARGET}")
    print()

    session = requests.Session()
    session.headers.update({
        "User-Agent": "BotScraper/1.0 (automated; research)",
    })

    # Scrape product list
    print("[*] Phase 1: Rapidly scraping product listings...")
    products = []
    start = time.time()

    for i in range(50):
        try:
            resp = session.get(f"{TARGET}/rest/products/search?q=", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if "data" in data and i == 0:
                    products = data["data"]
                    print(f"  [Request {i+1:3d}] Found {len(products)} products")
                else:
                    print(f"  [Request {i+1:3d}] Status: {resp.status_code} ({len(resp.content)} bytes)")
            else:
                print(f"  [Request {i+1:3d}] Status: {resp.status_code}")
        except Exception as e:
            print(f"  [Request {i+1:3d}] Error: {e}")

    elapsed = time.time() - start
    print(f"\n[*] Phase 1 complete: 50 requests in {elapsed:.1f}s ({50/elapsed:.1f} req/s)")

    # Scrape individual product pages
    print("\n[*] Phase 2: Scraping individual product details...")
    for i, product in enumerate(products[:10], 1):
        pid = product.get("id", i)
        try:
            resp = session.get(f"{TARGET}/api/Products/{pid}", timeout=5)
            if resp.status_code == 200:
                p = resp.json().get("data", {})
                print(f"  [Product {pid:2d}] {p.get('name', 'N/A'):40s} ${p.get('price', 'N/A')}")
            else:
                print(f"  [Product {pid:2d}] Status: {resp.status_code}")
        except Exception as e:
            print(f"  [Product {pid:2d}] Error: {e}")

    # Scrape reviews
    print("\n[*] Phase 3: Scraping product reviews...")
    for i in range(1, 11):
        try:
            resp = session.get(f"{TARGET}/rest/products/{i}/reviews", timeout=5)
            if resp.status_code == 200:
                reviews = resp.json().get("data", [])
                print(f"  [Product {i:2d}] {len(reviews)} reviews")
            else:
                print(f"  [Product {i:2d}] Status: {resp.status_code}")
        except Exception as e:
            print(f"  [Product {i:2d}] Error: {e}")

    total_elapsed = time.time() - start
    print(f"\n[+] Scraping complete: ~70 requests in {total_elapsed:.1f}s")
    print("[*] This rapid-fire access pattern should trigger Suricata bot detection")
    print()
    print("[*] Attack complete. Check Suricata alerts for SID 100008.")

if __name__ == "__main__":
    main()
