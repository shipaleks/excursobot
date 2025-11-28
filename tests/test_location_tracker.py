"""
Unit tests for location tracker.
"""

import time
from datetime import datetime, timedelta

import pytest
from scheduler.location_tracker import LocationTracker


def test_location_tracker_first_fact():
    """Test that first fact is always sent."""
    tracker = LocationTracker(interval_minutes=10)

    assert tracker.should_send_fact(chat_id=123, message_id=456) is True


def test_location_tracker_interval_not_reached():
    """Test that fact is not sent if interval hasn't passed."""
    tracker = LocationTracker(interval_minutes=10)

    # First call should return True
    assert tracker.should_send_fact(chat_id=123, message_id=456) is True

    # Second call immediately should return False
    assert tracker.should_send_fact(chat_id=123, message_id=456) is False


def test_location_tracker_interval_reached():
    """Test that fact is sent after interval has passed."""
    tracker = LocationTracker(interval_minutes=0.01)  # 0.6 seconds

    # First call
    assert tracker.should_send_fact(chat_id=123, message_id=456) is True

    # Immediate second call
    assert tracker.should_send_fact(chat_id=123, message_id=456) is False

    # Wait for interval to pass
    time.sleep(1)

    # Should now return True
    assert tracker.should_send_fact(chat_id=123, message_id=456) is True


def test_location_tracker_different_sessions():
    """Test that different chat/message combinations are tracked separately."""
    tracker = LocationTracker(interval_minutes=10)

    # Different sessions should all return True on first call
    assert tracker.should_send_fact(chat_id=123, message_id=456) is True
    assert tracker.should_send_fact(chat_id=123, message_id=789) is True
    assert tracker.should_send_fact(chat_id=456, message_id=123) is True

    # Immediate second calls should return False
    assert tracker.should_send_fact(chat_id=123, message_id=456) is False
    assert tracker.should_send_fact(chat_id=123, message_id=789) is False
    assert tracker.should_send_fact(chat_id=456, message_id=123) is False


def test_location_tracker_session_count():
    """Test session count tracking."""
    tracker = LocationTracker(interval_minutes=10)

    assert tracker.get_session_count() == 0

    tracker.should_send_fact(chat_id=123, message_id=456)
    assert tracker.get_session_count() == 1

    tracker.should_send_fact(chat_id=123, message_id=789)
    assert tracker.get_session_count() == 2

    tracker.should_send_fact(chat_id=123, message_id=456)  # Same session
    assert tracker.get_session_count() == 2


def test_location_tracker_cleanup():
    """Test cleanup of old sessions."""
    tracker = LocationTracker(interval_minutes=10)

    # Add some sessions
    tracker.should_send_fact(chat_id=123, message_id=456)
    tracker.should_send_fact(chat_id=789, message_id=101)

    assert tracker.get_session_count() == 2

    # Manually set one session to be old
    key = (123, 456)
    tracker._last_fact_time[key] = datetime.now() - timedelta(hours=3)

    # Cleanup old sessions (older than 2 hours)
    tracker.cleanup_old_sessions(max_age_hours=2)

    # Old session should be removed
    assert tracker.get_session_count() == 1
