#!/usr/bin/env bash
# Port Scan - Scan the lab network using Python sockets (no nmap dependency)

echo "[*] Port Scan PoC"
echo "[*] Target network: 172.20.0.0/24"
echo ""

# Try nmap first, fall back to Python
if command -v nmap &>/dev/null; then
    echo "[*] Using nmap for scanning..."
    echo ""
    nmap -sT -T4 --top-ports 20 172.20.0.0/24 2>&1
else
    echo "[*] nmap not found, using Python socket scanner..."
    echo ""

    python3 -c "
import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

SUBNET = '172.20.0'
COMMON_PORTS = [21, 22, 80, 443, 2222, 3000, 3306, 5000, 8000, 8080, 8443, 9200]
TIMEOUT = 1

def scan_port(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(TIMEOUT)
        result = s.connect_ex((host, port))
        s.close()
        if result == 0:
            try:
                service = socket.getservbyport(port)
            except OSError:
                service = 'unknown'
            return (host, port, 'open', service)
        return None
    except Exception:
        return None

print('[*] Scanning hosts 172.20.0.1 - 172.20.0.254')
print(f'[*] Ports: {COMMON_PORTS}')
print()

start = time.time()
results = []

with ThreadPoolExecutor(max_workers=50) as executor:
    futures = []
    for host_id in range(1, 255):
        host = f'{SUBNET}.{host_id}'
        for port in COMMON_PORTS:
            futures.append(executor.submit(scan_port, host, port))

    for future in as_completed(futures):
        result = future.result()
        if result:
            results.append(result)

elapsed = time.time() - start

# Sort and display results
results.sort(key=lambda x: (x[0], x[1]))

current_host = None
for host, port, state, service in results:
    if host != current_host:
        print(f'\nHost: {host}')
        print(f'  {\"PORT\":>8s}  {\"STATE\":8s}  SERVICE')
        print(f'  {\"----\":>8s}  {\"-----\":8s}  -------')
        current_host = host
    print(f'  {port:>8d}  {state:8s}  {service}')

print(f'\n[+] Scan complete: {len(results)} open ports found in {elapsed:.1f}s')
print(f'[+] Scanned {254 * len(COMMON_PORTS)} host:port combinations')
"
fi

echo ""
echo "[*] Attack complete. Check Suricata alerts for SID 100010."
