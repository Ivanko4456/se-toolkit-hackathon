"""LLM client for extracting structured data from user messages.

Uses Ollama-compatible endpoint. Falls back to regex-based extraction if LLM fails.
"""

import json
import logging
import os
import re
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

LLM_API_URL = os.getenv("LLM_API_URL", "http://llm:11434/api/generate")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2")

SYSTEM_PROMPT = """Extract structured data from this user message:
- URL: [detect the URL from the message]
- Title: [suggest a title based on context, or leave empty]
- Tags: [extract keywords as a list]

User message: "{user_input}"

Respond ONLY in valid JSON format: {{"url": "...", "title": "...", "tags": ["tag1", "tag2"]}}"""


async def extract_link_data(user_input: str) -> Optional[dict]:
    """Send user input to LLM and parse structured response.

    Returns dict with keys: url, title, tags — or None on failure.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                LLM_API_URL,
                json={
                    "model": LLM_MODEL,
                    "prompt": SYSTEM_PROMPT.format(user_input=user_input),
                    "stream": False,
                },
            )
            response.raise_for_status()
            data = response.json()
            llm_output = data.get("response", "")
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
