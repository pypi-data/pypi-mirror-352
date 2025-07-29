"""
Vocoders for Kalakan TTS.

This package contains the vocoders (mel-to-audio) used in Kalakan TTS,
including Griffin-Lim, WaveGlow, HiFi-GAN, and MelGAN.
"""

from kalakan.models.vocoders.base_vocoder import BaseVocoder
from kalakan.models.vocoders.griffin_lim import GriffinLim
from kalakan.models.vocoders.waveglow import WaveGlow
from kalakan.models.vocoders.hifigan import HiFiGAN
from kalakan.models.vocoders.melgan import MelGAN

__all__ = [
    "BaseVocoder",
    "GriffinLim",
    "WaveGlow",
    "HiFiGAN",
    "MelGAN",
]