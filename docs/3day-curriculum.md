# 3일 과정 커리큘럼 (고등학생 대상)

- 대상: 고등학생 (보안 비전공)
- 일정: 3일 × 6시간 = 18시간
- 블록 구성: 배경지식(2h) → 실습(30min) → 리뷰(30min) = 3시간/블록
- 하루 2블록
- 환경: OWASP Juice Shop + Docker Compose + Web Dashboard
- 스토리: 공격 → 규칙 기반 방어 → 규칙의 한계 → AI 방어

---

## Day 1: Red Team — 공격 실습

### 목표
- 웹 공격의 원리를 이해한다
- 실제 공격 PoC를 실행하고 결과를 확인한다
- 공격이 네트워크에서 어떻게 보이는지 감을 잡는다

---

### 블록 1 (09:00-12:00) — 웹 공격: SQLi + XSS

**배경지식 (2시간)**
- 웹 애플리케이션 동작 구조
  - 브라우저 → 서버 → DB 흐름
  - HTTP 요청/응답 기본
  - DevTools Network 탭 사용법
- SQL Injection
  - SQL이란? SELECT, WHERE 기본 문법
  - 웹 로그인이 DB에 쿼리하는 구조
  - 입력값이 쿼리에 그대로 들어가면 생기는 문제
  - ' OR 1=1-- 가 왜 동작하는지
  - UNION SELECT로 다른 테이블을 읽는 원리
  - 실제 피해 사례
- XSS (Cross-Site Scripting)
  - 브라우저가 HTML/JavaScript를 실행하는 원리
  - DOM 기초 개념
  - Reflected vs DOM-based vs Stored XSS 차이
  - XSS로 할 수 있는 것 (쿠키 탈취, 세션 하이재킹, 피싱)
  - 실제 피해 사례

**실습 (30분)**
- 문제 1: admin 계정으로 로그인하라 (' OR 1=1--)
- 문제 2: 검색창에서 모든 사용자 이메일을 추출하라 (UNION SELECT)
- 문제 3: 검색창에서 XSS alert을 띄워라 (DOM XSS)
- 문제 4: 상품 리뷰에 스크립트를 삽입하라 (Stored XSS)

**리뷰 (30분)**
- 각 문제 풀이 해설
- DevTools로 요청/응답 함께 확인
- SQLi vs XSS 공격 벡터 차이 정리
- "이 공격이 네트워크 로그에는 어떻게 찍히는가"
- Q&A

---

### 점심 (12:00-13:00)

---

### 블록 2 (13:00-16:00) — 인프라/네트워크 공격: BF + Bot + DoS + PortScan

**배경지식 (2시간)**
- 인증과 Brute Force
  - 인증 매커니즘 (ID/PW, 토큰, 세션, MFA)
  - Brute Force 공격 원리 (사전 대입)
  - 워드리스트란 무엇인가 (rockyou, SecLists)
  - 프로토콜별 차이: HTTP 로그인 vs SSH vs FTP
  - 방어: Rate limiting, Account lockout, CAPTCHA
- Bot 트래픽
  - 정상 사용자 vs 봇의 행동 차이
  - 웹 스크래핑, 자동 구매, 계정 생성 자동화
  - User-Agent, 요청 빈도, 패턴으로 구분
- DoS (Denial of Service)
  - 서버 자원 고갈 원리
  - Slowloris: 연결을 열어놓고 안 닫는 공격
  - 볼륨 기반 vs 애플리케이션 레이어 차이
- PortScan
  - 네트워크 정찰의 첫 단계
  - TCP SYN 스캔 원리
  - nmap 기본 사용법
  - 왜 위험한가: 공격 전 정보 수집
- Infiltration
  - 여러 취약점을 체인으로 연결하는 공격
  - 피벗: 외부 → 웹앱 → 내부망
  - 실제 APT 공격 사례

**실습 (30분)**
- 문제 5: Python 스크립트로 Juice Shop admin 비밀번호를 알아내라 (Web BF)
- 문제 6: SSH 서버의 admin 비밀번호를 알아내라 (SSH BF)
- 문제 7: Juice Shop 전 상품을 자동으로 수집하라 (Bot)
- 문제 8: Docker 내부 네트워크를 스캔하라 (PortScan)
- (데모) Infiltration 체인 공격 시연 (SQLi → 내부 DB → FLAG 획득)

**리뷰 (30분)**
- 각 문제 풀이 해설
- 프로토콜별 brute force 트래픽 패턴 비교
- Bot vs 정상 트래픽의 차이
- Infiltration 데모 해설: "공격이 연결되면 내부망까지 뚫린다"
- Day 1 전체 정리: 오늘 배운 공격 9종
- "이 공격들을 어떻게 탐지하고 막을 수 있을까?" → Day 2 예고

---

## Day 2: Blue Team — IDS 규칙 기반 방어

### 목표
- IDS가 무엇이고 어떻게 동작하는지 이해한다
- Suricata 규칙을 직접 작성할 수 있다
- 공격 → 탐지 → 규칙 개선 사이클을 체험한다
- 규칙 기반 방어의 한계를 체감한다

---

### 블록 1 (09:00-12:00) — IDS 개념 + 규칙 작성

**배경지식 (2시간)**
- 보안 방어 체계 개요
  - 방화벽 vs IDS vs IPS 차이
  - 네트워크 IDS vs 호스트 IDS
  - 시그니처 기반 vs 이상 탐지 기반
- Suricata 소개
  - 오픈소스 IDS 엔진
  - 패킷 캡처 → 규칙 매칭 → 알림 흐름
  - eve.json 로그 포맷
- Suricata 규칙 문법 상세
  - 기본 구조: alert [프로토콜] [출발] -> [목적] (옵션)
  - content: 문자열 매칭 (nocase)
  - pcre: 정규식 매칭
  - http_method, http_uri, http_header: HTTP 필드 지정
  - threshold: 빈도 기반 탐지 (type, track, count, seconds)
  - flow: 방향 지정 (to_server, established)
  - SID, msg, classtype: 메타데이터
- CIC-IDS 2017/2018 데이터셋
  - 실제 공격 트래픽 데이터
  - 79개 feature, 라벨 분류
  - 우리 실습 환경과의 매핑
- 규칙 작성 전략
  - Day 1 공격별 네트워크 시그니처 분석
  - 어디를 보면 되는가 (URI, body, 빈도)

**실습 (30분)**
- preset 규칙 11종을 대시보드에서 하나씩 열어보며 구조 파악
- 규칙 1: SQLi 탐지 규칙 작성 (UNION SELECT 패턴)
  - 함께 한 줄씩 작성
  - 대시보드 [+ New Rule] → 저장 → 적용
  - SQLi 공격 재실행 → 탐지 확인
- 규칙 2: XSS 탐지 규칙 작성 (`<script` 패턴)
  - 학생이 직접 작성 시도
  - 저장 → 적용 → XSS 공격 → 탐지 확인

**리뷰 (30분)**
- 작성한 규칙 해설
- "내가 만든 규칙이 공격을 잡았다"
- content 매칭이 패킷에서 어떻게 동작하는지
- 오탐 가능성: 정상 요청에 SELECT가 들어가면?
- Q&A

---

### 점심 (12:00-13:00)

---

### 블록 2 (13:00-16:00) — 규칙 실전 + 공격-방어 대결

**배경지식 (2시간)**
- threshold 심화
  - Brute Force 탐지: "5초에 10번 로그인 시도"
  - Bot 탐지: "10초에 30번 API 호출"
  - count/seconds 조합에 따른 오탐/미탐 트레이드오프
  - track by_src vs by_dst
- 규칙 튜닝 전략
  - 너무 느슨하면: 미탐 (공격을 놓침)
  - 너무 빡빡하면: 오탐 (정상을 잡음)
  - 실제 운영에서의 튜닝 사이클
- 규칙 기반 방어의 한계
  - 알려진 패턴만 잡는다
  - 공격 변형에 취약하다
  - 우회 기법: 인코딩, 대소문자, 분할 등
  - 제로데이 공격에 무력
- 공격 변형 예시
  - SQLi: `' OR 1=1--` → `' OR '1'='1` → URL 인코딩
  - XSS: `<script>` → `<ScRiPt>` → `<img onerror=...>`
  - "모든 변형을 규칙으로 막을 수 있는가?" → 불가능

**실습 (30분)**
- 규칙 3: Brute Force 탐지 규칙 작성 (threshold 설정)
  - threshold 값을 바꿔가며 테스트
  - "count를 3으로 하면? 100으로 하면?"
- 규칙 4: Bot 스크래핑 탐지 규칙 작성
- 공격-방어 대결 미니 라운드
  - 강사가 변형 공격 실행 → 학생 규칙이 잡는지 확인
  - 잡히면 → 공격 변형 → 다시 시도
  - "규칙을 우회하는 건 패턴만 바꾸면 된다"

**리뷰 (30분)**
- 규칙 4종 전체 정리
- 공격-방어 대결 결과 분석
- 규칙 기반의 한계 정리:
  - 알려진 패턴만 잡는다
  - 변형되면 못 잡는다
  - 새로운 공격(제로데이)에 무력
- "패턴이 아니라 행동 특성으로 판단하면?" → Day 3 AI 예고
- Q&A

---

## Day 3: AI IDS + 종합

### 목표
- AI/ML 기초 개념을 이해한다
- 실제 공격 데이터로 모델을 학습하고 추론한다
- 규칙 기반과 AI 기반의 차이를 비교한다
- 종합 CTF로 3일간 배운 것을 활용한다

---

### 블록 1 (09:00-12:00) — AI/ML 기초 + 모델 학습

**배경지식 (2시간)**
- 인공지능/머신러닝이란
  - 규칙 프로그래밍 vs 데이터로 학습
  - 지도학습: 입력(feature) → 출력(label)
  - 분류 문제란: "이 트래픽이 공격인가 정상인가"
- 네트워크 트래픽의 feature
  - CIC-IDS 2017 데이터셋의 79개 feature
  - 주요 feature: Flow Duration, Packet Length, Flow Bytes/s 등
  - "공격 유형마다 feature 값이 다르다"
  - feature 엔지니어링 간단 소개
- Decision Tree
  - 직관적 설명: "스무고개처럼 질문을 던져서 분류"
  - 트리 구조 시각화
  - 장점: 해석 가능, 단점: 과적합
- Random Forest
  - "여러 트리가 투표하면 더 정확하다"
  - 앙상블 개념
- 평가 지표
  - 정확도(accuracy)
  - 혼동행렬(confusion matrix): TP, FP, TN, FN
  - "정확도 99%인데 정말 좋은 건가?" (클래스 불균형)
  - Precision, Recall 개념
- 학습 파이프라인
  - 데이터 로드 → 전처리 → 분할 → 학습 → 평가
  - sklearn 라이브러리 소개
  - train/test split 개념
  - 과적합(overfitting) 설명

**실습 (30분)**
- 단계 1: CIC-IDS 2017 CSV 로드 + 데이터 탐색 (pandas)
  - Label 분포 확인
  - Web Attack 레코드 필터링
  - 주요 feature 통계 확인
- 단계 2: 데이터 전처리 (inf/NaN 제거, label 인코딩)
- 단계 3: train/test split (80/20)
- 단계 4: Decision Tree 학습 → 정확도 확인
- 단계 5: Random Forest 학습 → 정확도 비교
- 단계 6: feature importance 확인 ("어떤 특성이 가장 중요한지")

**리뷰 (30분)**
- 모델 학습 결과 해설
- confusion matrix 함께 분석
- "어떤 공격을 잘 잡고, 어떤 걸 못 잡는지"
- feature importance 해석
- Decision Tree vs Random Forest 비교
- Q&A

---

### 점심 (12:00-13:00)

---

### 블록 2 (13:00-16:00) — AI IDS 연동 + 종합 CTF

**배경지식 (2시간 중 1시간)**
- 규칙 기반 vs AI 기반 비교
  - 규칙: 빠르고 정확, 알려진 패턴만
  - AI: 변형에 강함, 오탐 가능, 학습 데이터 의존
  - 실제 보안 현장: 하이브리드 (규칙 + AI)
- AI IDS를 실제 시스템에 연동하는 방법
  - feature 추출 → 모델 추론 → alert 생성
  - 실시간 vs 배치 처리
- 비교 실험 설계
  - Day 2에서 규칙이 못 잡은 변형 공격
  - 같은 공격을 AI에 넣으면?

**실습 (30분)**
- 비교 실험:
  - 규칙이 못 잡은 변형 SQLi → AI 모델에 입력 → 분류 결과 확인
  - "규칙은 놓쳤는데 AI는 잡았다"
  - AI가 못 잡는 케이스도 확인 → "만능은 아니다"
- 종합 CTF (팀 대항전):
  - 미션 1: 변형 SQLi로 로그인 우회 (공격)
  - 미션 2: 미션 1을 탐지하는 규칙 작성 (방어)
  - 미션 3: CIC-IDS 데이터에서 특정 공격을 분류하는 모델 학습 (AI)
  - 미션 4: 자유 미션 — 새 공격 PoC 또는 새 규칙 작성

**리뷰 (30분)**
- CTF 결과 발표 + 시상
- 3일간 배운 것 정리:
  - Day 1: 공격의 원리 — "이렇게 뚫린다"
  - Day 2: 방어의 원리 — "이렇게 잡는다 + 한계"
  - Day 3: AI 활용 — "이렇게 개선한다"
- 실제 보안 업계에서의 활용
  - SOC (Security Operations Center)
  - SIEM + IDS + AI 통합
  - 보안 분야 진로
- Q&A + 마무리

---

## 요약

### 시간 구조

| 날 | 블록 1 (09:00-12:00) | 블록 2 (13:00-16:00) |
|----|---------------------|---------------------|
| Day 1 | 웹 공격 (SQLi + XSS) | 인프라/네트워크 공격 (BF + Bot + DoS + PortScan) |
| Day 2 | IDS 개념 + 규칙 작성 (SQLi/XSS 탐지) | 규칙 실전 (BF/Bot 탐지) + 대결 + 한계 |
| Day 3 | AI/ML 기초 + 모델 학습 | AI IDS 비교 + 종합 CTF |

### 블록 구성 (일관)

```
배경지식: 2시간
실습: 30분
리뷰: 30분
= 3시간/블록
```

### 문제 수

| 날 | 실습 문제 | 내용 |
|----|--------|------|
| Day 1 블록 1 | 4문제 | SQLi 2 + XSS 2 |
| Day 1 블록 2 | 4문제 + 데모 | BF 2 + Bot 1 + PortScan 1 + Infiltration 데모 |
| Day 2 블록 1 | 규칙 2종 작성 | SQLi 탐지 + XSS 탐지 |
| Day 2 블록 2 | 규칙 2종 작성 + 대결 | BF 탐지 + Bot 탐지 + 변형 공격 대결 |
| Day 3 블록 1 | 6단계 | 데이터 탐색 → 전처리 → 분할 → DT → RF → feature importance |
| Day 3 블록 2 | 비교 실험 + CTF 4미션 | 규칙 vs AI 비교 + 종합 CTF |

### 스토리 흐름

```
Day 1: "이렇게 뚫린다" (공격 9종 체험)
         ↓
Day 2: "이렇게 잡는다" (규칙 4종 작성) → "그런데 한계가 있다" (변형 우회)
         ↓
Day 3: "AI로 개선한다" (모델 학습) → "둘 다 쓰는 게 최선" (하이브리드)
```
