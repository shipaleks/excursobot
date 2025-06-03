"""
ExcursoBot - Telegram bot that provides interesting facts about locations.

Entry point of the application.
"""

import logging
import os
from pathlib import Path

from bot.handlers import setup_handlers
from dotenv import load_dotenv
from telegram.ext import Application

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Main function to initialize and run the bot."""
    # Get bot token from environment
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        logger.error("TELEGRAM_TOKEN environment variable is not set")
        return

    # Create application
    application = Application.builder().token(token).build()

    # Setup handlers
    setup_handlers(application)

    logger.info("Starting ExcursoBot...")

    # Start the bot
    application.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()
