"""LLM client for extracting structured data from user messages.

Uses OpenAI-compatible API (Qwen Code / OpenRouter / etc).
Falls back to regex-based extraction if LLM fails.
"""

import json
import logging
import os
import re
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_API_BASE_URL = os.getenv("LLM_API_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen-plus")

SYSTEM_PROMPT = """You are a helpful assistant that extracts structured data from user messages.

When the user sends a message containing a URL, respond with ONLY valid JSON in this exact format:
{"url": "the URL", "title": "a suggested title or null", "tags": ["tag1", "tag2"]}

Rules:
- Extract the full URL from the message.
- Suggest a title based on context, or use null.
- Extract relevant keywords as tags.
- Return ONLY the JSON object, no additional text."""


async def extract_link_data(user_input: str) -> Optional[dict]:
    """Send user input to LLM and parse structured response.

    Returns dict with keys: url, title, tags — or None on failure.
    """
    if not LLM_API_KEY:
        logger.warning("LLM_API_KEY not set. Falling back to regex.")
        return _fallback_extract(user_input)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{LLM_API_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {LLM_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost",
                    "X-Title": "LinkSaver Bot",
                },
                json={
                    "model": LLM_MODEL,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_input},
                    ],
                    "temperature": 0.1,
                },
            )
            response.raise_for_status()
            data = response.json()
            llm_output = data["choices"][0]["message"]["content"]
            return _parse_llm_response(llm_output)
    except Exception as e:
        logger.warning("LLM request failed: %s. Falling back to regex.", e)
        return _fallback_extract(user_input)


def _parse_llm_response(text: str) -> Optional[dict]:
    """Try to parse LLM output as JSON with structured link data."""
    # Extract JSON block if wrapped in code fences
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None

    try:
        data = json.loads(match.group())
        # Validate required fields
        url = data.get("url")
        if not url:
            return None
        return {
            "url": url,
            "title": data.get("title") or None,
            "tags": _normalize_tags(data.get("tags", [])),
        }
    except (json.JSONDecodeError, TypeError):
        return None


def _fallback_extract(user_input: str) -> Optional[dict]:
    """Regex-based fallback: extract URL and hashtags from message."""
    url_match = re.search(r"https?://\S+", user_input)
    if not url_match:
        return None

    url = url_match.group(0).strip("<>,.!)")
    # Extract hashtags as tags
    tags = re.findall(r"#(\w+)", user_input)
    # Try to guess a title from non-URL, non-hashtag text
    title_text = re.sub(r"https?://\S+", "", user_input)
    title_text = re.sub(r"#\w+", "", title_text).strip()
    title = title_text if title_text else None

    return {
        "url": url,
        "title": title,
        "tags": _normalize_tags(tags),
    }


def _normalize_tags(tags: list) -> list[str]:
    """Clean and deduplicate tags."""
    cleaned = []
    seen = set()
    for tag in tags:
        tag = str(tag).strip().lower().replace("#", "")
        if tag and tag not in seen:
            cleaned.append(tag)
            seen.add(tag)
    return cleaned
