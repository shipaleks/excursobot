"""
Location tracker for managing live location updates and fact delivery timing.
"""

import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class LocationTracker:
    """Tracks live location sessions and manages fact delivery timing."""

    def __init__(self, interval_minutes: int = 10):
        """
        Initialize location tracker.

        Args:
            interval_minutes: Interval in minutes between fact deliveries
        """
        self.interval_minutes = interval_minutes
        # Store last fact time for each chat_id + message_id combination
        self._last_fact_time: dict[tuple[int, int], datetime] = {}

    def should_send_fact(self, chat_id: int, message_id: int) -> bool:
        """
        Check if enough time has passed to send a new fact.

        Args:
            chat_id: Telegram chat ID
            message_id: Telegram message ID

        Returns:
            True if a fact should be sent, False otherwise
        """
        key = (chat_id, message_id)
        now = datetime.now()

        # If this is the first time seeing this location, send fact
        if key not in self._last_fact_time:
            self._last_fact_time[key] = now
            logger.info(
                f"First fact for chat {chat_id}, message {message_id}"
            )
            return True

        # Check if enough time has passed
        last_time = self._last_fact_time[key]
        time_passed = now - last_time
        interval = timedelta(minutes=self.interval_minutes)

        if time_passed >= interval:
            self._last_fact_time[key] = now
            logger.info(
                f"Sending fact for chat {chat_id}, message {message_id} "
                f"({time_passed.total_seconds() / 60:.1f} minutes since last)"
            )
            return True

        logger.debug(
            f"Skipping fact for chat {chat_id}, message {message_id} "
            f"({time_passed.total_seconds() / 60:.1f} / {self.interval_minutes} minutes)"
        )
        return False

    def cleanup_old_sessions(self, max_age_hours: int = 2) -> None:
        """
        Remove tracking data for old sessions.

        Args:
            max_age_hours: Maximum age in hours to keep session data
        """
        now = datetime.now()
        cutoff = now - timedelta(hours=max_age_hours)

        keys_to_remove = [
            key for key, last_time in self._last_fact_time.items()
            if last_time < cutoff
        ]

        for key in keys_to_remove:
            del self._last_fact_time[key]
            logger.info(f"Cleaned up old session: chat {key[0]}, message {key[1]}")

    def get_session_count(self) -> int:
        """Get the number of active tracked sessions."""
        return len(self._last_fact_time)

    def end_session(self, chat_id: int, message_id: int) -> None:
        """
        End a live location session.

        Args:
            chat_id: Telegram chat ID
            message_id: Telegram message ID
        """
        key = (chat_id, message_id)
        if key in self._last_fact_time:
            del self._last_fact_time[key]
            logger.info(f"Ended session for chat {chat_id}, message {message_id}")
