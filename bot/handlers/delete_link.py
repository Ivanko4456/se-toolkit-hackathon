"""Handler for deleting links via /delete command."""

import logging
import os

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

import httpx

logger = logging.getLogger(__name__)

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


async def cmd_delete(message: types.Message):
    """Show user's links with delete buttons."""
    user_id = str(message.from_user.id)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{API_BASE_URL}/api/links",
                params={"user_id": user_id, "limit": "20"},
            )
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        logger.error("Failed to fetch links for deletion: %s", e)
        await message.answer("❌ Failed to load links. Please try again later.")
        return

    links = data.get("links", [])
    if not links:
        await message.answer("📭 No links to delete.")
        return

    text = "🗑 <b>Select a link to delete:</b>\n"
    builder = InlineKeyboardBuilder()

    for link in links:
        title = link.get("title") or link.get("url")
        # Truncate long titles
        if len(title) > 40:
            title = title[:37] + "..."
        link_id = link["id"]
        builder.button(text=f"🗑 {title}", callback_data=f"delete_{link_id}")

    builder.adjust(1)
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")


async def cb_delete(callback: types.CallbackQuery):
    """Handle delete button callback."""
    user_id = str(callback.from_user.id)
    link_id = callback.data.replace("delete_", "")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.delete(
                f"{API_BASE_URL}/api/links/{link_id}",
                params={"user_id": user_id},
            )
            resp.raise_for_status()
    except httpx.HTTPStatusError as e:
        logger.error("Backend returned error on delete: %s", e.response.text)
        await callback.answer("❌ Failed to delete link.", show_alert=True)
        return
    except Exception as e:
        logger.error("Failed to delete link: %s", e)
        await callback.answer("❌ Error occurred. Try again.", show_alert=True)
        return

    await callback.answer("✅ Link deleted!", show_alert=True)

    # Update message to remove the deleted button
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{API_BASE_URL}/api/links",
                params={"user_id": user_id, "limit": "20"},
            )
            resp.raise_for_status()
            data = resp.json()

        links = data.get("links", [])
        if not links:
            await callback.message.edit_text("📭 No links left.")
            return

        text = "🗑 <b>Select a link to delete:</b>\n"
        builder = InlineKeyboardBuilder()

        for link in links:
            title = link.get("title") or link.get("url")
            if len(title) > 40:
                title = title[:37] + "..."
            lid = link["id"]
            builder.button(text=f"🗑 {title}", callback_data=f"delete_{lid}")

        builder.adjust(1)
        await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    except Exception:
        pass  # Ignore errors on refresh
