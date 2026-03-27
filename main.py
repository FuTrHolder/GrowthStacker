"""
main.py
GitHub Actions에서 실행되는 자동 블로그 포스팅 오케스트레이터.

실행 흐름:
  1. 키워드 풀에서 미사용 키워드 선택
  2. Gemini API로 SEO 블로그 포스트 생성
  3. Blogger API로 자동 게시
  4. post_log.json에 기록 후 Git 커밋 (워크플로우가 처리)
"""

import sys
import time
import traceback

from src.content_generator import pick_keyword, generate_post
from src.blogger_publisher import publish_post
from src.post_log import is_keyword_used, record_post, get_stats

MAX_KEYWORD_RETRIES = 10  # 키워드 중복 시 최대 재시도 횟수


def select_fresh_keyword() -> dict:
    """중복되지 않은 키워드를 찾아 반환합니다."""
    for attempt in range(MAX_KEYWORD_RETRIES):
        meta = pick_keyword()
        if not is_keyword_used(meta["keyword"]):
            return meta
        print(f"  [skip] 이미 사용된 키워드 ({attempt+1}/{MAX_KEYWORD_RETRIES}): {meta['keyword']}")

    # 모든 키워드가 소진된 경우 마지막 선택지 강제 사용
    print("  [warn] 사용 가능한 새 키워드가 없어 마지막 선택지를 재사용합니다.")
    return meta


def run():
    print("=" * 60)
    print("  AUTO BLOGGER — 자동 SEO 포스팅 시작")
    print("=" * 60)

    # ── 1. 키워드 선택 ──────────────────────────────────────────
    print("\n[1/3] 키워드 선택 중...")
    meta = select_fresh_keyword()
    print(f"  키워드  : {meta['keyword']}")
    print(f"  니치    : {meta['niche']}")
    print(f"  유형    : {meta['content_type']}")
    print(f"  독자    : {meta['audience']}")

    # ── 2. 콘텐츠 생성 ─────────────────────────────────────────
    print("\n[2/3] Gemini로 블로그 포스트 생성 중...")
    start = time.time()
    content_data = generate_post(meta)
    elapsed = round(time.time() - start, 1)
    char_count = len(content_data["content"])
    print(f"  생성 완료: {char_count:,}자 ({elapsed}s)")

    # ── 3. Blogger 게시 ────────────────────────────────────────
    print("\n[3/3] Blogger에 포스트 게시 중...")
    result = publish_post(content_data)
    print(f"  제목    : {result['title']}")
    print(f"  URL     : {result['url']}")
    print(f"  Post ID : {result['post_id']}")

    # ── 4. 로그 저장 ───────────────────────────────────────────
    record_post(result)
    stats = get_stats()
    print(f"\n  누적 포스트: {stats['total_posts']}개")

    # 썸네일 프롬프트 출력 (Actions 로그에서 확인 가능)
    if result.get("thumbnail_prompt"):
        print(f"\n  썸네일 프롬프트:\n  {result['thumbnail_prompt']}")

    print("\n  완료!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        traceback.print_exc()
        sys.exit(1)
