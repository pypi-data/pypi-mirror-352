"""
Utility functions for Kalakan TTS.

This package contains utility functions for Kalakan TTS,
including configuration management, logging, and device management.
"""

from kalakan.utils.config import Config
from kalakan.utils.device import get_device
from kalakan.utils.logging import setup_logger

__all__ = [
    "Config",
    "get_device",
    "setup_logger",
]