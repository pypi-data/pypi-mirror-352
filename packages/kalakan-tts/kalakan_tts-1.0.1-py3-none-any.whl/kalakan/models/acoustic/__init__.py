"""
Acoustic models for Kalakan TTS.

This package contains the acoustic models (text-to-mel) used in Kalakan TTS,
including Tacotron2, FastSpeech2, and Transformer-TTS.
"""

from kalakan.models.acoustic.base_acoustic import BaseAcousticModel
from kalakan.models.acoustic.tacotron2 import Tacotron2
from kalakan.models.acoustic.fastspeech2 import FastSpeech2
from kalakan.models.acoustic.transformer_tts import TransformerTTS

__all__ = [
    "BaseAcousticModel",
    "Tacotron2",
    "FastSpeech2",
    "TransformerTTS",
]