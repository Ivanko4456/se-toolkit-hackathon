"""Handler for saving links from user messages."""

import logging
import os

from aiogram import types

import httpx

from llm_client import extract_link_data

logger = logging.getLogger(__name__)

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


async def handle_save_link(message: types.Message):
    """Process a message containing a URL: extract data via LLM and save."""
    user_input = message.text or ""
    user_id = str(message.from_user.id)

    # Check if message contains http
    if "http" not in user_input.lower():
        await message.answer(
            "❌ Could not find a URL in the message. Please send a message with a link.",
        )
        return

    # Send typing action
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    # Extract structured data via LLM (with fallback)
    extracted = await extract_link_data(user_input)

    if not extracted:
        await message.answer(
            "❌ Could not find a URL in the message. Please send a message with a link.",
        )
        return

    url = extracted["url"]
    title = extracted.get("title")
    tags = extracted.get("tags", [])

    # Save via backend API
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{API_BASE_URL}/api/links",
                json={
                    "url": url,
                    "title": title,
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
    title_display = title or url
    await message.answer(
        f"✅ Link saved!\n\n"
        f"📎 <a href=\"{url}\">{title_display}</a>\n"
        f"🏷 {tags_str}".strip(),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
