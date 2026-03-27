"""
blogger_publisher.py
Blogger API v3를 사용하여 포스트를 자동으로 게시합니다.
- OAuth2 대신 API Key + 서비스 계정 방식 사용 (GitHub Actions 환경)
- 모든 자격증명은 환경변수에서만 읽습니다
"""

import os
import re
import json
import html
import markdown
from datetime import datetime, timezone
from google.oauth2 import service_account
from googleapiclient.discovery import build


# ─────────────────────────────────────────────
# 인증 초기화
# ─────────────────────────────────────────────
BLOGGER_SCOPES = ["https://www.googleapis.com/auth/blogger"]


def _get_blogger_service():
    """
    서비스 계정 JSON을 환경변수에서 읽어 Blogger 서비스 객체 반환.
    GitHub Secret: BLOGGER_SERVICE_ACCOUNT_JSON (JSON 전체 내용)
    """
    sa_json = os.environ.get("BLOGGER_SERVICE_ACCOUNT_JSON")
    if not sa_json:
        raise EnvironmentError(
            "BLOGGER_SERVICE_ACCOUNT_JSON 환경변수가 설정되지 않았습니다."
        )

    sa_info = json.loads(sa_json)
    credentials = service_account.Credentials.from_service_account_info(
        sa_info, scopes=BLOGGER_SCOPES
    )
    return build("blogger", "v3", credentials=credentials)


# ─────────────────────────────────────────────
# Markdown → HTML 변환
# ─────────────────────────────────────────────
def _md_to_html(md_text: str) -> tuple[str, str, str]:
    """
    Markdown을 HTML로 변환하고 제목 / 본문 / 썸네일 프롬프트를 분리합니다.
    Returns: (title, body_html, thumbnail_prompt)
    """
    lines = md_text.strip().splitlines()

    # H1 추출 → 포스트 제목
    title = "Blog Post"
    body_lines = []
    thumbnail_prompt = ""

    for line in lines:
        if line.startswith("# ") and title == "Blog Post":
            title = line[2:].strip()
        elif line.lower().startswith("**thumbnail prompt:**"):
            thumbnail_prompt = line.split(":", 1)[-1].strip().strip("*").strip()
        else:
            body_lines.append(line)

    body_md = "\n".join(body_lines)

    # Markdown → HTML
    body_html = markdown.markdown(
        body_md,
        extensions=["extra", "nl2br", "sane_lists"],
    )

    # SEO 기본 스타일 주입
    styled_html = f"""<div style="font-family:Georgia,serif;max-width:780px;margin:0 auto;line-height:1.8;color:#222;">
{body_html}
</div>"""

    return title, styled_html, thumbnail_prompt


# ─────────────────────────────────────────────
# 태그 추출 (H2 헤딩 기반)
# ─────────────────────────────────────────────
def _extract_labels(md_text: str, keyword: str) -> list[str]:
    """키워드와 H2 섹션에서 Blogger 라벨(태그)을 추출합니다."""
    labels = set()

    # 키워드에서 핵심 단어 추출
    stop = {"to", "the", "a", "an", "for", "with", "and", "or", "in", "on", "of", "how"}
    words = [w for w in re.split(r"\W+", keyword.lower()) if w and w not in stop]
    labels.update(words[:4])

    # H2 헤딩에서 라벨
    for match in re.finditer(r"^## (.+)$", md_text, re.MULTILINE):
        heading = match.group(1).strip()
        if len(heading) < 25:
            labels.add(heading.title())

    return sorted(labels)[:8]  # Blogger 라벨 최대 20개, 여유 있게 8개


# ─────────────────────────────────────────────
# 포스트 게시
# ─────────────────────────────────────────────
def publish_post(content_data: dict) -> dict:
    """
    생성된 콘텐츠를 Blogger에 게시합니다.

    content_data 필드:
        keyword   : str  — 타겟 키워드
        niche     : str  — 니치 분류
        content   : str  — Markdown 전문
        content_type: str

    Returns:
        {"post_id": ..., "url": ..., "title": ..., "published_at": ...}
    """
    blog_id = os.environ.get("BLOGGER_BLOG_ID")
    if not blog_id:
        raise EnvironmentError("BLOGGER_BLOG_ID 환경변수가 설정되지 않았습니다.")

    service = _get_blogger_service()

    md_text = content_data["content"]
    keyword = content_data["keyword"]

    title, body_html, thumbnail_prompt = _md_to_html(md_text)
    labels = _extract_labels(md_text, keyword)

    now_iso = datetime.now(timezone.utc).isoformat()

    post_body = {
        "kind": "blogger#post",
        "title": title,
        "content": body_html,
        "labels": labels,
        "published": now_iso,
    }

    result = (
        service.posts()
        .insert(blogId=blog_id, body=post_body, isDraft=False)
        .execute()
    )

    return {
        "post_id": result["id"],
        "url": result.get("url", ""),
        "title": title,
        "keyword": keyword,
        "niche": content_data.get("niche", ""),
        "thumbnail_prompt": thumbnail_prompt,
        "published_at": now_iso,
    }
