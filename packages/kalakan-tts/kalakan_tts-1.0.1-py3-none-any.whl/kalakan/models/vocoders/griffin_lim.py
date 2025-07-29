"""
Griffin-Lim vocoder for Kalakan TTS.

This module implements the Griffin-Lim algorithm for converting mel spectrograms
to audio waveforms, as described in "Signal estimation from modified short-time
Fourier transform" (Griffin and Lim, 1984).
"""

from typing import Optional

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchaudio

from kalakan.models.vocoders.base_vocoder import BaseVocoder


class GriffinLim(BaseVocoder):
    """
    Griffin-Lim vocoder for Kalakan TTS.
    
    This vocoder converts mel spectrograms to audio waveforms using
    the Griffin-Lim algorithm, which iteratively estimates the phase
    of the signal from its magnitude spectrogram.
    """
    
    def __init__(
        self,
        n_mels: int = 80,
        sample_rate: int = 22050,
        n_fft: int = 1024,
        hop_length: int = 256,
        win_length: Optional[int] = None,
        power: float = 1.0,
        n_iter: int = 60,
        momentum: float = 0.99,
        mel_fmin: float = 0.0,
        mel_fmax: Optional[float] = None,
        normalized: bool = True,
    ):
        """
        Initialize the Griffin-Lim vocoder.
        
        Args:
            n_mels: Number of mel bands in the input mel spectrogram.
            sample_rate: Audio sample rate.
            n_fft: FFT size.
            hop_length: Hop length between frames.
            win_length: Window length. If None, defaults to n_fft.
            power: Power of the magnitude spectrogram.
            n_iter: Number of Griffin-Lim iterations.
            momentum: Momentum for the Griffin-Lim algorithm.
            mel_fmin: Minimum frequency for mel bands.
            mel_fmax: Maximum frequency for mel bands. If None, defaults to sample_rate/2.
            normalized: Whether the input mel spectrogram is normalized.
        """
        super().__init__(n_mels=n_mels, sample_rate=sample_rate, hop_length=hop_length)
        
        # Set model name
        self.model_name = "griffin_lim"
        
        # Set parameters
        self.n_fft = n_fft
        self.win_length = win_length if win_length is not None else n_fft
        self.power = power
        self.n_iter = n_iter
        self.momentum = momentum
        self.mel_fmin = mel_fmin
        self.mel_fmax = mel_fmax if mel_fmax is not None else sample_rate / 2
        self.normalized = normalized
        
        # Create inverse mel transform
        self.inverse_mel_transform = torchaudio.transforms.InverseMelScale(
            n_stft=n_fft // 2 + 1,
            n_mels=n_mels,
            sample_rate=sample_rate,
            f_min=mel_fmin,
            f_max=self.mel_fmax,
        )
        
        # Create Griffin-Lim transform
        self.griffin_lim = torchaudio.transforms.GriffinLim(
            n_fft=n_fft,
            win_length=self.win_length,
            hop_length=hop_length,
            power=power,
            n_iter=n_iter,
            momentum=momentum,
        )
    
    def forward(self, mels: torch.Tensor) -> torch.Tensor:
        """
        Forward pass of the Griffin-Lim vocoder.
        
        Args:
            mels: Mel spectrograms [batch_size, n_mels, time].
                
        Returns:
            Generated audio waveforms [batch_size, time*hop_length].
        """
        return self.inference(mels)
    
    def inference(self, mels: torch.Tensor) -> torch.Tensor:
        """
        Generate audio from mel spectrograms using Griffin-Lim.
        
        Args:
            mels: Mel spectrograms [batch_size, n_mels, time].
                
        Returns:
            Generated audio waveforms [batch_size, time*hop_length].
        """
        # Move transforms to the same device as the input
        device = mels.device
        self.inverse_mel_transform = self.inverse_mel_transform.to(device)
        self.griffin_lim = self.griffin_lim.to(device)
        
        # Process each item in the batch
        batch_size = mels.size(0)
        audio = []
        
        for i in range(batch_size):
            # Get mel spectrogram for current item
            mel = mels[i]
            
            # Denormalize if needed
            if self.normalized:
                # This is a simple approximation; in practice, you'd need to store the mean and std
                mel = mel * 8.0
            
            # Convert from log scale if needed
            if torch.min(mel) < 0:
                mel = torch.exp(mel)
            
            # Convert mel spectrogram to linear spectrogram
            linear_spec = self.inverse_mel_transform(mel)
            
            # Apply Griffin-Lim algorithm
            audio_i = self.griffin_lim(linear_spec)
            
            # Add to batch
            audio.append(audio_i)
        
        # Stack audio waveforms
        audio = torch.stack(audio)
        
        return audio