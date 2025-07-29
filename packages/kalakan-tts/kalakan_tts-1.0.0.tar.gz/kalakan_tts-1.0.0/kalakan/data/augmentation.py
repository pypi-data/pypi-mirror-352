"""
Data augmentation for Kalakan TTS.

This module provides data augmentation techniques for TTS training,
including audio and text augmentation.
"""

import random
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchaudio
import torchaudio.transforms as T


class AudioAugmentation:
    """
    Audio augmentation for TTS training.
    
    This class provides various audio augmentation techniques for
    improving the robustness of TTS models.
    """
    
    def __init__(
        self,
        sample_rate: int = 22050,
        pitch_shift_range: Tuple[float, float] = (-2.0, 2.0),
        time_stretch_range: Tuple[float, float] = (0.9, 1.1),
        noise_level_range: Tuple[float, float] = (0.0, 0.005),
        reverb_prob: float = 0.3,
        reverb_room_size_range: Tuple[float, float] = (0.1, 0.7),
        reverb_damping_range: Tuple[float, float] = (0.1, 0.7),
        reverb_wet_level_range: Tuple[float, float] = (0.1, 0.5),
        reverb_dry_level_range: Tuple[float, float] = (0.5, 0.9),
        eq_prob: float = 0.3,
        eq_gain_range: Tuple[float, float] = (-6.0, 6.0),
        eq_q_range: Tuple[float, float] = (0.5, 2.0),
    ):
        """
        Initialize the audio augmentation.
        
        Args:
            sample_rate: Audio sample rate.
            pitch_shift_range: Range of pitch shift in semitones.
            time_stretch_range: Range of time stretch factor.
            noise_level_range: Range of noise level to add.
            reverb_prob: Probability of applying reverb.
            reverb_room_size_range: Range of room size for reverb.
            reverb_damping_range: Range of damping for reverb.
            reverb_wet_level_range: Range of wet level for reverb.
            reverb_dry_level_range: Range of dry level for reverb.
            eq_prob: Probability of applying EQ.
            eq_gain_range: Range of gain for EQ in dB.
            eq_q_range: Range of Q factor for EQ.
        """
        self.sample_rate = sample_rate
        self.pitch_shift_range = pitch_shift_range
        self.time_stretch_range = time_stretch_range
        self.noise_level_range = noise_level_range
        self.reverb_prob = reverb_prob
        self.reverb_room_size_range = reverb_room_size_range
        self.reverb_damping_range = reverb_damping_range
        self.reverb_wet_level_range = reverb_wet_level_range
        self.reverb_dry_level_range = reverb_dry_level_range
        self.eq_prob = eq_prob
        self.eq_gain_range = eq_gain_range
        self.eq_q_range = eq_q_range
    
    def __call__(
        self,
        audio: torch.Tensor,
        mel: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        """
        Apply audio augmentation.
        
        Args:
            audio: Audio waveform [batch_size, samples] or [samples].
            mel: Mel spectrogram [batch_size, n_mels, time] or [n_mels, time].
                If provided, it will be recomputed from the augmented audio.
                
        Returns:
            Tuple containing:
                - Augmented audio waveform.
                - Augmented mel spectrogram (if mel is provided).
        """
        # Check if audio is batched
        is_batched = audio.dim() == 2
        if not is_batched:
            audio = audio.unsqueeze(0)
        
        # Check if mel is batched
        mel_is_batched = mel is not None and mel.dim() == 3
        if mel is not None and not mel_is_batched:
            mel = mel.unsqueeze(0)
        
        # Apply augmentations
        for i in range(audio.size(0)):
            # Get current audio
            audio_i = audio[i]
            
            # Apply pitch shift
            if random.random() < 0.5:
                pitch_shift = random.uniform(*self.pitch_shift_range)
                audio_i = self._pitch_shift(audio_i, pitch_shift)
            
            # Apply time stretch
            if random.random() < 0.5:
                time_stretch = random.uniform(*self.time_stretch_range)
                audio_i = self._time_stretch(audio_i, time_stretch)
            
            # Apply noise
            if random.random() < 0.5:
                noise_level = random.uniform(*self.noise_level_range)
                audio_i = self._add_noise(audio_i, noise_level)
            
            # Apply reverb
            if random.random() < self.reverb_prob:
                room_size = random.uniform(*self.reverb_room_size_range)
                damping = random.uniform(*self.reverb_damping_range)
                wet_level = random.uniform(*self.reverb_wet_level_range)
                dry_level = random.uniform(*self.reverb_dry_level_range)
                audio_i = self._add_reverb(audio_i, room_size, damping, wet_level, dry_level)
            
            # Apply EQ
            if random.random() < self.eq_prob:
                center_freq = random.uniform(100, self.sample_rate // 2)
                gain = random.uniform(*self.eq_gain_range)
                q = random.uniform(*self.eq_q_range)
                audio_i = self._apply_eq(audio_i, center_freq, gain, q)
            
            # Update audio
            audio[i] = audio_i
        
        # Recompute mel spectrogram if provided
        if mel is not None:
            # Create mel spectrogram transform
            mel_transform = T.MelSpectrogram(
                sample_rate=self.sample_rate,
                n_fft=1024,
                win_length=1024,
                hop_length=256,
                f_min=0.0,
                f_max=self.sample_rate / 2,
                n_mels=mel.size(1),
                power=1.0,
                normalized=True,
            ).to(audio.device)
            
            # Compute mel spectrogram
            mel = mel_transform(audio)
            
            # Convert to log scale
            mel = torch.log(torch.clamp(mel, min=1e-5))
        
        # Unbatch if needed
        if not is_batched:
            audio = audio.squeeze(0)
        
        if mel is not None and not mel_is_batched:
            mel = mel.squeeze(0)
        
        return audio, mel
    
    def _pitch_shift(self, audio: torch.Tensor, pitch_shift: float) -> torch.Tensor:
        """
        Apply pitch shift to audio.
        
        Args:
            audio: Audio waveform [samples].
            pitch_shift: Pitch shift in semitones.
                
        Returns:
            Pitch-shifted audio waveform [samples].
        """
        # Convert to numpy
        audio_np = audio.cpu().numpy()
        
        # Apply pitch shift
        audio_np = torchaudio.functional.pitch_shift(
            torch.from_numpy(audio_np),
            self.sample_rate,
            pitch_shift,
        ).numpy()
        
        # Convert back to tensor
        audio = torch.from_numpy(audio_np).to(audio.device)
        
        return audio
    
    def _time_stretch(self, audio: torch.Tensor, time_stretch: float) -> torch.Tensor:
        """
        Apply time stretch to audio.
        
        Args:
            audio: Audio waveform [samples].
            time_stretch: Time stretch factor.
                
        Returns:
            Time-stretched audio waveform [samples].
        """
        # Convert to numpy
        audio_np = audio.cpu().numpy()
        
        # Apply time stretch
        audio_np = torchaudio.functional.time_stretch(
            torch.from_numpy(audio_np),
            time_stretch,
        ).numpy()
        
        # Convert back to tensor
        audio = torch.from_numpy(audio_np).to(audio.device)
        
        return audio
    
    def _add_noise(self, audio: torch.Tensor, noise_level: float) -> torch.Tensor:
        """
        Add noise to audio.
        
        Args:
            audio: Audio waveform [samples].
            noise_level: Noise level.
                
        Returns:
            Noisy audio waveform [samples].
        """
        # Generate noise
        noise = torch.randn_like(audio) * noise_level
        
        # Add noise
        audio = audio + noise
        
        # Clip to [-1, 1]
        audio = torch.clamp(audio, -1.0, 1.0)
        
        return audio
    
    def _add_reverb(
        self,
        audio: torch.Tensor,
        room_size: float,
        damping: float,
        wet_level: float,
        dry_level: float,
    ) -> torch.Tensor:
        """
        Add reverb to audio.
        
        Args:
            audio: Audio waveform [samples].
            room_size: Room size (0.0 to 1.0).
            damping: Damping (0.0 to 1.0).
            wet_level: Wet level (0.0 to 1.0).
            dry_level: Dry level (0.0 to 1.0).
                
        Returns:
            Reverbed audio waveform [samples].
        """
        # Simple convolution-based reverb
        # Create impulse response
        ir_length = int(self.sample_rate * room_size)
        ir = torch.zeros(ir_length, device=audio.device)
        
        # Add initial impulse
        ir[0] = 1.0
        
        # Add reflections
        for i in range(1, ir_length):
            ir[i] = ir[i-1] * (1.0 - damping)
        
        # Normalize
        ir = ir / ir.sum()
        
        # Apply convolution
        reverb = F.conv1d(
            audio.view(1, 1, -1),
            ir.view(1, 1, -1),
            padding=ir_length-1,
        ).view(-1)
        
        # Mix dry and wet signals
        audio = dry_level * audio + wet_level * reverb[:audio.size(0)]
        
        # Normalize
        audio = audio / torch.max(torch.abs(audio))
        
        return audio
    
    def _apply_eq(
        self,
        audio: torch.Tensor,
        center_freq: float,
        gain: float,
        q: float,
    ) -> torch.Tensor:
        """
        Apply EQ to audio.
        
        Args:
            audio: Audio waveform [samples].
            center_freq: Center frequency in Hz.
            gain: Gain in dB.
            q: Q factor.
                
        Returns:
            EQ'd audio waveform [samples].
        """
        # Convert to numpy
        audio_np = audio.cpu().numpy()
        
        # Apply EQ
        audio_np = torchaudio.functional.equalizer_biquad(
            torch.from_numpy(audio_np),
            self.sample_rate,
            center_freq,
            gain,
            q,
        ).numpy()
        
        # Convert back to tensor
        audio = torch.from_numpy(audio_np).to(audio.device)
        
        return audio


class TextAugmentation:
    """
    Text augmentation for TTS training.
    
    This class provides various text augmentation techniques for
    improving the robustness of TTS models.
    """
    
    def __init__(
        self,
        word_dropout_prob: float = 0.1,
        word_replacement_prob: float = 0.1,
        word_swap_prob: float = 0.1,
        word_dict: Optional[Dict[str, List[str]]] = None,
    ):
        """
        Initialize the text augmentation.
        
        Args:
            word_dropout_prob: Probability of dropping a word.
            word_replacement_prob: Probability of replacing a word.
            word_swap_prob: Probability of swapping adjacent words.
            word_dict: Dictionary of word replacements.
        """
        self.word_dropout_prob = word_dropout_prob
        self.word_replacement_prob = word_replacement_prob
        self.word_swap_prob = word_swap_prob
        self.word_dict = word_dict or {}
    
    def __call__(self, text: str) -> str:
        """
        Apply text augmentation.
        
        Args:
            text: Input text.
                
        Returns:
            Augmented text.
        """
        # Split text into words
        words = text.split()
        
        # Apply word dropout
        if random.random() < self.word_dropout_prob and len(words) > 1:
            idx = random.randint(0, len(words) - 1)
            words.pop(idx)
        
        # Apply word replacement
        if random.random() < self.word_replacement_prob and len(words) > 0:
            idx = random.randint(0, len(words) - 1)
            word = words[idx]
            
            if word in self.word_dict and self.word_dict[word]:
                words[idx] = random.choice(self.word_dict[word])
        
        # Apply word swap
        if random.random() < self.word_swap_prob and len(words) > 1:
            idx = random.randint(0, len(words) - 2)
            words[idx], words[idx + 1] = words[idx + 1], words[idx]
        
        # Join words
        text = ' '.join(words)
        
        return text