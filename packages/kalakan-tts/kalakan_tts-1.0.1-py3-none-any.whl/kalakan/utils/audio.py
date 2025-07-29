"""
Audio processing utilities for Kalakan TTS.

This module provides audio processing functionality for the Kalakan TTS system,
including mel-spectrogram extraction, audio loading, and normalization.
"""

import os
from typing import Dict, Optional, Tuple, Union, List

import librosa
import numpy as np
import torch
import torchaudio
import soundfile as sf
from torchaudio.transforms import MelSpectrogram


class AudioProcessor:
    """
    Audio processor for Kalakan TTS.

    This class provides methods for processing audio files, including
    loading, normalization, and mel-spectrogram extraction.
    """

    def __init__(
        self,
        sample_rate: int = 22050,
        n_fft: int = 1024,
        hop_length: int = 256,
        win_length: Optional[int] = None,
        n_mels: int = 80,
        mel_fmin: float = 0.0,
        mel_fmax: Optional[float] = None,
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
        Initialize the audio processor.

        Args:
            sample_rate: Audio sample rate in Hz.
            n_fft: FFT size.
            hop_length: Hop length between frames.
            win_length: Window size. If None, defaults to n_fft.
            n_mels: Number of mel bands.
            mel_fmin: Minimum frequency for mel bands.
            mel_fmax: Maximum frequency for mel bands. If None, defaults to sample_rate/2.
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
        self.hop_length = hop_length
        self.win_length = win_length if win_length is not None else n_fft
        self.n_mels = n_mels
        self.mel_fmin = mel_fmin
        self.mel_fmax = mel_fmax if mel_fmax is not None else sample_rate / 2
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
            f_min=mel_fmin,
            f_max=self.mel_fmax,
            n_mels=n_mels,
            center=center,
            pad_mode=pad_mode,
            power=power,
            norm=norm,
            mel_scale=mel_scale,
        ).to(self.device)

    def load_audio(
        self,
        file_path: str,
        target_sr: Optional[int] = None,
        mono: bool = True,
        normalize: bool = True,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        return_tensor: bool = True,
    ) -> Union[np.ndarray, torch.Tensor]:
        """
        Load an audio file.

        Args:
            file_path: Path to the audio file.
            target_sr: Target sample rate. If None, uses the processor's sample rate.
            mono: Whether to convert to mono.
            normalize: Whether to normalize the audio.
            start_time: Start time in seconds. If None, starts from the beginning.
            end_time: End time in seconds. If None, ends at the end.
            return_tensor: Whether to return a torch tensor or numpy array.

        Returns:
            Audio signal as a torch tensor or numpy array.
        """
        # Set target sample rate
        if target_sr is None:
            target_sr = self.sample_rate

        # Load audio file
        audio, sr = torchaudio.load(file_path)

        # Convert to mono if needed
        if mono and audio.shape[0] > 1:
            audio = torch.mean(audio, dim=0, keepdim=True)

        # Resample if needed
        if sr != target_sr:
            resampler = torchaudio.transforms.Resample(sr, target_sr)
            audio = resampler(audio)

        # Trim if needed
        if start_time is not None or end_time is not None:
            start_sample = int(start_time * target_sr) if start_time is not None else 0
            end_sample = int(end_time * target_sr) if end_time is not None else audio.shape[1]
            audio = audio[:, start_sample:end_sample]

        # Normalize if needed
        if normalize:
            audio = audio / (torch.max(torch.abs(audio)) + 1e-8)

        # Convert to numpy if needed
        if not return_tensor:
            audio = audio.cpu().numpy()

        return audio

    def save_audio(
        self,
        audio: Union[np.ndarray, torch.Tensor],
        file_path: str,
        sample_rate: Optional[int] = None,
        normalize: bool = False,
    ) -> None:
        """
        Save audio to a file.

        Args:
            audio: Audio signal as a numpy array or torch tensor.
            file_path: Path to save the audio file.
            sample_rate: Sample rate of the audio. If None, uses the processor's sample rate.
            normalize: Whether to normalize the audio before saving.
        """
        # Set sample rate
        if sample_rate is None:
            sample_rate = self.sample_rate

        # Convert to numpy if needed
        if isinstance(audio, torch.Tensor):
            audio = audio.cpu().numpy()

        # Ensure audio is 1D
        if audio.ndim == 2:
            audio = audio.squeeze(0)

        # Normalize if needed
        if normalize:
            audio = audio / (np.max(np.abs(audio)) + 1e-8)

        # Save audio
        sf.write(file_path, audio, sample_rate)

    def extract_mel_spectrogram(
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

    def extract_mel_from_file(
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
        # Load audio
        audio = self.load_audio(
            file_path=file_path,
            target_sr=self.sample_rate,
            mono=True,
            normalize=True,
            return_tensor=True,
        )

        # Extract mel spectrogram
        return self.extract_mel_spectrogram(audio, return_tensor=return_tensor)

    def griffin_lim(
        self,
        magnitudes: Union[np.ndarray, torch.Tensor],
        n_iters: int = 30,
        return_tensor: bool = True,
    ) -> Union[np.ndarray, torch.Tensor]:
        """
        Reconstruct audio from magnitude spectrogram using Griffin-Lim algorithm.

        Args:
            magnitudes: Magnitude spectrogram.
            n_iters: Number of iterations.
            return_tensor: Whether to return a torch tensor or numpy array.

        Returns:
            Reconstructed audio.
        """
        # Convert to numpy if needed
        if isinstance(magnitudes, torch.Tensor):
            magnitudes = magnitudes.cpu().numpy()

        # Ensure magnitudes is 2D (n_fft//2+1, time)
        if magnitudes.ndim == 3:
            magnitudes = magnitudes.squeeze(0)

        # Reconstruct audio
        audio = librosa.griffinlim(
            magnitudes,
            n_iter=n_iters,
            hop_length=self.hop_length,
            win_length=self.win_length,
            window="hann",
            center=self.center,
            momentum=0.99,
        )

        # Convert to tensor if requested
        if return_tensor:
            audio = torch.from_numpy(audio).float()

        return audio

    def mel_to_audio(
        self,
        mel: Union[np.ndarray, torch.Tensor],
        return_tensor: bool = True,
    ) -> Union[np.ndarray, torch.Tensor]:
        """
        Convert mel-spectrogram to audio using Griffin-Lim algorithm.

        Args:
            mel: Mel-spectrogram.
            return_tensor: Whether to return a torch tensor or numpy array.

        Returns:
            Reconstructed audio.
        """
        # Convert to numpy if needed
        if isinstance(mel, torch.Tensor):
            mel = mel.cpu().numpy()

        # Ensure mel is 2D (n_mels, time)
        if mel.ndim == 3:
            mel = mel.squeeze(0)

        # Convert to linear spectrogram
        linear = librosa.feature.inverse.mel_to_stft(
            mel,
            sr=self.sample_rate,
            n_fft=self.n_fft,
            power=self.power,
            fmin=self.mel_fmin,
            fmax=self.mel_fmax,
            htk=self.mel_scale == "htk",
        )

        # Reconstruct audio
        audio = self.griffin_lim(linear, return_tensor=return_tensor)

        return audio

    def get_config(self) -> Dict:
        """
        Get the configuration of the audio processor.

        Returns:
            Dictionary containing the configuration.
        """
        return {
            "sample_rate": self.sample_rate,
            "n_fft": self.n_fft,
            "hop_length": self.hop_length,
            "win_length": self.win_length,
            "n_mels": self.n_mels,
            "mel_fmin": self.mel_fmin,
            "mel_fmax": self.mel_fmax,
            "use_log_mel": self.use_log_mel,
            "normalize": self.normalize,
            "center": self.center,
            "pad_mode": self.pad_mode,
            "power": self.power,
            "norm": self.norm,
            "mel_scale": self.mel_scale,
        }

    @classmethod
    def from_config(cls, config: Dict, device: Optional[torch.device] = None) -> "AudioProcessor":
        """
        Create an audio processor from a configuration dictionary.

        Args:
            config: Configuration dictionary.
            device: Device to use for computation.

        Returns:
            AudioProcessor instance.
        """
        return cls(
            sample_rate=config.get("sample_rate", 22050),
            n_fft=config.get("n_fft", 1024),
            hop_length=config.get("hop_length", 256),
            win_length=config.get("win_length", None),
            n_mels=config.get("n_mels", 80),
            mel_fmin=config.get("mel_fmin", 0.0),
            mel_fmax=config.get("mel_fmax", None),
            use_log_mel=config.get("use_log_mel", True),
            normalize=config.get("normalize", True),
            center=config.get("center", True),
            pad_mode=config.get("pad_mode", "reflect"),
            power=config.get("power", 2.0),
            norm=config.get("norm", "slaney"),
            mel_scale=config.get("mel_scale", "htk"),
            device=device,
        )