"""
Tests for Kalakan TTS models.

This module contains tests for the Kalakan TTS models.
"""

import os
import unittest
from unittest.mock import MagicMock, patch

import torch

from kalakan.models.acoustic import Tacotron2, FastSpeech2, TransformerTTS
from kalakan.models.vocoders import GriffinLim, HiFiGAN, MelGAN, WaveGlow


class TestAcousticModels(unittest.TestCase):
    """Tests for acoustic models."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock phoneme dictionary
        self.phoneme_dict = {
            "a": 0,
            "b": 1,
            "c": 2,
            "pad": 3,
        }
        
        # Create mock inputs
        self.batch_size = 2
        self.max_phoneme_length = 10
        self.n_mels = 80
        self.max_mel_length = 50
        
        # Create phoneme inputs
        self.phonemes = torch.randint(
            0, 4, (self.batch_size, self.max_phoneme_length)
        )
        self.phoneme_lengths = torch.tensor([8, 6], dtype=torch.long)
        
        # Create mel inputs
        self.mels = torch.randn(
            self.batch_size, self.n_mels, self.max_mel_length
        )
        self.mel_lengths = torch.tensor([40, 30], dtype=torch.long)
    
    def test_tacotron2_forward(self):
        """Test Tacotron2 forward pass."""
        # Create model
        model = Tacotron2(
            n_phonemes=4,
            phoneme_dict=self.phoneme_dict,
            n_mels=self.n_mels,
        )
        
        # Set model to evaluation mode
        model.eval()
        
        # Forward pass
        with torch.no_grad():
            mel_outputs, outputs = model(
                phonemes=self.phonemes,
                phoneme_lengths=self.phoneme_lengths,
                mels=self.mels,
                mel_lengths=self.mel_lengths,
            )
        
        # Check outputs
        self.assertEqual(mel_outputs.shape[0], self.batch_size)
        self.assertEqual(mel_outputs.shape[1], self.n_mels)
        self.assertGreaterEqual(mel_outputs.shape[2], self.max_mel_length)
        
        # Check additional outputs
        self.assertIn("alignments", outputs)
        self.assertIn("gate_outputs", outputs)
    
    def test_fastspeech2_forward(self):
        """Test FastSpeech2 forward pass."""
        # Create model
        model = FastSpeech2(
            n_phonemes=4,
            phoneme_dict=self.phoneme_dict,
            n_mels=self.n_mels,
        )
        
        # Set model to evaluation mode
        model.eval()
        
        # Forward pass
        with torch.no_grad():
            mel_outputs, outputs = model(
                phonemes=self.phonemes,
                phoneme_lengths=self.phoneme_lengths,
            )
        
        # Check outputs
        self.assertEqual(mel_outputs.shape[0], self.batch_size)
        self.assertEqual(mel_outputs.shape[1], self.n_mels)
        
        # Check additional outputs
        self.assertIn("duration_predictions", outputs)
        self.assertIn("pitch_predictions", outputs)
        self.assertIn("energy_predictions", outputs)
    
    def test_transformer_tts_forward(self):
        """Test TransformerTTS forward pass."""
        # Create model
        model = TransformerTTS(
            n_phonemes=4,
            phoneme_dict=self.phoneme_dict,
            n_mels=self.n_mels,
        )
        
        # Set model to evaluation mode
        model.eval()
        
        # Forward pass
        with torch.no_grad():
            mel_outputs, outputs = model(
                phonemes=self.phonemes,
                phoneme_lengths=self.phoneme_lengths,
                mels=self.mels,
                mel_lengths=self.mel_lengths,
            )
        
        # Check outputs
        self.assertEqual(mel_outputs.shape[0], self.batch_size)
        self.assertEqual(mel_outputs.shape[1], self.n_mels)
        
        # Check additional outputs
        self.assertIn("attention_weights", outputs)
        self.assertIn("stop_outputs", outputs)


class TestVocoders(unittest.TestCase):
    """Tests for vocoders."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock inputs
        self.batch_size = 2
        self.n_mels = 80
        self.mel_length = 50
        
        # Create mel inputs
        self.mels = torch.randn(
            self.batch_size, self.n_mels, self.mel_length
        )
    
    def test_griffin_lim_forward(self):
        """Test GriffinLim forward pass."""
        # Create model
        model = GriffinLim(
            n_mels=self.n_mels,
            sample_rate=22050,
            hop_length=256,
        )
        
        # Set model to evaluation mode
        model.eval()
        
        # Forward pass
        with torch.no_grad():
            audio = model(self.mels)
        
        # Check outputs
        self.assertEqual(audio.shape[0], self.batch_size)
        self.assertEqual(audio.shape[1], self.mel_length * model.hop_length)
    
    def test_hifigan_forward(self):
        """Test HiFiGAN forward pass."""
        # Create model
        model = HiFiGAN(
            n_mels=self.n_mels,
            sample_rate=22050,
            hop_length=256,
        )
        
        # Set model to evaluation mode
        model.eval()
        
        # Forward pass
        with torch.no_grad():
            audio = model(self.mels)
        
        # Check outputs
        self.assertEqual(audio.shape[0], self.batch_size)
        self.assertEqual(audio.shape[1], 1)
        self.assertEqual(audio.shape[2], self.mel_length * model.hop_length)
    
    def test_melgan_forward(self):
        """Test MelGAN forward pass."""
        # Create model
        model = MelGAN(
            n_mels=self.n_mels,
            sample_rate=22050,
            hop_length=256,
        )
        
        # Set model to evaluation mode
        model.eval()
        
        # Forward pass
        with torch.no_grad():
            audio = model(self.mels)
        
        # Check outputs
        self.assertEqual(audio.shape[0], self.batch_size)
        self.assertEqual(audio.shape[1], 1)
        self.assertEqual(audio.shape[2], self.mel_length * model.hop_length)
    
    def test_waveglow_forward(self):
        """Test WaveGlow forward pass."""
        # Create model
        model = WaveGlow(
            n_mels=self.n_mels,
            sample_rate=22050,
            hop_length=256,
        )
        
        # Set model to evaluation mode
        model.eval()
        
        # Forward pass
        with torch.no_grad():
            audio = model._forward_inference(self.mels)
        
        # Check outputs
        self.assertEqual(audio.shape[0], self.batch_size)
        self.assertEqual(audio.shape[1], self.mel_length * model.hop_length)


if __name__ == "__main__":
    unittest.main()