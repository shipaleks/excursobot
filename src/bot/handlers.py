"""
Telegram bot handlers for processing messages and commands.
"""

import logging
from typing import Any

from services.openai_client import OpenAIClient
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

logger = logging.getLogger(__name__)


async def start(update: Update, context: Any) -> None:
    """Handle /start command."""
    welcome_message = (
        "👋 Привет! Я ExcursoBot.\n\n"
        "📍 Отправьте мне геолокацию, и я расскажу интересный факт "
        "о ближайшем месте!\n\n"
        "Для отправки локации нажмите 📎 → Локация."
    )
    await update.message.reply_text(welcome_message)


async def handle_location(update: Update, context: Any) -> None:
    """Handle location messages and return interesting facts."""
    if not update.message or not update.message.location:
        return

    location = update.message.location
    latitude = location.latitude
    longitude = location.longitude

    logger.info(f"Received location: {latitude}, {longitude}")

    # Send typing indicator
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action="typing"
    )

    try:
        # Get interesting fact from OpenAI
        openai_client = OpenAIClient()
        fact = await openai_client.get_location_fact(latitude, longitude)

        await update.message.reply_text(fact)

    except Exception as e:
        logger.error(f"Error getting location fact: {e}")
        error_message = (
            "😔 Извините, произошла ошибка при получении информации "
            "о данной локации. Попробуйте еще раз."
        )
        await update.message.reply_text(error_message)


async def help_command(update: Update, context: Any) -> None:
    """Handle /help command."""
    help_text = (
        "🤖 ExcursoBot - бот интересных фактов о местах\n\n"
        "📍 Просто отправьте мне геолокацию, и я расскажу "
        "удивительный факт о ближайшем месте!\n\n"
        "Команды:\n"
        "/start - начать работу с ботом\n"
        "/help - показать эту справку"
    )
    await update.message.reply_text(help_text)


def setup_handlers(application: Application) -> None:
    """Setup bot handlers."""
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Location handler
    application.add_handler(MessageHandler(filters.LOCATION, handle_location))

    logger.info("Bot handlers setup completed")
