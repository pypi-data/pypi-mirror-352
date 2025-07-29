"""
API for Kalakan TTS.

This package provides API functionality for Kalakan TTS,
including REST, gRPC, and WebSocket interfaces.
"""

from kalakan.api.server import create_app

__all__ = [
    "create_app",
]