"""
Unit tests for bot handlers.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from bot.handlers import handle_location, help_command, setup_handlers, start
from telegram import Chat, Location, Message, Update
from telegram.ext import Application


@pytest.fixture
def mock_update():
    """Create a mock Update object."""
    update = MagicMock(spec=Update)
    update.message = MagicMock(spec=Message)
    update.message.reply_text = AsyncMock()
    update.effective_chat = MagicMock(spec=Chat)
    update.effective_chat.id = 12345
    return update


@pytest.fixture
def mock_context():
    """Create a mock context object."""
    context = MagicMock()
    context.bot = MagicMock()
    context.bot.send_chat_action = AsyncMock()
    return context


@pytest.mark.asyncio
async def test_start_command(mock_update, mock_context):
    """Test /start command handler."""
    await start(mock_update, mock_context)

    mock_update.message.reply_text.assert_called_once()
    call_args = mock_update.message.reply_text.call_args[0][0]
    assert "ExcursoBot" in call_args
    assert "геолокацию" in call_args


@pytest.mark.asyncio
async def test_help_command(mock_update, mock_context):
    """Test /help command handler."""
    await help_command(mock_update, mock_context)

    mock_update.message.reply_text.assert_called_once()
    call_args = mock_update.message.reply_text.call_args[0][0]
    assert "ExcursoBot" in call_args
    assert "/start" in call_args
    assert "/help" in call_args


@pytest.mark.asyncio
async def test_handle_location_success(mock_update, mock_context):
    """Test successful location handling."""
    # Setup location
    location = MagicMock(spec=Location)
    location.latitude = 55.7558
    location.longitude = 37.6173
    mock_update.message.location = location

    # Mock OpenAI client
    with patch("bot.handlers.OpenAIClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.get_location_fact = AsyncMock(
            return_value="Интересный факт о Москве!"
        )

        await handle_location(mock_update, mock_context)

        # Verify typing action was sent
        mock_context.bot.send_chat_action.assert_called_once_with(
            chat_id=12345, action="typing"
        )

        # Verify OpenAI was called with correct coordinates
        mock_client.get_location_fact.assert_called_once_with(55.7558, 37.6173)

        # Verify response was sent
        mock_update.message.reply_text.assert_called_with("Интересный факт о Москве!")


@pytest.mark.asyncio
async def test_handle_location_error(mock_update, mock_context):
    """Test location handling with OpenAI error."""
    # Setup location
    location = MagicMock(spec=Location)
    location.latitude = 55.7558
    location.longitude = 37.6173
    mock_update.message.location = location

    # Mock OpenAI client to raise error
    with patch("bot.handlers.OpenAIClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.get_location_fact = AsyncMock(side_effect=Exception("API Error"))

        await handle_location(mock_update, mock_context)

        # Verify error message was sent
        mock_update.message.reply_text.assert_called()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "ошибка" in call_args


@pytest.mark.asyncio
async def test_handle_location_no_location(mock_update, mock_context):
    """Test handler when no location is provided."""
    mock_update.message.location = None

    await handle_location(mock_update, mock_context)

    # Should not call any other methods
    mock_context.bot.send_chat_action.assert_not_called()
    mock_update.message.reply_text.assert_not_called()


def test_setup_handlers():
    """Test handlers setup."""
    app = MagicMock(spec=Application)
    app.add_handler = MagicMock()

    setup_handlers(app)

    # Verify handlers were added
    assert app.add_handler.call_count == 3

    # Check that different types of handlers were added
    handler_types = [
        call[0][0].__class__.__name__ for call in app.add_handler.call_args_list
    ]
    assert "CommandHandler" in handler_types
    assert "MessageHandler" in handler_types
