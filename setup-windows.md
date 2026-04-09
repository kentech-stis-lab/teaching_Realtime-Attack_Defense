# Windows 설치 가이드

## 사전 요구사항

1. **Windows 10/11** (64-bit)
2. **Docker Desktop** 설치

## Step 1: Docker Desktop 설치

1. https://www.docker.com/products/docker-desktop 접속
2. "Download for Windows" 클릭 → 설치
3. 설치 중 "Use WSL 2 instead of Hyper-V" 체크 (권장)
4. 설치 완료 후 재부팅
5. Docker Desktop 실행 → 트레이 아이콘이 녹색이면 준비 완료

### Docker Desktop이 안 뜨면
- Windows 기능에서 "WSL 2" 또는 "Hyper-V" 활성화 필요
- 관리자 권한 PowerShell에서: `wsl --install`
- 재부팅 후 Docker Desktop 다시 실행

## Step 2: 프로젝트 다운로드

### 방법 A: Git 사용
```cmd
git clone https://github.com/kentech-stis-lab/teaching_Realtime-Attack_Defense.git
cd teaching_Realtime-Attack_Defense
```

### 방법 B: ZIP 다운로드
1. https://github.com/kentech-stis-lab/teaching_Realtime-Attack_Defense 접속
2. "Code" → "Download ZIP" 클릭
3. 압축 해제

## Step 3: 실행

```cmd
start.bat
```

더블클릭하거나 cmd에서 실행. 첫 실행 시 Docker 이미지 빌드에 5~10분 소요.

완료되면 브라우저가 자동으로 열립니다:
- **대시보드**: http://localhost:8080
- **Juice Shop**: http://localhost:3000

## Step 4: 종료

```cmd
stop.bat
```

## 문제 해결

### "Docker daemon is not running"
→ Docker Desktop이 실행 중인지 확인 (트레이 아이콘)

### "port is already allocated"
→ 이미 3000, 8000, 8080 포트를 쓰는 프로그램이 있음
→ 해당 프로그램을 종료하거나, docker-compose.yml에서 포트 변경

### 빌드가 너무 오래 걸림
→ 첫 빌드만 오래 걸림 (이미지 다운로드). 두 번째부터는 빠름

### WSL 관련 에러
→ 관리자 PowerShell에서: `wsl --update`
→ 재부팅 후 다시 시도

## SQLi 실습 (Windows cmd)

```cmd
curl -X POST http://localhost:3000/rest/user/login ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"' OR 1=1--\",\"password\":\"x\"}"
```

## 포트 정보

| 포트 | 서비스 |
|------|--------|
| 3000 | Juice Shop |
| 8000 | Backend API |
| 8080 | Dashboard |
| 2222 | SSH Server |
| 2121 | FTP Server |
