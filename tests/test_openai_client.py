"""
Unit tests for OpenAI client.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import openai
import pytest
from services.openai_client import OpenAIClient


@pytest.fixture
def mock_openai_response():
    """Create a mock OpenAI response."""
    response = MagicMock()
    choice = MagicMock()
    choice.message.content = "Удивительный факт о данном месте!"
    response.choices = [choice]
    return response


@pytest.mark.asyncio
async def test_openai_client_init_success():
    """Test successful OpenAI client initialization."""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        client = OpenAIClient()
        assert client.client is not None


def test_openai_client_init_no_api_key():
    """Test OpenAI client initialization without API key."""
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(
            ValueError, match="OPENAI_API_KEY environment variable is not set"
        ):
            OpenAIClient()


@pytest.mark.asyncio
async def test_get_location_fact_success(mock_openai_response):
    """Test successful location fact generation."""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        client = OpenAIClient()

        # Mock the OpenAI async client
        with patch.object(client.client, "chat") as mock_chat:
            mock_chat.completions.create = AsyncMock(return_value=mock_openai_response)

            result = await client.get_location_fact(55.7558, 37.6173)

            assert result == "Удивительный факт о данном месте!"

            # Verify the API call was made with correct parameters
            mock_chat.completions.create.assert_called_once()
            call_kwargs = mock_chat.completions.create.call_args.kwargs

            assert call_kwargs["model"] == "gpt-4o-mini"
            assert call_kwargs["temperature"] == 0.8
            assert call_kwargs["max_tokens"] == 120
            assert call_kwargs["timeout"] == 30.0
            assert len(call_kwargs["messages"]) == 2
            assert "55.7558" in call_kwargs["messages"][1]["content"]
            assert "37.6173" in call_kwargs["messages"][1]["content"]


@pytest.mark.asyncio
async def test_get_location_fact_long_response():
    """Test location fact with response longer than 280 characters."""
    long_response = "A" * 300  # 300 characters

    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        client = OpenAIClient()

        mock_response = MagicMock()
        choice = MagicMock()
        choice.message.content = long_response
        mock_response.choices = [choice]

        with patch.object(client.client, "chat") as mock_chat:
            mock_chat.completions.create = AsyncMock(return_value=mock_response)

            result = await client.get_location_fact(55.7558, 37.6173)

            assert len(result) <= 280
            assert result.endswith("...")


@pytest.mark.asyncio
async def test_get_location_fact_timeout_error():
    """Test handling of timeout error."""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        client = OpenAIClient()

        with patch.object(client.client, "chat") as mock_chat:
            mock_chat.completions.create = AsyncMock(
                side_effect=openai.APITimeoutError("Timeout")
            )

            result = await client.get_location_fact(55.7558, 37.6173)

            assert "слишком много времени" in result


@pytest.mark.asyncio
async def test_get_location_fact_rate_limit_error():
    """Test handling of rate limit error."""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        client = OpenAIClient()

        with patch.object(client.client, "chat") as mock_chat:
            # Create a proper mock response with request
            mock_request = MagicMock()
            mock_response = MagicMock()
            mock_response.request = mock_request

            mock_chat.completions.create = AsyncMock(
                side_effect=openai.RateLimitError(
                    "Rate limit exceeded", response=mock_response, body=None
                )
            )

            result = await client.get_location_fact(55.7558, 37.6173)

            assert "лимит запросов" in result


@pytest.mark.asyncio
async def test_get_location_fact_api_error():
    """Test handling of general API error."""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        client = OpenAIClient()

        with patch.object(client.client, "chat") as mock_chat:
            # Create a mock request object for the updated API
            mock_request = MagicMock()

            mock_chat.completions.create = AsyncMock(
                side_effect=openai.APIError(
                    "API Error", request=mock_request, body=None
                )
            )

            result = await client.get_location_fact(55.7558, 37.6173)

            assert "Интересное место!" in result  # Fallback message


@pytest.mark.asyncio
async def test_get_location_fact_empty_response():
    """Test handling of empty response from OpenAI."""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        client = OpenAIClient()

        mock_response = MagicMock()
        mock_response.choices = []

        with patch.object(client.client, "chat") as mock_chat:
            mock_chat.completions.create = AsyncMock(return_value=mock_response)

            result = await client.get_location_fact(55.7558, 37.6173)

            assert "Интересное место!" in result  # Fallback message


@pytest.mark.asyncio
async def test_get_location_fact_none_content():
    """Test handling of None content in response."""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        client = OpenAIClient()

        mock_response = MagicMock()
        choice = MagicMock()
        choice.message.content = None
        mock_response.choices = [choice]

        with patch.object(client.client, "chat") as mock_chat:
            mock_chat.completions.create = AsyncMock(return_value=mock_response)

            result = await client.get_location_fact(55.7558, 37.6173)

            assert "Интересное место!" in result  # Fallback message


def test_fallback_message():
    """Test fallback message content."""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        client = OpenAIClient()

        fallback = client._get_fallback_message()

        assert "Интересное место!" in fallback
        assert len(fallback) <= 280  # Should respect character limit
