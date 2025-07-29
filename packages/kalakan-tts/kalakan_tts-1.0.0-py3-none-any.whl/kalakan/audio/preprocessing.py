"""
Audio preprocessing for TTS.

This module provides functionality for preprocessing audio signals for TTS,
including normalization, silence trimming, and augmentation.
"""

from typing import Dict, List, Optional, Tuple, Union

import librosa
import numpy as np
import torch
import torchaudio
from torchaudio.transforms import Resample


class AudioPreprocessor:
    """
    Audio preprocessor for TTS.
    
    This class provides methods for preprocessing audio signals for TTS,
    including normalization, silence trimming, and augmentation.
    """
    
    def __init__(
        self,
        sample_rate: int = 22050,
        trim_silence: bool = True,
        silence_threshold: float = 60,
        normalize: bool = True,
        target_rms: float = 0.2,
        preemphasis: bool = True,
        preemphasis_coef: float = 0.97,
        device: Optional[torch.device] = None,
    ):
        """
        Initialize the audio preprocessor.
        
        Args:
            sample_rate: Audio sample rate in Hz.
            trim_silence: Whether to trim silence from the beginning and end.
            silence_threshold: Threshold for silence detection in dB.
            normalize: Whether to normalize the audio.
            target_rms: Target RMS level for normalization.
            preemphasis: Whether to apply preemphasis.
            preemphasis_coef: Preemphasis coefficient.
            device: Device to use for computation.
        """
        self.sample_rate = sample_rate
        self.trim_silence = trim_silence
        self.silence_threshold = silence_threshold
        self.normalize = normalize
        self.target_rms = target_rms
        self.preemphasis = preemphasis
        self.preemphasis_coef = preemphasis_coef
        self.device = device if device is not None else torch.device("cpu")
    
    def preprocess(
        self, 
        audio: Union[np.ndarray, torch.Tensor],
        return_tensor: bool = True,
    ) -> Union[np.ndarray, torch.Tensor]:
        """
        Preprocess audio signal.
        
        Args:
            audio: Audio signal as a numpy array or torch tensor.
            return_tensor: Whether to return a torch tensor or numpy array.
            
        Returns:
            Preprocessed audio as a torch tensor or numpy array.
        """
        # Convert to numpy for librosa operations if needed
        is_tensor = isinstance(audio, torch.Tensor)
        if is_tensor:
            audio_np = audio.cpu().numpy()
        else:
            audio_np = audio
        
        # Trim silence if requested
        if self.trim_silence:
            audio_np = self._trim_silence(audio_np)
        
        # Normalize if requested
        if self.normalize:
            audio_np = self._normalize(audio_np)
        
        # Apply preemphasis if requested
        if self.preemphasis:
            audio_np = self._preemphasis(audio_np)
        
        # Convert back to tensor if needed
        if return_tensor:
            return torch.from_numpy(audio_np).float().to(self.device)
        else:
            return audio_np
    
    def preprocess_file(
        self, 
        file_path: str,
        return_tensor: bool = True,
    ) -> Union[np.ndarray, torch.Tensor]:
        """
        Preprocess audio from a file.
        
        Args:
            file_path: Path to the audio file.
            return_tensor: Whether to return a torch tensor or numpy array.
            
        Returns:
            Preprocessed audio as a torch tensor or numpy array.
        """
        # Load audio file
        audio, sr = torchaudio.load(file_path)
        
        # Resample if needed
        if sr != self.sample_rate:
            resampler = Resample(sr, self.sample_rate)
            audio = resampler(audio)
        
        # Convert to mono if needed
        if audio.shape[0] > 1:
            audio = torch.mean(audio, dim=0, keepdim=True)
        
        # Preprocess audio
        return self.preprocess(audio.squeeze(0), return_tensor=return_tensor)
    
    def _trim_silence(self, audio: np.ndarray) -> np.ndarray:
        """
        Trim silence from the beginning and end of the audio.
        
        Args:
            audio: Audio signal as a numpy array.
            
        Returns:
            Trimmed audio as a numpy array.
        """
        return librosa.effects.trim(
            audio, 
            top_db=self.silence_threshold, 
            frame_length=2048, 
            hop_length=512
        )[0]
    
    def _normalize(self, audio: np.ndarray) -> np.ndarray:
        """
        Normalize the audio to a target RMS level.
        
        Args:
            audio: Audio signal as a numpy array.
            
        Returns:
            Normalized audio as a numpy array.
        """
        # Calculate current RMS
        rms = np.sqrt(np.mean(audio ** 2))
        
        # Avoid division by zero
        if rms > 0:
            # Scale to target RMS
            return audio * (self.target_rms / rms)
        else:
            return audio
    
    def _preemphasis(self, audio: np.ndarray) -> np.ndarray:
        """
        Apply preemphasis to the audio.
        
        Args:
            audio: Audio signal as a numpy array.
            
        Returns:
            Preemphasized audio as a numpy array.
        """
        return np.append(audio[0], audio[1:] - self.preemphasis_coef * audio[:-1])
    
    def get_config(self) -> Dict:
        """
        Get the configuration of the audio preprocessor.
        
        Returns:
            Dictionary containing the configuration.
        """
        return {
            "sample_rate": self.sample_rate,
            "trim_silence": self.trim_silence,
            "silence_threshold": self.silence_threshold,
            "normalize": self.normalize,
            "target_rms": self.target_rms,
            "preemphasis": self.preemphasis,
            "preemphasis_coef": self.preemphasis_coef,
        }
    
    @classmethod
    def from_config(cls, config: Dict, device: Optional[torch.device] = None) -> "AudioPreprocessor":
        """
        Create an audio preprocessor from a configuration dictionary.
        
        Args:
            config: Configuration dictionary.
            device: Device to use for computation.
            
        Returns:
            AudioPreprocessor instance.
        """
        return cls(
            sample_rate=config.get("sample_rate", 22050),
            trim_silence=config.get("trim_silence", True),
            silence_threshold=config.get("silence_threshold", 60),
            normalize=config.get("normalize", True),
            target_rms=config.get("target_rms", 0.2),
            preemphasis=config.get("preemphasis", True),
            preemphasis_coef=config.get("preemphasis_coef", 0.97),
            device=device,
        )


class AudioAugmenter:
    """
    Audio augmenter for TTS.
    
    This class provides methods for augmenting audio signals for TTS training,
    including time stretching, pitch shifting, and adding noise.
    """
    
    def __init__(
        self,
        sample_rate: int = 22050,
        time_stretch: bool = True,
        time_stretch_range: Tuple[float, float] = (0.9, 1.1),
        pitch_shift: bool = True,
        pitch_shift_range: Tuple[int, int] = (-2, 2),
        add_noise: bool = True,
        noise_level_range: Tuple[float, float] = (0.001, 0.005),
        apply_rir: bool = False,
        rir_files: Optional[List[str]] = None,
        device: Optional[torch.device] = None,
    ):
        """
        Initialize the audio augmenter.
        
        Args:
            sample_rate: Audio sample rate in Hz.
            time_stretch: Whether to apply time stretching.
            time_stretch_range: Range of time stretch factors.
            pitch_shift: Whether to apply pitch shifting.
            pitch_shift_range: Range of pitch shift in semitones.
            add_noise: Whether to add noise.
            noise_level_range: Range of noise levels.
            apply_rir: Whether to apply room impulse response.
            rir_files: List of RIR file paths.
            device: Device to use for computation.
        """
        self.sample_rate = sample_rate
        self.time_stretch = time_stretch
        self.time_stretch_range = time_stretch_range
        self.pitch_shift = pitch_shift
        self.pitch_shift_range = pitch_shift_range
        self.add_noise = add_noise
        self.noise_level_range = noise_level_range
        self.apply_rir = apply_rir
        self.rir_files = rir_files if rir_files is not None else []
        self.device = device if device is not None else torch.device("cpu")
        
        # Load RIR files if provided
        self.rir_list = []
        if self.apply_rir and self.rir_files:
            for rir_file in self.rir_files:
                rir, sr = torchaudio.load(rir_file)
                if sr != self.sample_rate:
                    resampler = Resample(sr, self.sample_rate)
                    rir = resampler(rir)
                self.rir_list.append(rir.squeeze(0))
    
    def augment(
        self, 
        audio: Union[np.ndarray, torch.Tensor],
        return_tensor: bool = True,
    ) -> Union[np.ndarray, torch.Tensor]:
        """
        Augment audio signal.
        
        Args:
            audio: Audio signal as a numpy array or torch tensor.
            return_tensor: Whether to return a torch tensor or numpy array.
            
        Returns:
            Augmented audio as a torch tensor or numpy array.
        """
        # Convert to numpy for librosa operations if needed
        is_tensor = isinstance(audio, torch.Tensor)
        if is_tensor:
            audio_np = audio.cpu().numpy()
        else:
            audio_np = audio
        
        # Apply time stretching if requested
        if self.time_stretch:
            audio_np = self._time_stretch(audio_np)
        
        # Apply pitch shifting if requested
        if self.pitch_shift:
            audio_np = self._pitch_shift(audio_np)
        
        # Add noise if requested
        if self.add_noise:
            audio_np = self._add_noise(audio_np)
        
        # Convert back to tensor if needed
        if is_tensor or return_tensor:
            audio_tensor = torch.from_numpy(audio_np).float().to(self.device)
            
            # Apply RIR if requested
            if self.apply_rir and self.rir_list:
                audio_tensor = self._apply_rir(audio_tensor)
            
            return audio_tensor
        else:
            return audio_np
    
    def _time_stretch(self, audio: np.ndarray) -> np.ndarray:
        """
        Apply time stretching to the audio.
        
        Args:
            audio: Audio signal as a numpy array.
            
        Returns:
            Time-stretched audio as a numpy array.
        """
        # Randomly select a stretch factor
        stretch_factor = np.random.uniform(
            self.time_stretch_range[0], 
            self.time_stretch_range[1]
        )
        
        # Apply time stretching
        return librosa.effects.time_stretch(audio, rate=stretch_factor)
    
    def _pitch_shift(self, audio: np.ndarray) -> np.ndarray:
        """
        Apply pitch shifting to the audio.
        
        Args:
            audio: Audio signal as a numpy array.
            
        Returns:
            Pitch-shifted audio as a numpy array.
        """
        # Randomly select a pitch shift
        n_steps = np.random.randint(
            self.pitch_shift_range[0], 
            self.pitch_shift_range[1] + 1
        )
        
        # Apply pitch shifting
        return librosa.effects.pitch_shift(
            audio, 
            sr=self.sample_rate, 
            n_steps=n_steps
        )
    
    def _add_noise(self, audio: np.ndarray) -> np.ndarray:
        """
        Add noise to the audio.
        
        Args:
            audio: Audio signal as a numpy array.
            
        Returns:
            Noisy audio as a numpy array.
        """
        # Randomly select a noise level
        noise_level = np.random.uniform(
            self.noise_level_range[0], 
            self.noise_level_range[1]
        )
        
        # Generate noise
        noise = np.random.randn(len(audio))
        
        # Add noise to the audio
        return audio + noise_level * noise
    
    def _apply_rir(self, audio: torch.Tensor) -> torch.Tensor:
        """
        Apply room impulse response to the audio.
        
        Args:
            audio: Audio signal as a torch tensor.
            
        Returns:
            Audio with RIR applied as a torch tensor.
        """
        if not self.rir_list:
            return audio
        
        # Randomly select an RIR
        rir = self.rir_list[np.random.randint(0, len(self.rir_list))]
        
        # Apply convolution
        return torch.nn.functional.conv1d(
            audio.unsqueeze(0).unsqueeze(0),
            rir.unsqueeze(0).unsqueeze(0),
            padding=rir.shape[0] - 1
        ).squeeze(0).squeeze(0)
    
    def get_config(self) -> Dict:
        """
        Get the configuration of the audio augmenter.
        
        Returns:
            Dictionary containing the configuration.
        """
        return {
            "sample_rate": self.sample_rate,
            "time_stretch": self.time_stretch,
            "time_stretch_range": self.time_stretch_range,
            "pitch_shift": self.pitch_shift,
            "pitch_shift_range": self.pitch_shift_range,
            "add_noise": self.add_noise,
            "noise_level_range": self.noise_level_range,
            "apply_rir": self.apply_rir,
            "rir_files": self.rir_files,
        }
    
    @classmethod
    def from_config(cls, config: Dict, device: Optional[torch.device] = None) -> "AudioAugmenter":
        """
        Create an audio augmenter from a configuration dictionary.
        
        Args:
            config: Configuration dictionary.
            device: Device to use for computation.
            
        Returns:
            AudioAugmenter instance.
        """
        return cls(
            sample_rate=config.get("sample_rate", 22050),
            time_stretch=config.get("time_stretch", True),
            time_stretch_range=config.get("time_stretch_range", (0.9, 1.1)),
            pitch_shift=config.get("pitch_shift", True),
            pitch_shift_range=config.get("pitch_shift_range", (-2, 2)),
            add_noise=config.get("add_noise", True),
            noise_level_range=config.get("noise_level_range", (0.001, 0.005)),
            apply_rir=config.get("apply_rir", False),
            rir_files=config.get("rir_files", None),
            device=device,
        )