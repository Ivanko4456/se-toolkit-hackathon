"""Handler for saving links from user messages."""

import logging
import os
import re

from aiogram import types

import httpx

logger = logging.getLogger(__name__)

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Regex to extract URL from message
URL_RE = re.compile(r'https?://[^\s<>"]+')
# Regex to extract hashtags
TAG_RE = re.compile(r'#(\w+)')


async def handle_save_link(message: types.Message):
    """Process a message containing a URL: extract via regex and save."""
    user_input = message.text or ""
    user_id = str(message.from_user.id)

    # Extract URL
    url_match = URL_RE.search(user_input)
    if not url_match:
        await message.answer(
            "❌ Could not find a URL in the message. Please send a message with a link.",
        )
        return

    url = url_match.group(0)
    # Extract hashtags as tags
    tags = TAG_RE.findall(user_input)

    # Send typing action
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    # Save via backend API
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{API_BASE_URL}/api/links",
                json={
                    "url": url,
                    "title": None,
                    "tags": tags,
                    "user_id": user_id,
                },
            )
            resp.raise_for_status()
    except httpx.HTTPStatusError as e:
        logger.error("Backend returned error: %s", e.response.text)
        await message.answer(f"❌ Error saving link: {e.response.status_code}")
        return
    except Exception as e:
        logger.error("Failed to save link: %s", e)
        await message.answer("❌ Could not save link. Please try again later.")
        return

    # Confirmation
    tags_str = " ".join(f"#{t}" for t in tags) if tags else ""
    await message.answer(
        f"✅ Link saved!\n\n"
        f"📎 <a href=\"{url}\">{url}</a>\n"
        f"🏷 {tags_str}".strip(),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
