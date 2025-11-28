"""
User settings manager for bot preferences.
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


class UserSettings:
    """Manages user-specific settings like reasoning effort level."""

    # Valid reasoning effort levels for GPT-5.1
    VALID_LEVELS = {"none", "minimal", "low", "medium", "high"}
    DEFAULT_LEVEL = "medium"

    def __init__(self):
        """Initialize user settings storage."""
        # Store settings per user_id
        self._settings: Dict[int, Dict[str, str]] = {}

    def get_reasoning_effort(self, user_id: int) -> str:
        """
        Get reasoning effort level for a user.

        Args:
            user_id: Telegram user ID

        Returns:
            Reasoning effort level ('none', 'minimal', 'low', 'medium', 'high')
        """
        if user_id not in self._settings:
            return self.DEFAULT_LEVEL

        return self._settings[user_id].get("reasoning_effort", self.DEFAULT_LEVEL)

    def set_reasoning_effort(self, user_id: int, level: str) -> bool:
        """
        Set reasoning effort level for a user.

        Args:
            user_id: Telegram user ID
            level: Reasoning effort level

        Returns:
            True if successful, False if invalid level
        """
        if level not in self.VALID_LEVELS:
            logger.warning(f"Invalid reasoning level: {level}")
            return False

        if user_id not in self._settings:
            self._settings[user_id] = {}

        self._settings[user_id]["reasoning_effort"] = level
        logger.info(f"Set reasoning_effort={level} for user {user_id}")
        return True

    def get_level_description(self, level: str) -> str:
        """
        Get human-readable description for a reasoning level.

        Args:
            level: Reasoning effort level

        Returns:
            Description in Russian
        """
        descriptions = {
            "none": "Без рассуждений - максимальная скорость",
            "minimal": "Минимальные рассуждения - быстрый ответ",
            "low": "Низкий уровень - для простых задач",
            "medium": "Средний уровень - баланс скорости и качества",
            "high": "Высокий уровень - максимальное качество",
        }
        return descriptions.get(level, "Неизвестный уровень")


# Global settings instance
user_settings = UserSettings()
