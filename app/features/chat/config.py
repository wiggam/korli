"""Configuration settings for chat feature"""

from typing import Final

# Summary Configuration
MESSAGES_BEFORE_SUMMARY: Final[int] = 30
"""Trigger summarization when message count exceeds this threshold"""

MESSAGES_TO_KEEP: Final[int] = 20
"""Number of recent messages to keep after summarization"""


