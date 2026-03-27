# Auto Blogger — GitHub Actions + Gemini + Blogger

매일 자동으로 SEO 최적화 영문 블로그 포스트를 생성하고 Blogger에 게시합니다.  
**완전 무료** (Gemini Flash 무료 티어 + Blogger 무료 플랫폼)

---

## 구조

```
auto-blogger/
├── .github/
│   └── workflows/
│       └── auto_post.yml      ← GitHub Actions cron 정의
├── src/
│   ├── content_generator.py   ← Gemini로 포스트 생성
│   ├── blogger_publisher.py   ← Blogger API 게시
│   └── post_log.py            ← 중복 방지 로그 관리
├── main.py                    ← 오케스트레이터
├── post_log.json              ← 게시 기록 (자동 커밋)
└── requirements.txt
```

---

## 설정 순서

### 1. Gemini API 키 발급 (무료)

1. [Google AI Studio](https://aistudio.google.com/apikey) 접속
2. **Create API Key** 클릭
3. 키 복사 후 보관

### 2. Blogger 서비스 계정 설정

#### 2-1. Google Cloud 프로젝트 설정
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성 (또는 기존 프로젝트 선택)
3. **API 및 서비스 > 라이브러리** 에서 **Blogger API v3** 활성화

#### 2-2. 서비스 계정 생성
1. **IAM 및 관리자 > 서비스 계정** 이동
2. **서비스 계정 만들기** 클릭
3. 이름 입력 후 생성
4. **키 탭 > 키 추가 > JSON** 으로 키 파일 다운로드

#### 2-3. Blogger 블로그에 서비스 계정 권한 부여
1. Blogger 대시보드 > **설정 > 사용자**
2. 서비스 계정 이메일(`...@...iam.gserviceaccount.com`) 을 **작성자** 권한으로 추가

#### 2-4. Blog ID 확인
- Blogger 대시보드 URL에서 확인:  
  `https://www.blogger.com/blog/posts/[BLOG_ID]`

### 3. GitHub Secrets 등록

저장소 **Settings > Secrets and variables > Actions > New repository secret**:

| Secret 이름 | 값 |
|---|---|
| `GEMINI_API_KEY` | Google AI Studio에서 발급한 키 |
| `BLOGGER_SERVICE_ACCOUNT_JSON` | 다운로드한 JSON 파일 전체 내용 (붙여넣기) |
| `BLOGGER_BLOG_ID` | Blogger 블로그 ID (숫자) |

> ⚠️ **보안**: 키를 코드에 직접 작성하지 마세요. Secrets는 로그에도 출력되지 않습니다.

### 4. 저장소 생성 및 파일 업로드

```bash
git init auto-blogger
cd auto-blogger
# 파일 복사 후
git add .
git commit -m "init: auto blogger setup"
git remote add origin https://github.com/YOUR_USERNAME/auto-blogger.git
git push -u origin main
```

### 5. 실행 확인

- **Actions 탭** 에서 워크플로우 수동 실행 (workflow_dispatch)
- 성공 시 Blogger에 포스트가 게시되고 `post_log.json` 이 자동 커밋됩니다

---

## 스케줄 변경

`auto_post.yml` 의 cron 표현식 수정:

```yaml
# 매일 오전 9시 (KST = UTC+9)
- cron: "0 0 * * *"

# 주 3회 (월/수/금 오전 9시 KST)
- cron: "0 0 * * 1,3,5"

# 매일 2회 (오전 9시, 오후 9시 KST)
- cron: "0 0,12 * * *"
```

---

## 키워드 추가

`src/content_generator.py` 의 `KEYWORD_POOLS` 딕셔너리에 직접 추가:

```python
KEYWORD_POOLS = {
    "ai_money": [
        "your new keyword here",
        ...
    ],
}
```

---

## 비용

| 항목 | 비용 |
|---|---|
| Gemini 1.5 Flash API | 무료 (분당 15회, 일 1500회) |
| Blogger 플랫폼 | 무료 |
| GitHub Actions | 무료 (월 2000분) |
| **합계** | **$0** |
