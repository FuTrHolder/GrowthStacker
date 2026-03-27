"""
post_log.py
게시된 포스트 기록을 JSON 파일로 관리합니다.
- 같은 키워드 중복 게시 방지
- GitHub Actions 워크플로우에서 커밋으로 영속 저장
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

LOG_PATH = Path(os.environ.get("POST_LOG_PATH", "post_log.json"))


def _load() -> dict:
    if LOG_PATH.exists():
        try:
            return json.loads(LOG_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {"posts": [], "keywords_used": []}


def _save(data: dict) -> None:
    LOG_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def is_keyword_used(keyword: str) -> bool:
    """해당 키워드가 이미 사용됐는지 확인합니다."""
    data = _load()
    return keyword.lower() in [k.lower() for k in data.get("keywords_used", [])]


def record_post(publish_result: dict) -> None:
    """게시 완료된 포스트를 로그에 기록합니다."""
    data = _load()

    data["keywords_used"].append(publish_result["keyword"])
    data["posts"].append(
        {
            "post_id": publish_result["post_id"],
            "title": publish_result["title"],
            "url": publish_result["url"],
            "keyword": publish_result["keyword"],
            "niche": publish_result.get("niche", ""),
            "published_at": publish_result["published_at"],
        }
    )

    _save(data)


def get_stats() -> dict:
    """로그 요약 통계를 반환합니다."""
    data = _load()
    posts = data.get("posts", [])
    return {
        "total_posts": len(posts),
        "keywords_used": len(data.get("keywords_used", [])),
        "latest": posts[-1] if posts else None,
    }
