"""
Telegram bot handlers for processing messages and commands.
"""

import logging
from typing import Any

from scheduler.location_tracker import LocationTracker
from services.openai_client import OpenAIClient
from services.user_settings import user_settings
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

logger = logging.getLogger(__name__)

# Global location tracker instance
location_tracker = LocationTracker(interval_minutes=10)


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
    chat_id = update.effective_chat.id
    message_id = update.message.message_id

    # Check if this is a live location
    is_live = location.live_period is not None
    logger.info(
        f"Received location: {latitude}, {longitude} "
        f"(live: {is_live}, chat: {chat_id}, msg: {message_id})"
    )

    # For live locations, check if we should send a fact based on timing
    if is_live and not location_tracker.should_send_fact(chat_id, message_id):
        logger.debug(f"Skipping fact - interval not reached")
        return

    # Send typing indicator
    await context.bot.send_chat_action(
        chat_id=chat_id, action="typing"
    )

    try:
        # Get interesting fact from OpenAI with user's reasoning settings
        user_id = update.effective_user.id
        reasoning_effort = user_settings.get_reasoning_effort(user_id)
        openai_client = OpenAIClient(reasoning_effort=reasoning_effort)
        fact = await openai_client.get_location_fact(latitude, longitude)

        await update.message.reply_text(fact)

    except Exception as e:
        logger.error(f"Error getting location fact: {e}")
        error_message = (
            "😔 Извините, произошла ошибка при получении информации "
            "о данной локации. Попробуйте еще раз."
        )
        await update.message.reply_text(error_message)


async def handle_edited_location(update: Update, context: Any) -> None:
    """Handle edited location messages (live location updates)."""
    if not update.edited_message or not update.edited_message.location:
        return

    location = update.edited_message.location
    latitude = location.latitude
    longitude = location.longitude
    chat_id = update.effective_chat.id
    message_id = update.edited_message.message_id

    # Check if live location has ended (live_period is None when user stops sharing)
    if location.live_period is None:
        logger.info(
            f"Live location ended for chat {chat_id}, message {message_id} "
            f"at {latitude}, {longitude}"
        )
        location_tracker.end_session(chat_id, message_id)
        return

    logger.info(
        f"Received edited location: {latitude}, {longitude} "
        f"(chat: {chat_id}, msg: {message_id}, live_period: {location.live_period}s)"
    )

    # Check if we should send a fact based on timing
    if not location_tracker.should_send_fact(chat_id, message_id):
        logger.debug(f"Skipping fact - interval not reached")
        return

    # Send typing indicator
    await context.bot.send_chat_action(
        chat_id=chat_id, action="typing"
    )

    try:
        # Get interesting fact from OpenAI with user's reasoning settings
        user_id = update.effective_user.id
        reasoning_effort = user_settings.get_reasoning_effort(user_id)
        openai_client = OpenAIClient(reasoning_effort=reasoning_effort)
        fact = await openai_client.get_location_fact(latitude, longitude)

        # Reply to the original message
        await context.bot.send_message(chat_id=chat_id, text=fact)

    except Exception as e:
        logger.error(f"Error getting location fact for edited location: {e}")
        error_message = (
            "😔 Извините, произошла ошибка при получении информации "
            "о данной локации. Попробуйте еще раз."
        )
        await context.bot.send_message(chat_id=chat_id, text=error_message)


async def help_command(update: Update, context: Any) -> None:
    """Handle /help command."""
    help_text = (
        "🤖 ExcursoBot - бот интересных фактов о местах\n\n"
        "📍 Просто отправьте мне геолокацию, и я расскажу "
        "удивительный факт о ближайшем месте!\n\n"
        "Команды:\n"
        "/start - начать работу с ботом\n"
        "/help - показать эту справку\n"
        "/reason <level> - настроить уровень рассуждений AI"
    )
    await update.message.reply_text(help_text)


async def reason_command(update: Update, context: Any) -> None:
    """Handle /reason command to set reasoning effort level."""
    user_id = update.effective_user.id

    # If no arguments, show current setting and available levels
    if not context.args:
        current_level = user_settings.get_reasoning_effort(user_id)
        current_desc = user_settings.get_level_description(current_level)

        help_text = (
            f"🧠 Текущий уровень рассуждений: **{current_level}**\n"
            f"{current_desc}\n\n"
            "Доступные уровни:\n"
            "• `none` - Без рассуждений (максимальная скорость)\n"
            "• `minimal` - Минимальные рассуждения\n"
            "• `low` - Низкий уровень\n"
            "• `medium` - Средний уровень (по умолчанию)\n"
            "• `high` - Высокий уровень (лучшее качество)\n\n"
            "Использование: `/reason <level>`\n"
            "Пример: `/reason high`"
        )
        await update.message.reply_text(help_text, parse_mode="Markdown")
        return

    # Set new level
    new_level = context.args[0].lower()

    if user_settings.set_reasoning_effort(user_id, new_level):
        description = user_settings.get_level_description(new_level)
        success_text = (
            f"✅ Уровень рассуждений изменён на **{new_level}**\n\n"
            f"{description}\n\n"
            "Новые факты будут генерироваться с этим уровнем."
        )
        await update.message.reply_text(success_text, parse_mode="Markdown")
    else:
        error_text = (
            f"❌ Неверный уровень: `{new_level}`\n\n"
            "Доступные уровни: `none`, `minimal`, `low`, `medium`, `high`\n"
            "Пример: `/reason medium`"
        )
        await update.message.reply_text(error_text, parse_mode="Markdown")


def setup_handlers(application: Application) -> None:
    """Setup bot handlers."""
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("reason", reason_command))

    # Location handlers
    application.add_handler(MessageHandler(filters.LOCATION, handle_location))

    # Edited message handler for live location updates
    application.add_handler(
        MessageHandler(filters.LOCATION & filters.UpdateType.EDITED_MESSAGE, handle_edited_location)
    )

    logger.info("Bot handlers setup completed")
