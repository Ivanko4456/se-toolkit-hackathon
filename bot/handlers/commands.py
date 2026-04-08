"""Telegram bot command handlers (/start, /help, /mylinks)."""

import logging

from aiogram import types
from aiogram.utils.markdown import hbold, hlink, hcode

import httpx

logger = logging.getLogger(__name__)

API_BASE_URL = __import__("os").getenv("API_BASE_URL", "http://localhost:8000")


async def cmd_start(message: types.Message):
    """Welcome message with short tutorial."""
    text = (
        f"👋 {hbold('Hi!')} I'm LinkSaver Bot.\n\n"
        "📌 <b>How to save a link:</b>\n"
        "Just send me a message with a URL. You can add tags with #\n"
        'For example: <code>https://example.com #python #tutorial</code>\n\n'
        "🔍 <b>How to find links:</b>\n"
        f"{hcode('/mylinks')} — all your links\n"
        f"{hcode('/mylinks python')} — links tagged with python\n\n"
        f"{hcode('/help')} — help"
    )
    await message.answer(text, parse_mode="HTML")


async def cmd_help(message: types.Message):
    """Help message with usage examples."""
    text = (
        "📖 <b>LinkSaver — Help</b>\n\n"
        "<b>Commands:</b>\n"
        f"{hcode('/start')} — welcome message\n"
        f"{hcode('/help')} — this help\n"
        f"{hcode('/mylinks [tag]')} — your links\n"
        f"{hcode('/delete')} — delete a link\n\n"
        "<b>Saving a link:</b>\n"
        "Send a message with a URL:\n"
        "  <code>https://habr.com/article/123 #habr #dev</code>\n\n"
        "The bot will extract the URL, pick a title and tags, and save to the database.\n"
        "If something goes wrong — it will ask for clarification."
    )
    await message.answer(text, parse_mode="HTML")


async def cmd_mylinks(message: types.Message):
    """Fetch and display user's links, optionally filtered by tag."""
    user_id = str(message.from_user.id)
    parts = message.text.split(maxsplit=1)
    tag = parts[1].strip() if len(parts) > 1 else None

    params: dict = {"user_id": user_id, "limit": "20"}
    if tag:
        params["tag"] = tag

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{API_BASE_URL}/api/links", params=params)
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        logger.error("Failed to fetch links: %s", e)
        await message.answer("❌ Failed to load links. Please try again later.")
        return

    links = data.get("links", [])
    if not links:
        query = f" with tag <b>{hbold(tag)}</b>" if tag else ""
        await message.answer(f"📭 No links{query} yet.")
        return

    lines = [f"📌 <b>Your links{' (' + tag + ')' if tag else ''}:</b>\n"]
    for link in links:
        title = link.get("title") or link.get("url")
        url = link.get("url")
        tags = ", ".join(f"#{t}" for t in link.get("tags", []))
        lines.append(f"• {hlink(title, url)} {tags}")

    await message.answer("\n".join(lines), parse_mode="HTML", disable_web_page_preview=True)
