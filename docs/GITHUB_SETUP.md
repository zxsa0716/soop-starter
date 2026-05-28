# GitHub 공개 가이드

본 문서는 숲스타터를 GitHub에 안전하게 공개하기 위한 단계별 가이드이다. PowerShell 또는 Git Bash 환경을 가정한다.

## 1. 사전 점검 (보안 검증)

GitHub에 push하기 **전에** 반드시 다음을 확인한다.

### 1.1 .env 파일이 추적되지 않는지 확인

```powershell
cd E:\forestLLM
# .env가 있으면 제외 대상에 포함되는지 확인
git check-ignore .env
# 출력: .env  → 정상 (추적 제외됨)
```

### 1.2 코드에 API 키가 남아있지 않은지 확인

```powershell
# AIzaSy로 시작하는 Gemini 키 검색
Select-String -Path "**\*.py" -Pattern "AIzaSy" -Recurse

# sk-, ghp_, xoxb- 등 다른 키도 검색
Select-String -Path "**\*.py","**\*.md","**\*.yml" -Pattern "sk-|ghp_|xoxb-|AIzaSy" -Recurse

# 출력이 비어있어야 함 (.env.example 한 줄은 무방)
```

### 1.3 대용량 / 저작권 파일 제외 확인

```powershell
git status
# refs/ 폴더, *.pkl, *.parquet, *.gpkg 등이 보이지 않아야 함
```

## 2. GitHub 저장소 생성

### 2.1 GitHub 웹에서 새 저장소 만들기

1. https://github.com/new 접속
2. 다음 항목을 입력
   - **Repository name**: `soop-starter` (또는 원하는 이름)
   - **Description**: `한국 청년 임업인 산촌 진입 의사결정 지원 시스템`
   - **Visibility**: Public (또는 Private)
   - **Initialize this repository with**: 모두 체크 해제 (README, .gitignore, license는 이미 로컬에 있음)
3. **Create repository** 클릭
4. 다음 화면의 저장소 URL을 복사 (예: `https://github.com/Heedo-cs/soop-starter.git`)

## 3. 로컬 Git 초기화 및 첫 커밋

### 3.1 PowerShell에서 실행

```powershell
cd E:\forestLLM

# Git 초기화 (이미 .git 폴더가 있으면 생략)
git init

# 사용자 정보 설정 (전역 설정이 없는 경우)
git config user.name "Heedo"
git config user.email "zxsa0716@kookmin.ac.kr"

# 첫 커밋 전에 .env 파일이 실수로 추가되지 않는지 한 번 더 확인
git status
```

### 3.2 staging area에 파일 추가

```powershell
# 모든 추적 대상 파일 추가
git add .

# 무엇이 추가되었는지 확인 (.env가 있으면 안 됨)
git status

# 문제 없으면 첫 커밋
git commit -m "Initial commit: 숲스타터 v1.0 - 산촌 진입 의사결정 지원 시스템"
```

### 3.3 GitHub 저장소와 연결 후 push

```powershell
# main 브랜치 사용 (master가 기본이면 변경)
git branch -M main

# 원격 저장소 추가 (URL은 본인 것으로 교체)
git remote add origin https://github.com/Heedo-cs/soop-starter.git

# Push
git push -u origin main
```

처음 push 시 GitHub 인증 화면이 나타날 수 있다.

## 4. GitHub Personal Access Token 발급 (HTTPS 인증)

비밀번호 인증이 deprecated 되었으므로 Personal Access Token이 필요하다.

1. https://github.com/settings/tokens 접속
2. **Generate new token** → **Generate new token (classic)** 클릭
3. 다음 항목 입력
   - **Note**: `soop-starter-push` (식별용 이름)
   - **Expiration**: 90 days (또는 원하는 기간)
   - **Select scopes**: `repo` (전체 체크)
4. **Generate token** 클릭
5. 표시되는 토큰을 복사 (한 번만 볼 수 있음)
6. `git push` 시 비밀번호 자리에 이 토큰을 붙여넣기

## 5. 후속 push (자주 쓰는 명령)

```powershell
# 작업 후 변경 사항 확인
git status
git diff

# 변경 파일을 staging area에 추가
git add streamlit_app/soop_app.py
# 또는 모든 변경 파일을 한 번에
git add .

# 커밋
git commit -m "fix: 임산물 비교 ROI 계산 버그 수정"

# Push
git push
```

## 6. .env 실수로 commit한 경우 (긴급 복구)

만약 실수로 `.env` 또는 API 키를 commit하여 push 했다면, **즉시 다음 조치**를 취한다.

### 6.1 모든 API 키 폐기

- Gemini API key: https://aistudio.google.com/apikey 에서 해당 키 삭제 후 새로 발급
- 공공데이터 API: data.go.kr에서 활용신청 취소 후 재발급

### 6.2 Git 히스토리에서 제거

```powershell
# git-filter-repo 도구 설치 (한 번만)
pip install git-filter-repo

# .env 파일을 모든 commit에서 제거
git filter-repo --invert-paths --path .env

# 원격 저장소에 강제 push (히스토리 재작성)
git push origin --force --all
```

### 6.3 collaborator에게 알림

다른 사람이 fork했거나 clone했을 가능성이 있으므로 보안 사고를 알리고 키 폐기를 통보한다.

## 7. 저장소 README 시각화 첨부

GitHub README의 시각화는 자동으로 렌더링된다. 본 저장소의 `docs/figures/` 폴더 PNG는 README.md 또는 다른 문서에서 상대 경로로 참조하면 자동 표시된다.

```markdown
![M03 결과](docs/figures/r2_per_product.png)
```

## 8. GitHub Releases (선택)

학술 발표용 PPTX·DOCX는 git tracking 대상에서 제외되어 있으므로, GitHub Releases 기능으로 별도 배포한다.

1. https://github.com/사용자이름/soop-starter/releases/new 접속
2. **Choose a tag**: `v1.0.0` 입력 후 **Create new tag**
3. **Release title**: `Soop Starter v1.0 - 학술 발표 자료`
4. **Description**: 변경 사항 요약
5. **Attach binaries by dropping them here**: PPTX, DOCX, Streamlit demo zip 파일 드래그
6. **Publish release** 클릭

## 9. Streamlit Community Cloud 배포 (선택)

코드만 push한 후 다음 단계로 무료 클라우드 배포 가능.

1. https://share.streamlit.io 접속 후 GitHub 계정 연결
2. **New app** 클릭
3. 저장소 선택: `Heedo-cs/soop-starter`
4. **Main file path**: `streamlit_app/soop_app.py`
5. **Advanced settings**:
   - Python version: 3.10 또는 3.11
   - Secrets: `GEMINI_API_KEY="AIzaSy..."` (Streamlit 내부 secrets에만 저장됨)
6. **Deploy** 클릭

배포 후 `https://soop-starter.streamlit.app` 형식의 URL이 발급되며, 심사위원에게 클릭만으로 시연 가능한 링크를 제공할 수 있다.

## 10. 권장 후속 작업

### 10.1 라이선스 명시

이미 LICENSE 파일이 있으나, README 상단에 명시적으로 표시한다.

```markdown
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
```

### 10.2 GitHub Actions CI (선택)

`.github/workflows/ci.yml` 파일을 추가하여 매 push 시 자동 테스트를 수행할 수 있다.

```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r streamlit_app/requirements.txt
      - run: python -c "import ast; ast.parse(open('streamlit_app/soop_app.py').read())"
```

### 10.3 Issue 템플릿

`.github/ISSUE_TEMPLATE/bug_report.md` 및 `.github/ISSUE_TEMPLATE/feature_request.md`를 만들어 협업자가 이슈를 체계적으로 제출하도록 안내한다.

## 11. 체크리스트

push 전 최종 확인:

- [ ] `.env`가 `.gitignore`에 등록되어 있다
- [ ] `git status`에서 `.env`가 보이지 않는다
- [ ] 코드에 `AIzaSy`, `sk-` 등 키가 남아있지 않다
- [ ] `refs/` 폴더 (저작권 PDF)는 제외된다
- [ ] `*.pkl`, `*.parquet`, `*.gpkg` 등 대용량 binary는 제외된다
- [ ] README.md가 학자 톤 한국어로 작성되어 있다
- [ ] docs/ 폴더에 METHODOLOGY, REFERENCES, ARCHITECTURE, RESULTS가 있다
- [ ] docs/figures/에 14개 PNG가 있다
- [ ] LICENSE 파일이 있다
- [ ] requirements.txt가 정확하다

위 11개 항목을 모두 확인한 후 push한다.
