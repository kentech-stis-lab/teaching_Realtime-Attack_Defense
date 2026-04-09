# 구현 설계서: Red/Blue Team 실습 대시보드

## 1. 시스템 개요

```
┌─────────────────────────────────────────────────────────┐
│                   Web Dashboard (:8080)                  │
│  ┌──────────┐  ┌──────────┐  ┌────────────────────────┐ │
│  │ Attack   │  │ Defense  │  │ Live Monitor           │ │
│  │ Panel    │  │ Panel    │  │ (Suricata alerts 실시간) │ │
│  └────┬─────┘  └────┬─────┘  └────────────┬───────────┘ │
└───────┼─────────────┼─────────────────────┼─────────────┘
        │             │                     │
        ▼             ▼                     ▲
┌──────────────┐ ┌──────────────┐  ┌────────────────┐
│ Backend API  │ │ Suricata     │  │ Suricata       │
│ (FastAPI)    │─│ Rule Manager │  │ EVE Log Stream │
│ :8000        │ └──────────────┘  └────────────────┘
└──────┬───────┘
       │ PoC 실행
       ▼
┌──────────────────────────────────────────┐
│         Docker Lab Network               │
│  Juice Shop  SSH  FTP  Internal-DB/API   │
└──────────────────────────────────────────┘
```

### 핵심 기능 2가지

1. **사전 준비된 공격/방어 실행 및 모니터링**
   - 9종 공격 PoC를 버튼 클릭으로 실행
   - 대응 Suricata 규칙을 보고 ON/OFF
   - IDS 탐지 결과 실시간 스트리밍

2. **학생 커스텀 공격/방어 추가**
   - 웹 에디터에서 새 PoC 스크립트 작성 → 등록 → 실행
   - 웹 에디터에서 새 Suricata 규칙 작성 → 등록 → 적용

---

## 2. 아키텍처

### 2.1 컨테이너 구성

| 컨테이너 | 이미지 | 포트 | 역할 |
|----------|--------|------|------|
| `juice-shop` | bkimminich/juice-shop | 3000 | 공격 대상 (웹앱) |
| `ssh-server` | linuxserver/openssh-server | 2222 | SSH Brute Force 대상 |
| `ftp-server` | fauria/vsftpd | 2121 | FTP Brute Force 대상 |
| `internal-db` | mysql:8 | (internal) | Infiltration 대상 |
| `internal-api` | python:3.10-slim (Flask) | (internal) | Infiltration 대상 |
| `suricata` | jasonish/suricata | 9000 | IDS — 트래픽 미러링 |
| `backend` | python:3.10-slim (FastAPI) | 8000 | API 서버 |
| `dashboard` | node:20-slim (React) | 8080 | 웹 대시보드 |

### 2.2 네트워크

```
frontend-net (172.20.0.0/24)
  ├── juice-shop    (.10)
  ├── ssh-server    (.11)
  ├── ftp-server    (.12)
  ├── suricata      (.13)  ← 미러링 모드
  ├── backend       (.14)
  └── dashboard     (.15)

backend-net (172.20.1.0/24)
  ├── juice-shop    (.10)  ← 양쪽 네트워크 연결
  ├── internal-db   (.20)
  ├── internal-api  (.21)
  └── backend       (.14)  ← PoC 실행 시 내부망 접근 필요
```

### 2.3 데이터 흐름

```
[사용자 클릭 "Run Attack"]
    │
    ▼
[Dashboard] → POST /api/attacks/{id}/run → [Backend API]
    │                                           │
    │                                           ▼
    │                                    [PoC 스크립트 실행]
    │                                    (subprocess로 Python/bash)
    │                                           │
    │                                           ▼
    │                                    [공격 트래픽 발생]
    │                                    Juice Shop / SSH / FTP
    │                                           │
    │                                           ▼
    │                                    [Suricata 탐지]
    │                                    eve.json에 alert 기록
    │                                           │
    ▼                                           ▼
[Dashboard] ← WebSocket /ws/alerts ← [Backend: tail eve.json]
    │
    ▼
[실시간 Alert 표시]
```

---

## 3. Backend API 설계 (FastAPI)

### 3.1 디렉토리 구조

```
backend/
├── main.py                 # FastAPI 앱
├── routers/
│   ├── attacks.py          # 공격 PoC CRUD + 실행
│   ├── rules.py            # Suricata 규칙 CRUD + 적용
│   └── monitor.py          # WebSocket 실시간 알림
├── pocs/                   # PoC 스크립트 저장
│   ├── preset/             # 사전 준비된 9종
│   │   ├── sqli_login_bypass.py
│   │   ├── sqli_union_select.py
│   │   ├── xss_dom.py
│   │   ├── xss_reflected.py
│   │   ├── xss_stored.py
│   │   ├── brute_web.py
│   │   ├── brute_ssh.sh
│   │   ├── brute_ftp.sh
│   │   ├── bot_scraper.py
│   │   ├── dos_slowloris.py
│   │   ├── portscan.sh
│   │   └── infiltration.py
│   └── custom/             # 학생이 추가한 PoC
├── rules/                  # Suricata 규칙 저장
│   ├── preset/             # 사전 준비된 규칙
│   │   └── local.rules
│   └── custom/             # 학생이 추가한 규칙
├── models.py               # Pydantic 모델
└── config.py               # 설정
```

### 3.2 API 엔드포인트

#### 공격 (Attacks)

```
GET    /api/attacks                 # 전체 공격 목록 (preset + custom)
GET    /api/attacks/{id}            # 공격 상세 (코드, 설명, 유형)
POST   /api/attacks/{id}/run       # 공격 실행 → 결과 반환
POST   /api/attacks/{id}/stop      # 실행 중인 공격 중지
POST   /api/attacks                 # [학생] 새 공격 PoC 등록
PUT    /api/attacks/{id}            # [학생] PoC 수정
DELETE /api/attacks/{id}            # [학생] PoC 삭제 (custom만)
```

#### 방어 규칙 (Rules)

```
GET    /api/rules                   # 전체 규칙 목록 (preset + custom)
GET    /api/rules/{id}              # 규칙 상세
PUT    /api/rules/{id}/toggle      # 규칙 ON/OFF
POST   /api/rules                   # [학생] 새 Suricata 규칙 등록
PUT    /api/rules/{id}              # [학생] 규칙 수정
DELETE /api/rules/{id}              # [학생] 규칙 삭제 (custom만)
POST   /api/rules/reload            # Suricata 규칙 리로드
```

#### 모니터링 (Monitor)

```
WS     /ws/alerts                   # Suricata alert 실시간 스트리밍
GET    /api/alerts                  # 최근 alert 목록 (페이징)
GET    /api/alerts/stats            # 공격 유형별 탐지 통계
GET    /api/status                  # 전체 시스템 상태 (컨테이너 health)
```

### 3.3 데이터 모델

```python
# models.py

class Attack(BaseModel):
    id: str                          # "sqli_login_bypass"
    name: str                        # "SQL Injection - 로그인 우회"
    category: str                    # "SQLi" | "XSS" | "BruteForce" | ...
    cic_ids_label: str               # "Web Attack - Sql Injection"
    description: str                 # 공격 설명
    code: str                        # PoC 소스코드
    language: str                    # "python" | "bash"
    is_preset: bool                  # True=사전준비, False=학생추가
    status: str                      # "idle" | "running" | "completed" | "error"

class Rule(BaseModel):
    id: str                          # "sqli_union_detect"
    name: str                        # "SQLi UNION SELECT 탐지"
    category: str                    # 대응 공격 유형
    content: str                     # Suricata 규칙 원문
    enabled: bool                    # ON/OFF
    is_preset: bool
    sid: int                         # Suricata SID

class Alert(BaseModel):
    timestamp: str
    src_ip: str
    dest_ip: str
    src_port: int
    dest_port: int
    proto: str
    alert_msg: str                   # Suricata alert message
    alert_sid: int
    severity: int
    category: str                    # 매핑된 공격 유형
```

### 3.4 핵심 구현: PoC 실행

```python
# routers/attacks.py

import asyncio
import subprocess
from pathlib import Path

POCS_DIR = Path("pocs")
running_processes: dict[str, subprocess.Popen] = {}

@router.post("/attacks/{attack_id}/run")
async def run_attack(attack_id: str):
    attack = load_attack(attack_id)

    if attack.language == "python":
        cmd = ["python3", str(POCS_DIR / attack.path)]
    else:
        cmd = ["bash", str(POCS_DIR / attack.path)]

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    running_processes[attack_id] = proc

    # 비동기로 결과 수집
    stdout, stderr = proc.communicate(timeout=30)

    return {
        "attack_id": attack_id,
        "exit_code": proc.returncode,
        "stdout": stdout,
        "stderr": stderr,
    }
```

### 3.5 핵심 구현: Suricata 규칙 관리

```python
# routers/rules.py

SURICATA_RULES_DIR = Path("/etc/suricata/rules")
CUSTOM_RULES_FILE = SURICATA_RULES_DIR / "custom.rules"

@router.post("/rules")
async def create_rule(rule: RuleCreate):
    """학생이 새 Suricata 규칙 추가"""
    # 규칙 문법 검증
    validate_suricata_rule(rule.content)

    # custom.rules에 추가
    with open(CUSTOM_RULES_FILE, "a") as f:
        f.write(f"\n# {rule.name}\n{rule.content}\n")

    # Suricata 리로드 (kill -USR2)
    reload_suricata()

    return {"id": rule.id, "status": "applied"}

def reload_suricata():
    """Suricata 규칙 리로드 (재시작 없이)"""
    subprocess.run(
        ["docker", "exec", "suricata",
         "suricatasc", "-c", "reload-rules"],
        check=True
    )
```

### 3.6 핵심 구현: 실시간 Alert 스트리밍

```python
# routers/monitor.py

import json
import asyncio
from fastapi import WebSocket

EVE_LOG = "/var/log/suricata/eve.json"

@router.websocket("/ws/alerts")
async def alert_stream(ws: WebSocket):
    await ws.accept()

    # eve.json을 tail -f 방식으로 읽기
    proc = await asyncio.create_subprocess_exec(
        "tail", "-f", "-n", "0", EVE_LOG,
        stdout=asyncio.subprocess.PIPE
    )

    try:
        while True:
            line = await proc.stdout.readline()
            if not line:
                break
            data = json.loads(line)
            if data.get("event_type") == "alert":
                alert = {
                    "timestamp": data["timestamp"],
                    "src_ip": data["src_ip"],
                    "dest_ip": data["dest_ip"],
                    "alert_msg": data["alert"]["signature"],
                    "alert_sid": data["alert"]["signature_id"],
                    "severity": data["alert"]["severity"],
                    "category": data["alert"].get("category", ""),
                }
                await ws.send_json(alert)
    finally:
        proc.kill()
```

---

## 4. Dashboard 설계 (React)

### 4.1 디렉토리 구조

```
dashboard/
├── src/
│   ├── App.jsx
│   ├── components/
│   │   ├── Layout.jsx              # 3-panel 레이아웃
│   │   ├── AttackPanel/
│   │   │   ├── AttackList.jsx      # 공격 목록 (preset + custom)
│   │   │   ├── AttackCard.jsx      # 개별 공격 카드 (Run 버튼)
│   │   │   ├── AttackEditor.jsx    # [학생] 새 PoC 작성 에디터
│   │   │   └── AttackOutput.jsx    # 실행 결과 터미널 출력
│   │   ├── DefensePanel/
│   │   │   ├── RuleList.jsx        # 규칙 목록 (ON/OFF 토글)
│   │   │   ├── RuleCard.jsx        # 개별 규칙 카드
│   │   │   └── RuleEditor.jsx      # [학생] 새 규칙 작성 에디터
│   │   ├── MonitorPanel/
│   │   │   ├── AlertFeed.jsx       # 실시간 alert 피드
│   │   │   ├── AlertStats.jsx      # 공격 유형별 탐지 통계 차트
│   │   │   └── SystemStatus.jsx    # 컨테이너 상태
│   │   └── common/
│   │       ├── CodeEditor.jsx      # Monaco 에디터 래퍼
│   │       └── Terminal.jsx        # 실행 결과 표시
│   ├── hooks/
│   │   ├── useWebSocket.js         # WebSocket 연결
│   │   └── useApi.js               # REST API 호출
│   └── api.js                      # axios 설정
├── package.json
└── Dockerfile
```

### 4.2 화면 레이아웃

```
┌─────────────────────────────────────────────────────────────────┐
│  🔴 Red/Blue Team Lab                              [Status: ●]  │
├────────────────────┬────────────────────┬───────────────────────┤
│                    │                    │                       │
│  🔴 ATTACK PANEL   │  🔵 DEFENSE PANEL  │  📊 LIVE MONITOR     │
│                    │                    │                       │
│  [+ New Attack]    │  [+ New Rule]      │  ┌─────────────────┐ │
│                    │                    │  │ Alert Feed       │ │
│  ── Preset ──      │  ── Preset ──      │  │                 │ │
│  ┌──────────────┐  │  ┌──────────────┐  │  │ 14:32:01 SQLi   │ │
│  │ SQLi Login   │  │  │ SQLi Detect  │  │  │   detected      │ │
│  │ Bypass       │  │  │ ☑ Enabled    │  │  │ 14:32:03 XSS    │ │
│  │              │  │  │              │  │  │   detected      │ │
│  │ [View] [Run] │  │  │ [View] [⚙]  │  │  │ ...             │ │
│  └──────────────┘  │  └──────────────┘  │  └─────────────────┘ │
│  ┌──────────────┐  │  ┌──────────────┐  │                       │
│  │ SQLi UNION   │  │  │ XSS Detect   │  │  ┌─────────────────┐ │
│  │ SELECT       │  │  │ ☑ Enabled    │  │  │ Detection Stats │ │
│  │              │  │  │              │  │  │                 │ │
│  │ [View] [Run] │  │  │ [View] [⚙]  │  │  │ SQLi    ███░ 4  │ │
│  └──────────────┘  │  └──────────────┘  │  │ XSS     ██░░ 2  │ │
│  ...               │  ...               │  │ BF      █░░░ 1  │ │
│                    │                    │  │ ...             │ │
│  ── Custom ──      │  ── Custom ──      │  └─────────────────┘ │
│  ┌──────────────┐  │  ┌──────────────┐  │                       │
│  │ My Attack #1 │  │  │ My Rule #1   │  │                       │
│  │ [Edit][Run]  │  │  │ [Edit][⚙]   │  │                       │
│  │ [Delete]     │  │  │ [Delete]     │  │                       │
│  └──────────────┘  │  └──────────────┘  │                       │
│                    │                    │                       │
├────────────────────┴────────────────────┴───────────────────────┤
│  [Output Terminal]                                              │
│  $ Running: sqli_login_bypass.py...                             │
│  [+] Found: admin@juice-sh.op / admin123                        │
│  [✓] Attack completed (exit 0)                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4.3 주요 컴포넌트 상세

#### AttackCard — 공격 실행 버튼

```
┌───────────────────────────────┐
│ 🔴 SQL Injection — 로그인 우회  │
│ CIC-IDS: Web Attack - SQLi    │
│ Category: SQLi    Preset: ✓   │
│                               │
│ POST /rest/user/login         │
│ {"email":"' OR 1=1--", ...}   │
│                               │
│ [View Code]  [▶ Run]  [■ Stop]│
└───────────────────────────────┘
```

- **View Code**: 모달로 PoC 전체 소스코드 표시
- **Run**: POST `/api/attacks/{id}/run` → 하단 터미널에 결과 표시
- **Stop**: 실행 중인 공격 중지

#### RuleCard — 규칙 ON/OFF

```
┌───────────────────────────────┐
│ 🔵 SQLi UNION SELECT 탐지      │
│ SID: 100001    Preset: ✓      │
│ [ON ●━━━━━━━━━━━━━━━━━ OFF]   │
│                               │
│ alert http any any -> any ... │
│ content:"UNION"; nocase; ...  │
│                               │
│ [View Full]   [⚙ Edit]       │
└───────────────────────────────┘
```

- **Toggle**: PUT `/api/rules/{id}/toggle` → Suricata 자동 리로드
- **View Full**: 모달로 규칙 전문 표시

#### AttackEditor — 학생 PoC 작성

```
┌───────────────────────────────────────────────┐
│ 새 공격 PoC 등록                                │
│                                               │
│ 이름: [________________________]               │
│ 유형: [SQLi ▼]                                 │
│ 언어: [Python ▼]                               │
│ 설명: [________________________]               │
│                                               │
│ ┌─────────────────────────────────────────┐   │
│ │ # Monaco Editor                         │   │
│ │ import requests                         │   │
│ │                                         │   │
│ │ r = requests.post(                      │   │
│ │   "http://juice-shop:3000/rest/..."     │   │
│ │ ...                                     │   │
│ └─────────────────────────────────────────┘   │
│                                               │
│            [Cancel]  [Save & Register]         │
└───────────────────────────────────────────────┘
```

- Monaco Editor (VS Code 에디터 컴포넌트) 사용
- Python / Bash 선택 가능
- 저장 시 POST `/api/attacks` → 목록에 즉시 반영

#### RuleEditor — 학생 Suricata 규칙 작성

```
┌───────────────────────────────────────────────┐
│ 새 Suricata 규칙 등록                           │
│                                               │
│ 이름: [________________________]               │
│ 유형: [SQLi ▼]                                 │
│                                               │
│ ┌─────────────────────────────────────────┐   │
│ │ alert http any any -> any any (         │   │
│ │   msg:"My custom SQLi rule";           │   │
│ │   content:"DROP TABLE"; nocase;        │   │
│ │   sid:200001; rev:1;)                  │   │
│ └─────────────────────────────────────────┘   │
│                                               │
│ [Syntax Check]   [Cancel]  [Save & Apply]     │
│                                               │
│ ✓ Syntax valid                                │
└───────────────────────────────────────────────┘
```

- Syntax Check: POST `/api/rules/validate` → Suricata 규칙 문법 검증
- Save & Apply: 저장 + Suricata 즉시 리로드

---

## 5. 사전 준비 PoC 목록 (Preset)

| ID | 이름 | 유형 | 언어 | 대상 |
|----|------|------|------|------|
| `sqli_login_bypass` | 로그인 우회 (' OR 1=1--) | SQLi | Python | Juice Shop |
| `sqli_union_select` | UNION SELECT 사용자 추출 | SQLi | Python | Juice Shop |
| `xss_dom` | DOM XSS (검색창) | XSS | Python | Juice Shop |
| `xss_reflected` | Reflected XSS (주문 추적) | XSS | Python | Juice Shop |
| `xss_stored` | Stored XSS (리뷰 API) | XSS | Python | Juice Shop |
| `brute_web` | Web 로그인 Brute Force | BruteForce | Python | Juice Shop |
| `brute_ssh` | SSH Brute Force (Hydra) | BruteForce | Bash | ssh-server |
| `brute_ftp` | FTP Brute Force (Hydra) | BruteForce | Bash | ftp-server |
| `bot_scraper` | 자동 스크래핑 + 주문 | Bot | Python | Juice Shop |
| `dos_slowloris` | Slowloris DoS | DoS | Python | Juice Shop |
| `portscan_nmap` | 내부 네트워크 스캔 | PortScan | Bash | Docker net |
| `infiltration` | 내부망 침투 (SQLi→DB→API) | Infiltration | Python | internal-* |

## 6. 사전 준비 Suricata 규칙 (Preset)

| SID | 이름 | 탐지 대상 |
|-----|------|----------|
| 100001 | SQLi UNION SELECT | `UNION` + `SELECT` in HTTP |
| 100002 | SQLi Auth Bypass | `' OR`, `1=1`, `--` in HTTP body |
| 100003 | XSS script tag | `<script` in HTTP |
| 100004 | XSS javascript scheme | `javascript:` in HTTP |
| 100005 | Web Brute Force | `/rest/user/login` POST ×10/60s |
| 100006 | SSH Brute Force | port 2222 ×5/30s |
| 100007 | FTP Brute Force | port 2121 + `530` ×5/30s |
| 100008 | Bot API scraping | `/api/Products` GET ×50/10s |
| 100009 | DoS slowloris | incomplete HTTP ×100/10s |
| 100010 | PortScan SYN | SYN flags ×100/10s |
| 100011 | Infiltration | frontend→backend-net 연결 |

---

## 7. 보안 제약 (Sandbox)

학생이 임의 코드를 실행하므로 격리가 필요:

| 제약 | 구현 방법 |
|------|----------|
| PoC 실행 격리 | backend 컨테이너 내부에서만 실행 (호스트 접근 불가) |
| 실행 시간 제한 | subprocess timeout=30초, DoS는 60초 |
| 네트워크 제한 | PoC는 Docker 내부 네트워크만 접근 가능 |
| 파일시스템 제한 | PoC 저장 디렉토리만 쓰기 가능 |
| Suricata 규칙 | SID 범위 제한: custom은 200000~ |
| 위험 명령 차단 | `rm`, `dd`, `mkfs` 등 블랙리스트 |

---

## 8. AI IDS 인터페이스 (껍데기)

모델은 후속 연결, 인터페이스만 준비:

```python
# backend/ai_ids.py

class AIIDSInterface:
    """AI 기반 IDS 인터페이스 — 모델은 후속 연결"""

    def predict(self, flow_features: dict) -> dict:
        """
        Input: CIC-IDS 형식의 flow feature dict (79개 feature)
        Output: {"label": str, "confidence": float}
        """
        # TODO: 실제 모델 연결
        return {"label": "BENIGN", "confidence": 0.0, "model": "not_loaded"}

    def load_model(self, model_path: str) -> bool:
        """학생이 학습한 모델 로드"""
        # TODO: 구현
        return False
```

Dashboard에 AI IDS 탭 (비활성 상태로 표시):
```
┌───────────────────────────────┐
│ 🤖 AI IDS (Coming Soon)       │
│                               │
│ Model: Not loaded             │
│ [Upload Model] (비활성)        │
│                               │
│ Predictions: -                │
└───────────────────────────────┘
```

---

## 9. start.sh — 원커맨드 환경 구축

```bash
#!/bin/bash
# 전체 환경 설치 + 실행

echo "=== Red/Blue Team Lab Setup ==="

# 1) Docker 확인
if ! command -v docker &> /dev/null; then
    echo "[!] Docker not found. Install Docker first."
    exit 1
fi

# 2) Docker Compose 빌드 + 실행
docker compose build
docker compose up -d

# 3) 상태 확인
echo "Waiting for services..."
sleep 10
docker compose ps

# 4) 초기 데이터 로드 (preset PoC, rules)
docker exec backend python3 init_presets.py

echo ""
echo "=== Setup Complete ==="
echo "Dashboard:   http://localhost:8080"
echo "Juice Shop:  http://localhost:3000"
echo "Backend API: http://localhost:8000/docs"
echo ""
```

---

## 10. 파일 구조 전체

```
teaching/
├── docker-compose.yml
├── start.sh
├── stop.sh
├── backend/                    # FastAPI 서버
│   ├── Dockerfile
│   ├── main.py
│   ├── routers/
│   ├── pocs/preset/            # 사전 준비 PoC 12종
│   ├── pocs/custom/            # 학생 추가 PoC
│   ├── rules/preset/           # 사전 준비 Suricata 규칙
│   ├── rules/custom/           # 학생 추가 규칙
│   ├── ai_ids.py               # AI IDS 인터페이스 (껍데기)
│   └── requirements.txt
├── dashboard/                  # React 웹 대시보드
│   ├── Dockerfile
│   ├── src/
│   └── package.json
├── suricata/                   # Suricata 설정
│   ├── suricata.yaml
│   └── rules/local.rules
├── services/                   # 추가 서비스 설정
│   ├── ssh/sshd_config
│   ├── ftp/vsftpd.conf
│   ├── internal-api/app.py
│   └── internal-db/init.sql
├── wordlists/
│   └── common.txt              # Brute Force용 (100~500개)
├── scripts/                    # CIC-IDS 분석 스크립트
├── results/                    # 분석 결과
├── docs/
│   └── implementation-design.md
├── main.tex                    # 내부 공유용 슬라이드
├── workshop-design.md          # 수업 설계
└── README.md
```

---

## 11. 구현 우선순위

| 순서 | 작업 | 의존성 |
|------|------|--------|
| 1 | `docker-compose.yml` — 전체 컨테이너 구성 | 없음 |
| 2 | Suricata 설정 + preset 규칙 11종 | 1 |
| 3 | Backend API — 공격 CRUD + 실행 | 1 |
| 4 | Preset PoC 12종 스크립트 작성 | 1, 3 |
| 5 | Backend API — 규칙 CRUD + 리로드 | 2, 3 |
| 6 | Backend API — WebSocket alert 스트리밍 | 2, 3 |
| 7 | Dashboard — 3-panel 레이아웃 | 3 |
| 8 | Dashboard — Attack/Defense 패널 | 3, 5 |
| 9 | Dashboard — Live Monitor + 차트 | 6 |
| 10 | Dashboard — 학생 에디터 (PoC + Rule) | 7, 8 |
| 11 | AI IDS 인터페이스 (껍데기) | 3 |
| 12 | `start.sh` + 오프라인 대비 | 전체 |
