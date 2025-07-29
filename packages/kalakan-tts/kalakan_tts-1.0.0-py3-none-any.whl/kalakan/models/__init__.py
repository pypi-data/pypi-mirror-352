"""
Neural network architectures for Kalakan TTS.

This package contains the neural network architectures used in Kalakan TTS,
including acoustic models (text-to-mel) and vocoders (mel-to-audio).
"""

from kalakan.models.acoustic import Tacotron2, FastSpeech2, TransformerTTS
from kalakan.models.vocoders import GriffinLim, HiFiGAN, MelGAN, WaveGlow

__all__ = [
    # Acoustic models
    "Tacotron2",
    "FastSpeech2",
    "TransformerTTS",
    
    # Vocoders
    "GriffinLim",
    "HiFiGAN",
    "MelGAN",
    "WaveGlow",
]