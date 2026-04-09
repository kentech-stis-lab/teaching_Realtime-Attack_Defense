# 3일 과정 요약

- 대상: 고등학생 | 3일 × 6시간 = 18시간
- 블록: 배경(2h) → 실습(30min) → 리뷰(30min) = 3h/블록, 하루 2블록
- 스토리: 뚫린다 → 잡는다 → 한계 → AI로 개선

---

## Day 1: Red Team — 공격

### 오전 — 웹 공격 (SQLi + XSS)

- 배경지식 (2h)
  - 웹 애플리케이션 동작 구조 (브라우저 → 서버 → DB)
  - HTTP 요청/응답 기본, DevTools 사용법
  - SQL Injection: SQL 기본 문법, 쿼리 삽입 원리, ' OR 1=1--, UNION SELECT
  - XSS: 브라우저 스크립트 실행 원리, DOM/Reflected/Stored 차이, 쿠키 탈취
- 실습 (30min)
  - 문제 1: SQLi 로그인 우회 (' OR 1=1--)
  - 문제 2: UNION SELECT로 사용자 이메일 추출
  - 문제 3: DOM XSS (검색창 alert)
  - 문제 4: Stored XSS (리뷰에 스크립트 삽입)
- 리뷰 (30min)
  - 풀이 해설 + DevTools로 요청/응답 확인
  - SQLi vs XSS 공격 벡터 차이 정리

### 오후 — 인프라/네트워크 공격 (BF + Bot + DoS + PortScan)

- 배경지식 (2h)
  - 인증 구조, Brute Force 원리, 워드리스트
  - 프로토콜별 차이: HTTP vs SSH vs FTP
  - Bot 트래픽 특성, 정상 vs 봇 행동 차이
  - DoS: slowloris 원리, 서버 자원 고갈
  - PortScan: TCP SYN 스캔, nmap 기본
  - Infiltration: 취약점 체인, 외부 → 웹앱 → 내부망 피벗
- 실습 (30min)
  - 문제 5: Web Brute Force (Python 스크립트)
  - 문제 6: SSH Brute Force
  - 문제 7: Bot 자동 스크래핑
  - 문제 8: PortScan (nmap)
  - (데모) Infiltration 체인 공격 시연
- 리뷰 (30min)
  - 풀이 해설 + 트래픽 패턴 비교
  - Day 1 전체 정리: 공격 9종
  - "이걸 어떻게 막지?" → Day 2 예고

---

## Day 2: Blue Team — 규칙 기반 방어

### 오전 — IDS 개념 + 규칙 작성

- 배경지식 (2h)
  - 방화벽 vs IDS vs IPS 차이
  - Suricata 소개, 패킷 캡처 → 규칙 매칭 → 알림 흐름
  - 규칙 문법: content, pcre, http_method, http_uri, threshold, flow
  - SID, msg, classtype 메타데이터
  - CIC-IDS 2017/2018 데이터셋 소개
  - Day 1 공격별 네트워크 시그니처 분석
- 실습 (30min)
  - preset 규칙 11종 구조 파악
  - 규칙 직접 작성 1: SQLi 탐지 (UNION SELECT 패턴)
  - 규칙 직접 작성 2: XSS 탐지 (`<script` 패턴)
  - 공격 재실행 → 탐지 확인
- 리뷰 (30min)
  - 작성한 규칙 해설
  - content 매칭이 패킷에서 동작하는 방식
  - 오탐 가능성 논의

### 오후 — 규칙 실전 + 대결 + 한계

- 배경지식 (2h)
  - threshold 심화: count/seconds 조합, by_src vs by_dst
  - 규칙 튜닝: 느슨하면 미탐, 빡빡하면 오탐
  - 규칙 기반의 한계: 알려진 패턴만 탐지
  - 우회 기법: 인코딩, 대소문자, 분할
  - 변형 공격 예시: `' OR 1=1--` → `' OR '1'='1`, `<script>` → `<ScRiPt>`
  - 제로데이에 무력
- 실습 (30min)
  - 규칙 직접 작성 3: Brute Force 탐지 (threshold 설정)
  - 규칙 직접 작성 4: Bot 탐지 (빈도 기반)
  - 변형 공격 대결: 강사가 변형 → 학생 규칙이 잡는지 확인
- 리뷰 (30min)
  - 규칙 4종 전체 정리
  - 대결 결과 분석
  - 한계 정리: "변형하면 못 잡는다", "제로데이에 무력"
  - "패턴 대신 행동 특성으로 판단하면?" → Day 3 예고

---

## Day 3: AI IDS + 종합

### 오전 — AI/ML 기초 + 모델 학습

- 배경지식 (2h)
  - 머신러닝이란: 규칙 프로그래밍 vs 데이터 학습
  - 분류 문제: feature → label
  - CIC-IDS feature 79개, 공격 유형별 특성 차이
  - Decision Tree: "스무고개처럼 질문으로 분류"
  - Random Forest: "여러 트리가 투표"
  - 평가: accuracy, confusion matrix, precision/recall
  - "정확도 99%인데 진짜 좋은 건가?" (클래스 불균형)
  - sklearn 소개, train/test split, 과적합
- 실습 (30min)
  - 단계 1: CIC-IDS CSV 로드 + 데이터 탐색
  - 단계 2: 전처리 (inf/NaN 제거, label 인코딩)
  - 단계 3: train/test split (80/20)
  - 단계 4: Decision Tree 학습 → 정확도 확인
  - 단계 5: Random Forest 학습 → 비교
  - 단계 6: feature importance 확인
- 리뷰 (30min)
  - confusion matrix 분석: "어떤 공격을 잘 잡고, 못 잡는지"
  - DT vs RF 비교
  - feature importance 해석

### 오후 — AI IDS 연동 + 종합 CTF

- 배경지식 (1h)
  - 규칙 기반 vs AI 기반 장단점 비교
  - 하이브리드 접근: 규칙 + AI
  - 실제 보안 현장: SOC, SIEM + IDS + AI
- 실습 (30min)
  - 비교 실험: 규칙이 못 잡은 변형 공격 → AI 모델 추론 → 잡히는지 확인
  - 종합 CTF (팀 대항전):
    - 미션 1: 변형 SQLi로 로그인 우회 (공격)
    - 미션 2: 미션 1을 탐지하는 규칙 작성 (방어)
    - 미션 3: CIC-IDS 데이터에서 공격 분류 모델 학습 (AI)
    - 미션 4: 자유 미션 (새 PoC 또는 새 규칙)
- 리뷰 (30min)
  - CTF 결과 + 시상
  - 3일 정리: 뚫린다 → 잡는다 → 한계 → AI로 개선 → 둘 다 쓰는 게 최선
  - 보안 분야 진로 소개

---

## 스토리

```
Day 1: "이렇게 뚫린다"
  ↓
Day 2: "이렇게 잡는다" → "한계가 있다"
  ↓
Day 3: "AI로 개선한다" → "둘 다 쓰는 게 최선"
```
