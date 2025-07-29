#!/usr/bin/env python3
"""
Test script to verify the Kalakan TTS installation.

This script tests the basic functionality of the Kalakan TTS system
to verify that it's installed correctly.
"""

import os
import sys
import unittest

# Add parent directory to path to allow importing from kalakan
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
import numpy as np

from kalakan.text.twi_g2p import TwiG2P
from kalakan.text.phonemes import TwiPhonemes
from kalakan.models.acoustic.tacotron2 import Tacotron2
from kalakan.models.vocoders.griffin_lim import GriffinLim
from kalakan.synthesis.synthesizer import Synthesizer
from kalakan.utils.device import get_device


class TestInstallation(unittest.TestCase):
    """Test case for verifying the Kalakan TTS installation."""
    
    def test_imports(self):
        """Test that all required modules can be imported."""
        # The imports at the top of the file already test this
        self.assertTrue(True)
    
    def test_device(self):
        """Test that the device can be determined."""
        device = get_device()
        self.assertIsInstance(device, torch.device)
    
    def test_phonemes(self):
        """Test the phoneme system."""
        # Test phoneme set
        self.assertGreater(len(TwiPhonemes.SYMBOLS), 0)
        
        # Test phoneme conversion
        text = "Akwaaba"
        g2p = TwiG2P()
        phonemes = g2p.text_to_phonemes(text)
        self.assertGreater(len(phonemes), 0)
        
        # Test phoneme sequence
        phoneme_sequence = g2p.text_to_phoneme_sequence(text)
        self.assertGreater(len(phoneme_sequence), 0)
    
    def test_models(self):
        """Test model creation."""
        # Test Tacotron2 model
        tacotron2 = Tacotron2()
        self.assertIsInstance(tacotron2, Tacotron2)
        
        # Test Griffin-Lim vocoder
        griffin_lim = GriffinLim()
        self.assertIsInstance(griffin_lim, GriffinLim)
    
    def test_synthesizer(self):
        """Test synthesizer creation."""
        # Test synthesizer
        synthesizer = Synthesizer()
        self.assertIsInstance(synthesizer, Synthesizer)
        
        # Test text processing
        text = "Akwaaba"
        phoneme_sequence = synthesizer.g2p.text_to_phoneme_sequence(text)
        self.assertGreater(len(phoneme_sequence), 0)


if __name__ == "__main__":
    unittest.main()