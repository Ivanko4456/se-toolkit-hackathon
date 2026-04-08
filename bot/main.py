"""LinkSaver Telegram Bot main entry point."""

import asyncio
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# MUST be before any other imports that use env vars!
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart

from handlers.commands import cmd_mylinks, cmd_start, cmd_help
from handlers.save_link import handle_save_link
from handlers.delete_link import cmd_delete, cb_delete

logger = logging.getLogger(__name__)


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


async def main() -> None:
    setup_logging()

    logger.info(f"Loaded .env from {env_path}")
    logger.info(f"API_BASE_URL={os.getenv('API_BASE_URL')}")

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not set. Exiting.")
        sys.exit(1)

    bot = Bot(token=token)
    dp = Dispatcher()

    # Command handlers
    dp.message.register(cmd_start, CommandStart())
    dp.message.register(cmd_help, Command("help"))
    dp.message.register(cmd_mylinks, Command("mylinks"))
    dp.message.register(cmd_delete, Command("delete"))

    # Save link handler — any message containing "http"
    async def has_link(message) -> bool:
        return message.text and "http" in message.text.lower()

    dp.message.register(handle_save_link, has_link)

    # Delete callback
    dp.callback_query.register(cb_delete, lambda c: c.data.startswith("delete_"))

    logger.info("Bot started. Listening for messages...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
