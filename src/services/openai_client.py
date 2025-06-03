"""
OpenAI client wrapper for generating location-based facts.
"""

import logging
import os

import openai

logger = logging.getLogger(__name__)


class OpenAIClient:
    """OpenAI client for generating interesting facts about locations."""

    def __init__(self) -> None:
        """Initialize OpenAI client."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")

        self.client = openai.AsyncOpenAI(api_key=api_key)

    async def get_location_fact(self, latitude: float, longitude: float) -> str:
        """
        Get an interesting fact about a location using GPT-4.1-mini.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate

        Returns:
            Interesting fact about the location (≤280 characters)
        """
        prompt = (
            f"Given coordinates {latitude}, {longitude}, return one surprising "
            f"fact about any landmark, historical event, or interesting place "
            f"within 1 km radius. Keep it under 280 characters and write in Russian. "
            f"Make it engaging and surprising for travelers."
        )

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4.1-mini",  # Using gpt-4.1-mini as requested
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert travel guide who knows fascinating "
                            "facts about places around the world. Always respond "
                            "in Russian with engaging, surprising facts."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.8,
                max_tokens=120,
                timeout=30.0,
            )

            if not response.choices:
                logger.error("No response from OpenAI")
                return self._get_fallback_message()

            fact = response.choices[0].message.content
            if not fact:
                logger.error("Empty response from OpenAI")
                return self._get_fallback_message()

            # Ensure fact is within character limit
            if len(fact) > 280:
                fact = fact[:277] + "..."

            logger.info(f"Generated fact for {latitude}, {longitude}: {fact[:50]}...")
            return fact

        except openai.APITimeoutError:
            logger.error("OpenAI API timeout")
            return "⏱️ Извините, запрос занял слишком много времени. Попробуйте еще раз."

        except openai.RateLimitError:
            logger.error("OpenAI API rate limit exceeded")
            return "🚦 Превышен лимит запросов. Попробуйте через несколько минут."

        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            return self._get_fallback_message()

        except Exception as e:
            logger.error(f"Unexpected error in OpenAI client: {e}")
            return self._get_fallback_message()

    def _get_fallback_message(self) -> str:
        """Get fallback message when OpenAI fails."""
        return (
            "🗺️ Интересное место! К сожалению, сейчас не могу рассказать "
            "удивительный факт, но попробуйте еще раз - каждая точка "
            "на карте хранит свои секреты!"
        )
