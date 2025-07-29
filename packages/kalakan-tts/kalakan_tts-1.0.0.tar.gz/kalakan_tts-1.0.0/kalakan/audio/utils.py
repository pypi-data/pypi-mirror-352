"""
Audio utilities for TTS.

This module provides utility functions for working with audio in TTS,
including loading, saving, and converting audio files.
"""

import os
from typing import Optional, Tuple, Union

import librosa
import numpy as np
import soundfile as sf
import torch
import torchaudio
from torchaudio.transforms import Resample


def load_audio(
    file_path: str,
    sample_rate: int = 22050,
    mono: bool = True,
    normalize: bool = True,
    return_tensor: bool = True,
    device: Optional[torch.device] = None,
) -> Union[np.ndarray, torch.Tensor]:
    """
    Load an audio file.
    
    Args:
        file_path: Path to the audio file.
        sample_rate: Target sample rate.
        mono: Whether to convert to mono.
        normalize: Whether to normalize the audio to [-1, 1].
        return_tensor: Whether to return a torch tensor or numpy array.
        device: Device to use for computation.
        
    Returns:
        Audio signal as a torch tensor or numpy array.
    """
    # Check if file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")
    
    # Load audio file
    audio, sr = torchaudio.load(file_path)
    
    # Resample if needed
    if sr != sample_rate:
        resampler = Resample(sr, sample_rate)
        audio = resampler(audio)
    
    # Convert to mono if needed
    if mono and audio.shape[0] > 1:
        audio = torch.mean(audio, dim=0, keepdim=True)
    
    # Normalize if requested
    if normalize:
        max_val = torch.max(torch.abs(audio))
        if max_val > 0:
            audio = audio / max_val
    
    # Move to device if specified
    if device is not None:
        audio = audio.to(device)
    
    # Convert to numpy if requested
    if not return_tensor:
        audio = audio.cpu().numpy()
    
    return audio


def save_audio(
    audio: Union[np.ndarray, torch.Tensor],
    file_path: str,
    sample_rate: int = 22050,
    normalize: bool = True,
) -> None:
    """
    Save audio to a file.
    
    Args:
        audio: Audio signal as a numpy array or torch tensor.
        file_path: Path to save the audio file.
        sample_rate: Sample rate of the audio.
        normalize: Whether to normalize the audio to [-1, 1] before saving.
    """
    # Convert to numpy if needed
    if isinstance(audio, torch.Tensor):
        audio = audio.detach().cpu().numpy()
    
    # Ensure audio is 1D
    if audio.ndim > 1:
        audio = audio.squeeze()
    
    # Normalize if requested
    if normalize:
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            audio = audio / max_val
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    
    # Save audio file
    sf.write(file_path, audio, sample_rate)


def convert_audio_format(
    input_file: str,
    output_file: str,
    target_sample_rate: Optional[int] = None,
    target_channels: Optional[int] = None,
) -> None:
    """
    Convert an audio file to a different format.
    
    Args:
        input_file: Path to the input audio file.
        output_file: Path to save the output audio file.
        target_sample_rate: Target sample rate. If None, keep the original.
        target_channels: Target number of channels. If None, keep the original.
    """
    # Load audio file
    audio, sr = torchaudio.load(input_file)
    
    # Resample if needed
    if target_sample_rate is not None and sr != target_sample_rate:
        resampler = Resample(sr, target_sample_rate)
        audio = resampler(audio)
        sr = target_sample_rate
    
    # Convert channels if needed
    if target_channels is not None:
        if target_channels == 1 and audio.shape[0] > 1:
            # Convert to mono
            audio = torch.mean(audio, dim=0, keepdim=True)
        elif target_channels == 2 and audio.shape[0] == 1:
            # Convert to stereo
            audio = audio.repeat(2, 1)
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    
    # Save audio file
    torchaudio.save(output_file, audio, sr)


def get_audio_info(file_path: str) -> dict:
    """
    Get information about an audio file.
    
    Args:
        file_path: Path to the audio file.
        
    Returns:
        Dictionary containing audio information.
    """
    # Check if file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")
    
    # Get audio metadata
    info = torchaudio.info(file_path)
    
    # Load audio to get duration and other properties
    audio, sr = torchaudio.load(file_path)
    duration = audio.shape[1] / sr
    
    return {
        "sample_rate": sr,
        "channels": audio.shape[0],
        "samples": audio.shape[1],
        "duration": duration,
        "format": os.path.splitext(file_path)[1][1:],
        "bits_per_sample": info.bits_per_sample if hasattr(info, 'bits_per_sample') else None,
    }


def audio_to_mel_spectrogram(
    audio: Union[np.ndarray, torch.Tensor],
    sample_rate: int = 22050,
    n_fft: int = 1024,
    hop_length: int = 256,
    n_mels: int = 80,
    f_min: float = 0.0,
    f_max: Optional[float] = None,
    power: float = 2.0,
    normalized: bool = True,
    return_tensor: bool = True,
    device: Optional[torch.device] = None,
) -> Union[np.ndarray, torch.Tensor]:
    """
    Convert audio to mel spectrogram.
    
    Args:
        audio: Audio signal as a numpy array or torch tensor.
        sample_rate: Audio sample rate.
        n_fft: FFT size.
        hop_length: Hop length between frames.
        n_mels: Number of mel bands.
        f_min: Minimum frequency for mel bands.
        f_max: Maximum frequency for mel bands. If None, defaults to sample_rate/2.
        power: Power of the magnitude spectrogram.
        normalized: Whether to normalize the mel spectrogram.
        return_tensor: Whether to return a torch tensor or numpy array.
        device: Device to use for computation.
        
    Returns:
        Mel spectrogram as a torch tensor or numpy array.
    """
    # Set default f_max if not provided
    if f_max is None:
        f_max = sample_rate / 2
    
    # Convert to tensor if needed
    if isinstance(audio, np.ndarray):
        audio = torch.from_numpy(audio).float()
    
    # Move to device if specified
    if device is not None:
        audio = audio.to(device)
    
    # Ensure audio is 1D
    if audio.dim() > 1:
        audio = audio.squeeze(0)
    
    # Create mel spectrogram transform
    mel_transform = torchaudio.transforms.MelSpectrogram(
        sample_rate=sample_rate,
        n_fft=n_fft,
        hop_length=hop_length,
        f_min=f_min,
        f_max=f_max,
        n_mels=n_mels,
        power=power,
    ).to(audio.device)
    
    # Compute mel spectrogram
    mel = mel_transform(audio)
    
    # Convert to log scale
    mel = torch.log(torch.clamp(mel, min=1e-5))
    
    # Normalize if requested
    if normalized:
        mel = (mel - mel.mean()) / (mel.std() + 1e-5)
    
    # Convert to numpy if requested
    if not return_tensor:
        mel = mel.cpu().numpy()
    
    return mel


def mel_spectrogram_to_audio(
    mel_spectrogram: Union[np.ndarray, torch.Tensor],
    sample_rate: int = 22050,
    n_fft: int = 1024,
    hop_length: int = 256,
    power: float = 2.0,
    normalized: bool = True,
    return_tensor: bool = True,
    device: Optional[torch.device] = None,
) -> Union[np.ndarray, torch.Tensor]:
    """
    Convert mel spectrogram to audio using Griffin-Lim algorithm.
    
    Args:
        mel_spectrogram: Mel spectrogram as a numpy array or torch tensor.
        sample_rate: Audio sample rate.
        n_fft: FFT size.
        hop_length: Hop length between frames.
        power: Power of the magnitude spectrogram.
        normalized: Whether the mel spectrogram is normalized.
        return_tensor: Whether to return a torch tensor or numpy array.
        device: Device to use for computation.
        
    Returns:
        Audio signal as a torch tensor or numpy array.
    """
    # Convert to tensor if needed
    if isinstance(mel_spectrogram, np.ndarray):
        mel_spectrogram = torch.from_numpy(mel_spectrogram).float()
    
    # Move to device if specified
    if device is not None:
        mel_spectrogram = mel_spectrogram.to(device)
    
    # Denormalize if needed
    if normalized:
        # This is a simple approximation; in practice, you'd need to store the mean and std
        mel_spectrogram = mel_spectrogram * 8.0
    
    # Convert from log scale
    mel_spectrogram = torch.exp(mel_spectrogram)
    
    # Create inverse mel transform
    inverse_mel_transform = torchaudio.transforms.InverseMelScale(
        n_stft=n_fft // 2 + 1,
        n_mels=mel_spectrogram.shape[0],
        sample_rate=sample_rate,
    ).to(mel_spectrogram.device)
    
    # Convert mel spectrogram to linear spectrogram
    linear_spectrogram = inverse_mel_transform(mel_spectrogram)
    
    # Apply Griffin-Lim algorithm
    griffin_lim = torchaudio.transforms.GriffinLim(
        n_fft=n_fft,
        hop_length=hop_length,
        power=power,
    ).to(mel_spectrogram.device)
    
    # Reconstruct audio
    audio = griffin_lim(linear_spectrogram.unsqueeze(0)).squeeze(0)
    
    # Convert to numpy if requested
    if not return_tensor:
        audio = audio.cpu().numpy()
    
    return audio