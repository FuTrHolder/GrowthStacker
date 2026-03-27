"""
content_generator.py
Gemini API (google-genai SDK) 를 사용하여 SEO 최적화 블로그 포스트를 생성합니다.
- google.generativeai (deprecated) 대신 google.genai 사용
- 모든 API 키는 환경변수에서만 읽습니다
"""

import os
import random
from google import genai
from google.genai import types


# ─────────────────────────────────────────────
# Gemini 클라이언트 초기화
# ─────────────────────────────────────────────
def _get_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
    return genai.Client(api_key=api_key)


# gemini-2.0-flash: 무료 티어 지원 최신 모델
MODEL_ID = "gemini-2.0-flash"


# ─────────────────────────────────────────────
# 키워드 풀
# ─────────────────────────────────────────────
KEYWORD_POOLS = {
    "ai_money": [
        "how to make money with AI tools for beginners",
        "best AI tools for passive income 2026",
        "how to use ChatGPT to make money online",
        "best AI writing tools for freelancers 2026",
        "how to start an AI automation business from scratch",
        "how to earn money with Gemini AI for free",
        "best AI side hustles for beginners in 2026",
        "how to make money with AI content creation",
    ],
    "product_review": [
        "best budget laptops for students 2026 review",
        "notion vs obsidian for productivity which is better",
        "best AI image generators compared 2026",
        "grammarly vs quillbot review for bloggers",
        "best free project management tools for freelancers",
        "canva pro vs adobe express honest review 2026",
    ],
    "tech_tutorial": [
        "how to automate blog posting with Python beginners guide",
        "how to use Google Gemini API for free step by step",
        "how to set up GitHub Actions for beginners 2026",
        "how to build a simple chatbot with Gemini API",
        "how to make money blogging step by step for beginners",
        "how to create SEO blog posts with AI tools free",
    ],
}

CONTENT_TYPES = ["how-to guide", "list article", "review/comparison"]
AUDIENCES = ["beginners", "freelancers", "bloggers", "entrepreneurs"]


def pick_keyword() -> dict:
    niche = random.choice(list(KEYWORD_POOLS.keys()))
    keyword = random.choice(KEYWORD_POOLS[niche])
    return {
        "niche": niche,
        "keyword": keyword,
        "content_type": random.choice(CONTENT_TYPES),
        "audience": random.choice(AUDIENCES),
    }


# ─────────────────────────────────────────────
# 블로그 포스트 생성
# ─────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert SEO blog writer targeting US traffic for Google AdSense monetization.

STRICT RULES:
- Write 100% in natural, human-like English
- Grade 6-8 reading level
- No fluff, no repetitive AI phrases
- Short paragraphs (2-4 lines max)
- Include at least ONE unique angle or real-world use case
- Only include verifiable, accurate information
- Do NOT fabricate statistics or tools

MANDATORY STRUCTURE (use exact H1/H2/H3 markdown):
1. # [SEO Title - clickable, keyword-included]
2. ## Introduction  (hook + problem statement, 2-3 paragraphs)
3. ## Why It Matters  (context + benefits)
4. ## [Main Content Section]  (step-by-step OR list OR comparison)
5. ## Practical Tips  (3-5 actionable bullet points)
6. ## Conclusion  (summary + key takeaway)
7. ## FAQ  (exactly 4 Q&A pairs)
8. **Thumbnail Prompt:** [single-line image prompt]

Output: clean Markdown ONLY. No extra commentary."""


def generate_post(meta: dict) -> dict:
    """
    Gemini로 블로그 포스트 생성.
    Returns: {"keyword": ..., "content": ..., "niche": ..., "content_type": ...}
    """
    client = _get_client()

    user_prompt = (
        f"Write a complete SEO-optimized blog post.\n"
        f"Target keyword: \"{meta['keyword']}\"\n"
        f"Content type: {meta['content_type']}\n"
        f"Target audience: {meta['audience']}\n"
        f"Niche: {meta['niche'].replace('_', ' ')}\n\n"
        f"Follow the mandatory structure exactly. Output Markdown only."
    )

    response = client.models.generate_content(
        model=MODEL_ID,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.75,
            max_output_tokens=2048,
        ),
    )

    content = response.text.strip()
    return {
        "keyword": meta["keyword"],
        "niche": meta["niche"],
        "content_type": meta["content_type"],
        "content": content,
    }
