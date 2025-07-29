"""
Mel-spectrogram extraction for audio processing.

This module provides functionality for extracting mel-spectrograms from audio
signals, which are used as input features for acoustic models in TTS.
"""

from typing import Dict, Optional, Tuple, Union

import librosa
import numpy as np
import torch
import torchaudio
from torchaudio.transforms import MelSpectrogram


class MelSpectrogramExtractor:
    """
    Mel-spectrogram feature extractor for audio processing.
    
    This class provides methods for extracting mel-spectrograms from audio
    signals, which are used as input features for acoustic models in TTS.
    """
    
    def __init__(
        self,
        sample_rate: int = 22050,
        n_fft: int = 1024,
        win_length: Optional[int] = None,
        hop_length: int = 256,
        n_mels: int = 80,
        f_min: float = 0.0,
        f_max: Optional[float] = None,
        use_log_mel: bool = True,
        normalize: bool = True,
        center: bool = True,
        pad_mode: str = "reflect",
        power: float = 2.0,
        norm: Optional[str] = "slaney",
        mel_scale: str = "htk",
        device: Optional[torch.device] = None,
    ):
        """
        Initialize the mel-spectrogram extractor.
        
        Args:
            sample_rate: Audio sample rate in Hz.
            n_fft: FFT size.
            win_length: Window size. If None, defaults to n_fft.
            hop_length: Hop length between frames.
            n_mels: Number of mel bands.
            f_min: Minimum frequency for mel bands.
            f_max: Maximum frequency for mel bands. If None, defaults to sample_rate/2.
            use_log_mel: Whether to use log-scale mel spectrograms.
            normalize: Whether to normalize mel spectrograms.
            center: Whether to pad the signal at the beginning and end.
            pad_mode: Padding mode for FFT.
            power: Power of the magnitude spectrogram.
            norm: Normalization mode for mel filterbank.
            mel_scale: Scale for mel filterbank.
            device: Device to use for computation.
        """
        self.sample_rate = sample_rate
        self.n_fft = n_fft
        self.win_length = win_length if win_length is not None else n_fft
        self.hop_length = hop_length
        self.n_mels = n_mels
        self.f_min = f_min
        self.f_max = f_max if f_max is not None else sample_rate / 2
        self.use_log_mel = use_log_mel
        self.normalize = normalize
        self.center = center
        self.pad_mode = pad_mode
        self.power = power
        self.norm = norm
        self.mel_scale = mel_scale
        self.device = device if device is not None else torch.device("cpu")
        
        # Create the mel spectrogram transform
        self.mel_transform = MelSpectrogram(
            sample_rate=sample_rate,
            n_fft=n_fft,
            win_length=self.win_length,
            hop_length=hop_length,
            f_min=f_min,
            f_max=self.f_max,
            n_mels=n_mels,
            center=center,
            pad_mode=pad_mode,
            power=power,
            norm=norm,
            mel_scale=mel_scale,
        ).to(self.device)
    
    def extract(
        self, 
        audio: Union[np.ndarray, torch.Tensor],
        return_tensor: bool = True,
    ) -> Union[np.ndarray, torch.Tensor]:
        """
        Extract mel-spectrogram from audio.
        
        Args:
            audio: Audio signal as a numpy array or torch tensor.
            return_tensor: Whether to return a torch tensor or numpy array.
            
        Returns:
            Mel-spectrogram as a torch tensor or numpy array.
        """
        # Convert to torch tensor if needed
        if isinstance(audio, np.ndarray):
            audio = torch.from_numpy(audio).float().to(self.device)
        
        # Ensure audio is 2D (batch_size, samples)
        if audio.dim() == 1:
            audio = audio.unsqueeze(0)
        
        # Extract mel spectrogram
        mel = self.mel_transform(audio)
        
        # Apply log scaling if requested
        if self.use_log_mel:
            mel = torch.log(torch.clamp(mel, min=1e-5))
        
        # Normalize if requested
        if self.normalize:
            mel = (mel - mel.mean()) / (mel.std() + 1e-5)
        
        # Convert to numpy if requested
        if not return_tensor:
            mel = mel.cpu().numpy()
        
        return mel
    
    def extract_from_file(
        self, 
        file_path: str,
        return_tensor: bool = True,
    ) -> Union[np.ndarray, torch.Tensor]:
        """
        Extract mel-spectrogram from an audio file.
        
        Args:
            file_path: Path to the audio file.
            return_tensor: Whether to return a torch tensor or numpy array.
            
        Returns:
            Mel-spectrogram as a torch tensor or numpy array.
        """
        # Load audio file
        audio, sr = torchaudio.load(file_path)
        
        # Resample if needed
        if sr != self.sample_rate:
            resampler = torchaudio.transforms.Resample(sr, self.sample_rate)
            audio = resampler(audio)
        
        # Convert to mono if needed
        if audio.shape[0] > 1:
            audio = torch.mean(audio, dim=0, keepdim=True)
        
        # Extract mel spectrogram
        return self.extract(audio.squeeze(0), return_tensor=return_tensor)
    
    def get_config(self) -> Dict:
        """
        Get the configuration of the mel-spectrogram extractor.
        
        Returns:
            Dictionary containing the configuration.
        """
        return {
            "sample_rate": self.sample_rate,
            "n_fft": self.n_fft,
            "win_length": self.win_length,
            "hop_length": self.hop_length,
            "n_mels": self.n_mels,
            "f_min": self.f_min,
            "f_max": self.f_max,
            "use_log_mel": self.use_log_mel,
            "normalize": self.normalize,
            "center": self.center,
            "pad_mode": self.pad_mode,
            "power": self.power,
            "norm": self.norm,
            "mel_scale": self.mel_scale,
        }
    
    @classmethod
    def from_config(cls, config: Dict, device: Optional[torch.device] = None) -> "MelSpectrogramExtractor":
        """
        Create a mel-spectrogram extractor from a configuration dictionary.
        
        Args:
            config: Configuration dictionary.
            device: Device to use for computation.
            
        Returns:
            MelSpectrogramExtractor instance.
        """
        return cls(
            sample_rate=config.get("sample_rate", 22050),
            n_fft=config.get("n_fft", 1024),
            win_length=config.get("win_length", None),
            hop_length=config.get("hop_length", 256),
            n_mels=config.get("n_mels", 80),
            f_min=config.get("f_min", 0.0),
            f_max=config.get("f_max", None),
            use_log_mel=config.get("use_log_mel", True),
            normalize=config.get("normalize", True),
            center=config.get("center", True),
            pad_mode=config.get("pad_mode", "reflect"),
            power=config.get("power", 2.0),
            norm=config.get("norm", "slaney"),
            mel_scale=config.get("mel_scale", "htk"),
            device=device,
        )