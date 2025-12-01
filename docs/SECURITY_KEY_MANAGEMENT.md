# API 키 보안 관리 가이드

> **⚠️ 중요**: API 키는 절대 코드나 문서에 직접 작성하지 마세요!

---

## 🚨 키 노출 시 즉시 조치

### 1. Google Cloud Console에서 키 폐기/재발급

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 프로젝트 선택: `Nexsupply (id: gen-lang-client-0791049134)`
3. **APIs & Services → Credentials** 이동
4. 노출된 키 찾기 → **Delete** 또는 **Regenerate** 클릭

### 2. GitHub에서 키 제거

1. 레포를 **Private**로 전환 (Settings → Danger Zone)
2. 키가 포함된 파일에서 키 제거
3. 커밋 및 푸시
4. Git history 정리 (선택적, 아래 참고)

---

## ✅ 올바른 키 관리 방법

### 로컬 개발 환경

1. **`.env` 파일에만 저장**
   ```bash
   # .env 파일 (절대 Git에 커밋하지 마세요!)
   GEMINI_API_KEY=실제_키_값
   ```

2. **코드에서 읽기**
   ```python
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   api_key = os.getenv("GEMINI_API_KEY")
   ```

3. **`.gitignore` 확인**
   ```
   .env
   .env.local
   .env.*.local
   ```

### GitHub Actions / CI/CD

1. **GitHub Secrets에 저장**
   - Repository → Settings → Secrets and variables → Actions
   - New repository secret 클릭
   - Name: `GEMINI_API_KEY`
   - Value: 실제 API 키

2. **워크플로에서 사용**
   ```yaml
   env:
     GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
   ```

### Vercel / Render / Supabase 등 배포 환경

- 각 플랫폼의 **Environment Variables** 또는 **Secrets** 기능 사용
- 절대 코드에 하드코딩하지 않기

---

## 📝 문서 작성 시 주의사항

### ❌ 잘못된 예시
```markdown
GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
```

### ✅ 올바른 예시
```markdown
GEMINI_API_KEY=YOUR_GEMINI_API_KEY

**중요**: 실제 키를 여기에 넣지 말고 `.env` 파일에 저장하세요.
```

---

## 🔧 Git History에서 키 제거 (선택적)

키가 이미 커밋 히스토리에 포함되어 있다면:

### 방법 1: git filter-repo 사용 (권장)

```bash
# 1. git-filter-repo 설치
pip install git-filter-repo

# 2. 스크립트 실행
bash scripts/remove_leaked_key.sh

# 3. 강제 푸시 (⚠️ 주의: 팀원들에게 미리 알려야 함)
git push origin --force --all
git push origin --force --tags
```

### 방법 2: BFG Repo-Cleaner 사용

```bash
# 1. BFG 설치
brew install bfg  # macOS
# 또는 https://rtyley.github.io/bfg-repo-cleaner/ 에서 다운로드

# 2. 키 제거
bfg --replace-text passwords.txt

# 3. 강제 푸시
git push origin --force --all
```

---

## 🛡️ 예방 조치

### 1. Pre-commit Hook 설정

`.git/hooks/pre-commit` 파일 생성:

```bash
#!/bin/bash
# API 키 패턴 검사
if git diff --cached | grep -E "AIzaSy[A-Za-z0-9_-]{35}"; then
    echo "❌ ERROR: Potential API key detected in commit!"
    echo "Please remove the API key and use .env file instead."
    exit 1
fi
```

### 2. GitHub Actions에서 자동 검사

`.github/workflows/security-check.yml`:

```yaml
- name: Check for leaked secrets
  run: |
    if grep -r "AIzaSy" --include="*.md" --include="*.py" .; then
      echo "⚠️ WARNING: Potential API key found!"
      exit 1
    fi
```

### 3. gitleaks 사용 (권장)

```bash
# 설치
brew install gitleaks  # macOS

# 검사
gitleaks detect --source . --verbose
```

---

## 📋 체크리스트

키를 사용하기 전에 확인:

- [ ] `.env` 파일에 키가 저장되어 있는가?
- [ ] `.env` 파일이 `.gitignore`에 포함되어 있는가?
- [ ] 코드에 하드코딩된 키가 없는가?
- [ ] 문서에 실제 키가 없는가?
- [ ] GitHub Secrets에 키가 저장되어 있는가? (CI/CD 사용 시)
- [ ] 배포 환경의 Environment Variables에 키가 저장되어 있는가?

---

## 🆘 문제 발생 시

1. **즉시 키 폐기/재발급** (Google Cloud Console)
2. **GitHub에서 키 제거** (파일 수정 + 커밋)
3. **Git History 정리** (선택적)
4. **사용량 확인** (GCP Console에서 API 호출량 체크)
5. **요금 확인** (Billing에서 이상 사용량 체크)

---

## 참고 자료

- [Google Cloud API Key 보안 가이드](https://cloud.google.com/docs/authentication/api-keys)
- [GitHub Secrets 가이드](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)

