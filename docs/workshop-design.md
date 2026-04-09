# OWASP Juice Shop 기반 실시간 공격/방어 실습 수업 설계

## 0. 범위 확정: CIC-IDS 2017/2018 공격 유형 전체 커버

Juice Shop(Node.js 웹앱) + Docker Compose 확장으로 CIC-IDS 주요 공격 유형을 **모두** 재현한다.

| CIC-IDS Label             | 재현 방법                                 | 실습 포함 |
|---------------------------|------------------------------------------|-----------|
| Web Attack - Brute Force  | Juice Shop 로그인 페이지                   | **포함** |
| Web Attack - XSS          | Juice Shop DOM/Reflected/Stored           | **포함** |
| Web Attack - SQL Injection| Juice Shop 로그인, 검색                    | **포함** |
| SSH Brute Force           | Docker Compose로 SSH 서버 추가             | **포함** |
| FTP Brute Force           | Docker Compose로 FTP 서버 추가             | **포함** |
| DoS / DDoS                | Juice Shop 대상 slowloris / 대량 요청       | **포함** |
| Bot                       | Juice Shop 대상 자동 스크래핑/주문 스크립트   | **포함** |
| Infiltration              | 웹앱 → 내부 DB 서버 접근 시나리오            | **포함** |
| PortScan                  | Docker 내부 네트워크 대상 nmap               | **포함** |

> **최종 실습 대상: 9종** — Juice Shop 원본 + Docker Compose 확장 환경

---

## 1. 실습 환경 아키텍처

### Docker Compose 구성

```
juice-shop-lab/
├── docker-compose.yml
│
├── juice-shop        (웹앱)           localhost:3000
├── ssh-server        (OpenSSH)        localhost:2222
├── ftp-server        (vsftpd)         localhost:2121
├── internal-db       (MySQL)          내부망만 노출
├── internal-api      (Flask 미니 서버) 내부망만 노출
│
└── 네트워크 구성
      ├── frontend-net   (학생 접근 가능: juice-shop, ssh, ftp)
      └── backend-net    (내부망: juice-shop ↔ internal-db, internal-api)
```

- **Juice Shop** → SQLi, XSS, Web Brute Force, Bot, DoS 실습
- **SSH/FTP 서버** → SSH/FTP Brute Force 실습 (Hydra, Python)
- **내부 DB/API** → Infiltration 실습 (웹앱 취약점으로 내부망 접근)
- **Docker 네트워크** → PortScan 실습 (nmap으로 내부 서비스 탐색)

### 오프라인 대비

| 구성요소          | 온라인                              | 오프라인 대안                     |
|-------------------|-------------------------------------|----------------------------------|
| Docker 이미지     | `docker compose pull`               | USB로 이미지 tar 배포             |
| Python 패키지     | `pip install`                       | 오프라인 wheels 묶음              |
| Wordlist          | SecLists GitHub                     | USB 사전 배포                     |
| 도구 (nmap 등)    | apt install                         | USB .deb 배포                    |

---

## 2. 수업 구조 (총 5회, 회당 2시간)

### Session 1: 환경 구축 + SQL Injection (2h)

| 시간      | 내용                                | 형태   |
|-----------|-------------------------------------|--------|
| 0:00-0:20 | Docker Compose 환경 세팅 + 접속 확인  | 핸즈온  |
| 0:20-0:30 | 배경: SQL이란? 웹 로그인이 DB에 쿼리하는 구조 | 슬라이드 5장 이내 |
| 0:30-1:00 | **실습 1) 로그인 우회** — `' OR 1=1--` 로 admin 로그인 | 핸즈온  |
| 1:00-1:30 | **실습 2) 검색창 SQLi** — UNION SELECT로 DB 테이블 노출 | 핸즈온  |
| 1:30-1:50 | **실습 3) DevTools Network 탭**으로 요청/응답 직접 확인 | 핸즈온  |
| 1:50-2:00 | 정리: "이 공격이 IDS 로그에는 어떻게 찍히는가" | 토론   |

**Juice Shop Challenges:** Login Admin, Login Bender, Christmas Special

---

### Session 2: XSS (2h)

| 시간      | 내용                                | 형태   |
|-----------|-------------------------------------|--------|
| 0:00-0:15 | 배경: 브라우저가 스크립트를 실행하는 원리 (DOM 기초) | 슬라이드 5장 이내 |
| 0:15-0:45 | **실습 1) Reflected XSS** — 검색창에 `<iframe src="javascript:alert('xss')">` | 핸즈온  |
| 0:45-1:15 | **실습 2) DOM-based XSS** — URL fragment 조작 (`/#/search?q=...`) | 핸즈온  |
| 1:15-1:45 | **실습 3) Stored XSS** — 리뷰/피드백에 스크립트 삽입 | 핸즈온  |
| 1:45-2:00 | 정리: XSS 유형별 차이 + IDS 탐지 포인트 | 토론   |

**Juice Shop Challenges:** DOM XSS, Reflected XSS, Stored XSS via API

---

### Session 3: Brute Force — Web + SSH + FTP (2h)

| 시간      | 내용                                | 형태   |
|-----------|-------------------------------------|--------|
| 0:00-0:10 | 배경: 인증 매커니즘과 brute force 원리 | 슬라이드 3장 |
| 0:10-0:40 | **실습 1) Web Brute Force** — Python 스크립트로 Juice Shop 로그인 공격 | 핸즈온  |
| 0:40-1:10 | **실습 2) SSH Brute Force** — Hydra로 ssh-server 공격 | 핸즈온  |
| 1:10-1:40 | **실습 3) FTP Brute Force** — Hydra로 ftp-server 공격 | 핸즈온  |
| 1:40-2:00 | 정리: 프로토콜별 brute force 트래픽 차이 비교 | 토론   |

**실습 스켈레톤:**
```python
# web_brute_force.py
import requests

TARGET = "http://localhost:3000/rest/user/login"
PASSWORDS = open("wordlist.txt").read().splitlines()

for pw in PASSWORDS:
    resp = requests.post(TARGET, json={
        "email": "admin@juice-sh.op",
        "password": pw
    })
    if resp.status_code == 200:
        print(f"[+] Found: {pw}")
        break
```

```bash
# SSH Brute Force (Hydra)
hydra -l admin -P wordlist.txt ssh://localhost:2222

# FTP Brute Force (Hydra)
hydra -l admin -P wordlist.txt ftp://localhost:2121
```

---

### Session 4: Bot + DoS + PortScan (2h)

| 시간      | 내용                                | 형태   |
|-----------|-------------------------------------|--------|
| 0:00-0:10 | 배경: 봇 트래픽 vs 정상 트래픽, DoS 원리 | 슬라이드 5장 |
| 0:10-0:40 | **실습 1) Bot** — Juice Shop 자동 스크래핑 + 자동 주문 스크립트 | 핸즈온  |
| 0:40-1:10 | **실습 2) DoS** — slowloris로 Juice Shop 응답 지연 관찰 | 핸즈온  |
| 1:10-1:40 | **실습 3) PortScan** — nmap으로 Docker 내부 네트워크 스캔 | 핸즈온  |
| 1:40-2:00 | 정리: 각 공격의 네트워크 패턴 비교 (패킷 수, 주기, 포트 분포) | 토론   |

**실습 스켈레톤:**
```python
# bot_scraper.py — Juice Shop 자동 스크래핑
import requests, time

s = requests.Session()
# 로그인
s.post("http://localhost:3000/rest/user/login",
       json={"email":"admin@juice-sh.op","password":"admin123"})

# 전 상품 자동 수집
products = s.get("http://localhost:3000/api/Products").json()
for p in products["data"]:
    print(f"[Bot] {p['name']} - ${p['price']}")
    time.sleep(0.1)  # rate 조절
```

```bash
# PortScan (nmap)
nmap -sT -p 1-10000 172.20.0.0/24    # Docker 내부 대역

# DoS (slowloris)
slowloris localhost:3000 -s 200
```

---

### Session 5: Infiltration + 종합 CTF (2h)

| 시간      | 내용                                | 형태   |
|-----------|-------------------------------------|--------|
| 0:00-0:10 | 배경: 내부망 침투 개념, 피벗 공격      | 슬라이드 3장 |
| 0:10-0:40 | **실습 1) Infiltration** — SQLi로 내부 DB 서버 정보 노출 → 내부 API 접근 | 핸즈온  |
| 0:40-1:00 | **실습 2)** 내부 API에서 민감 데이터 추출 | 핸즈온  |
| 1:00-2:00 | **종합 CTF** — 9가지 공격 유형 혼합 미션 | 팀 경쟁  |

---

## 3. CIC-IDS 연결 포인트 ("치팅식" 탐지 연동)

각 세션 마지막에 IDS 팀과 연결:

| 공격 유형          | 네트워크 시그니처 (IDS가 볼 것)                          | CIC-IDS 대응 Label                |
|-------------------|--------------------------------------------------------|----------------------------------|
| SQL Injection     | HTTP body에 `' OR`, `UNION SELECT`, `--` 포함           | Web Attack - Sql Injection       |
| XSS               | HTTP param에 `<script>`, `<iframe>`, `javascript:`      | Web Attack - XSS                 |
| Web Brute Force   | 동일 endpoint에 짧은 시간 내 다수 POST 요청               | Web Attack - Brute Force         |
| SSH Brute Force   | port 2222에 다수 TCP 연결 + 인증 실패                     | SSH-Patator / SSH-Bruteforce     |
| FTP Brute Force   | port 2121에 다수 TCP 연결 + 인증 실패                     | FTP-Patator / FTP-BruteForce     |
| Bot               | 짧은 간격으로 다수 API endpoint GET 요청                   | Bot                              |
| DoS               | 다수 TCP 연결 유지 + 불완전 HTTP 요청 (slowloris 패턴)     | DoS slowloris / DoS Hulk         |
| PortScan          | 짧은 시간에 다수 포트로 SYN 패킷                           | PortScan                         |
| Infiltration      | 웹앱에서 내부망 IP로의 비정상 연결                          | Infiltration                     |

---

## 4. 종합 CTF 미션 (Session 5 후반)

| #  | 미션                                      | 공격 유형          | 난이도 |
|----|------------------------------------------|--------------------|--------|
| 1  | admin 계정으로 로그인하라                   | SQLi               | ★☆☆   |
| 2  | 검색창에서 모든 사용자 이메일을 추출하라      | SQLi (UNION)       | ★★☆   |
| 3  | 상품 리뷰에 XSS payload를 삽입하라          | Stored XSS         | ★★☆   |
| 4  | 주문 추적 페이지에서 XSS를 트리거하라        | Reflected XSS      | ★★☆   |
| 5  | jim@juice-sh.op 의 비밀번호를 알아내라      | Web Brute Force    | ★★☆   |
| 6  | SSH 서버의 admin 비밀번호를 알아내라         | SSH Brute Force    | ★★☆   |
| 7  | FTP 서버에서 secret.txt를 다운받아라        | FTP Brute Force    | ★★☆   |
| 8  | Docker 내부망에서 숨겨진 서비스를 찾아라     | PortScan           | ★★☆   |
| 9  | Juice Shop 전 상품을 자동으로 장바구니에 담아라 | Bot              | ★★★   |
| 10 | 내부 DB에서 flag 테이블의 값을 읽어라        | Infiltration       | ★★★   |

---

## 5. 체크리스트 (후속 액션)

- [ ] Docker Compose 파일 작성 + 테스트
- [ ] SSH/FTP 서버 컨테이너 설정 (계정, wordlist 매칭)
- [ ] 내부 DB/API 서버 구현 (Infiltration 시나리오)
- [ ] Docker 이미지 USB tar 준비 (오프라인 대비)
- [ ] 각 세션별 실습 가이드 문서 작성 (step-by-step)
- [ ] Brute Force용 wordlist 선정 및 축소 (수업용 100~500개)
- [ ] 종합 CTF 채점 기준 확정
- [ ] IDS 팀과 공격-탐지 매핑 최종 합의
- [ ] CIC-IDS 2017 데이터 분석 결과와 실습 시나리오 매칭 검증

---

## 6. 구현 현황 (2026-04-05 기준)

위 설계를 기반으로 전체 환경이 구현 완료됨:

- Docker Compose 8개 서비스 동작 확인
- PoC 12종 (Python/Bash) 대시보드에서 버튼 클릭 실행
- Suricata 규칙 11종 ON/OFF 토글
- 웹 대시보드 (React) 3-panel 레이아웃
- 실시간 탐지 모니터링 (3초 폴링)
- 학생 커스텀 PoC/규칙 추가 기능
- `bash start.sh` 원커맨드 실행

상세 구현 내용: [implementation-design.md](implementation-design.md)
