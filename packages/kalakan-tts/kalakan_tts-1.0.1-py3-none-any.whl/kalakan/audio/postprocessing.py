"""
Audio postprocessing for TTS.

This module provides functionality for postprocessing audio signals generated
by TTS models, including denoising, dereverberation, and compression.
"""

from typing import Dict, Optional, Tuple, Union

import numpy as np
import torch
import torchaudio
from torchaudio.transforms import Resample


class AudioPostprocessor:
    """
    Audio postprocessor for TTS.
    
    This class provides methods for postprocessing audio signals generated
    by TTS models, including denoising, dereverberation, and compression.
    """
    
    def __init__(
        self,
        sample_rate: int = 22050,
        denoise: bool = False,
        dereverberate: bool = False,
        compress: bool = True,
        compression_threshold: float = 0.8,
        compression_ratio: float = 4.0,
        device: Optional[torch.device] = None,
    ):
        """
        Initialize the audio postprocessor.
        
        Args:
            sample_rate: Audio sample rate in Hz.
            denoise: Whether to apply denoising.
            dereverberate: Whether to apply dereverberation.
            compress: Whether to apply compression.
            compression_threshold: Threshold for compression.
            compression_ratio: Ratio for compression.
            device: Device to use for computation.
        """
        self.sample_rate = sample_rate
        self.denoise = denoise
        self.dereverberate = dereverberate
        self.compress = compress
        self.compression_threshold = compression_threshold
        self.compression_ratio = compression_ratio
        self.device = device if device is not None else torch.device("cpu")
    
    def postprocess(
        self, 
        audio: Union[np.ndarray, torch.Tensor],
        return_tensor: bool = True,
    ) -> Union[np.ndarray, torch.Tensor]:
        """
        Postprocess audio signal.
        
        Args:
            audio: Audio signal as a numpy array or torch tensor.
            return_tensor: Whether to return a torch tensor or numpy array.
            
        Returns:
            Postprocessed audio as a torch tensor or numpy array.
        """
        # Convert to tensor if needed
        is_tensor = isinstance(audio, torch.Tensor)
        if not is_tensor:
            audio = torch.from_numpy(audio).float().to(self.device)
        
        # Apply denoising if requested
        if self.denoise:
            audio = self._denoise(audio)
        
        # Apply dereverberation if requested
        if self.dereverberate:
            audio = self._dereverberate(audio)
        
        # Apply compression if requested
        if self.compress:
            audio = self._compress(audio)
        
        # Convert to numpy if requested
        if not return_tensor:
            audio = audio.cpu().numpy()
        
        return audio
    
    def _denoise(self, audio: torch.Tensor) -> torch.Tensor:
        """
        Apply denoising to the audio.
        
        Args:
            audio: Audio signal as a torch tensor.
            
        Returns:
            Denoised audio as a torch tensor.
        """
        # Simple spectral subtraction denoising
        # In a real implementation, this would use a more sophisticated method
        
        # Convert to frequency domain
        n_fft = 2048
        hop_length = 512
        window = torch.hann_window(n_fft).to(self.device)
        
        # Compute STFT
        stft = torch.stft(
            audio,
            n_fft=n_fft,
            hop_length=hop_length,
            window=window,
            return_complex=True,
        )
        
        # Estimate noise from the first few frames
        noise_frames = 5
        noise_estimate = torch.mean(torch.abs(stft[:, :noise_frames]), dim=1, keepdim=True)
        
        # Apply spectral subtraction
        magnitude = torch.abs(stft)
        phase = torch.angle(stft)
        
        # Subtract noise estimate with a floor
        magnitude = torch.clamp(magnitude - 2 * noise_estimate, min=0.0)
        
        # Reconstruct complex STFT
        stft_denoised = magnitude * torch.exp(1j * phase)
        
        # Convert back to time domain
        audio_denoised = torch.istft(
            stft_denoised,
            n_fft=n_fft,
            hop_length=hop_length,
            window=window,
            length=audio.shape[0],
        )
        
        return audio_denoised
    
    def _dereverberate(self, audio: torch.Tensor) -> torch.Tensor:
        """
        Apply dereverberation to the audio.
        
        Args:
            audio: Audio signal as a torch tensor.
            
        Returns:
            Dereverberated audio as a torch tensor.
        """
        # Simple spectral enhancement dereverberation
        # In a real implementation, this would use a more sophisticated method
        
        # Convert to frequency domain
        n_fft = 2048
        hop_length = 512
        window = torch.hann_window(n_fft).to(self.device)
        
        # Compute STFT
        stft = torch.stft(
            audio,
            n_fft=n_fft,
            hop_length=hop_length,
            window=window,
            return_complex=True,
        )
        
        # Apply spectral enhancement
        magnitude = torch.abs(stft)
        phase = torch.angle(stft)
        
        # Simple spectral enhancement
        magnitude = magnitude ** 0.8
        
        # Reconstruct complex STFT
        stft_enhanced = magnitude * torch.exp(1j * phase)
        
        # Convert back to time domain
        audio_enhanced = torch.istft(
            stft_enhanced,
            n_fft=n_fft,
            hop_length=hop_length,
            window=window,
            length=audio.shape[0],
        )
        
        return audio_enhanced
    
    def _compress(self, audio: torch.Tensor) -> torch.Tensor:
        """
        Apply compression to the audio.
        
        Args:
            audio: Audio signal as a torch tensor.
            
        Returns:
            Compressed audio as a torch tensor.
        """
        # Normalize audio to [-1, 1]
        max_val = torch.max(torch.abs(audio))
        if max_val > 0:
            audio = audio / max_val
        
        # Apply compression
        mask = torch.abs(audio) > self.compression_threshold
        compressed = torch.zeros_like(audio)
        
        # Apply compression only to values above threshold
        compressed[mask] = torch.sign(audio[mask]) * (
            self.compression_threshold + 
            (torch.abs(audio[mask]) - self.compression_threshold) / self.compression_ratio
        )
        
        # Keep values below threshold unchanged
        compressed[~mask] = audio[~mask]
        
        # Normalize to [-1, 1] again
        max_val = torch.max(torch.abs(compressed))
        if max_val > 0:
            compressed = compressed / max_val
        
        return compressed
    
    def get_config(self) -> Dict:
        """
        Get the configuration of the audio postprocessor.
        
        Returns:
            Dictionary containing the configuration.
        """
        return {
            "sample_rate": self.sample_rate,
            "denoise": self.denoise,
            "dereverberate": self.dereverberate,
            "compress": self.compress,
            "compression_threshold": self.compression_threshold,
            "compression_ratio": self.compression_ratio,
        }
    
    @classmethod
    def from_config(cls, config: Dict, device: Optional[torch.device] = None) -> "AudioPostprocessor":
        """
        Create an audio postprocessor from a configuration dictionary.
        
        Args:
            config: Configuration dictionary.
            device: Device to use for computation.
            
        Returns:
            AudioPostprocessor instance.
        """
        return cls(
            sample_rate=config.get("sample_rate", 22050),
            denoise=config.get("denoise", False),
            dereverberate=config.get("dereverberate", False),
            compress=config.get("compress", True),
            compression_threshold=config.get("compression_threshold", 0.8),
            compression_ratio=config.get("compression_ratio", 4.0),
            device=device,
        )