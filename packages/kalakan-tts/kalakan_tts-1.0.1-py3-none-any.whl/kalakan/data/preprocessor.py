"""
Data preprocessing for Kalakan TTS.

This module provides classes for preprocessing text and audio data
for TTS training and inference.
"""

import os
import json
from typing import Dict, List, Optional, Tuple, Union

import librosa
import numpy as np
import torch
import torchaudio

from kalakan.audio.utils import load_audio, save_audio
from kalakan.text.cleaner import clean_text
from kalakan.text.normalizer import normalize_text
from kalakan.text.twi_g2p import TwiG2P


class AudioPreprocessor:
    """
    Preprocessor for audio data.
    
    This class provides methods for preprocessing audio data for TTS,
    including loading, resampling, normalization, and mel spectrogram extraction.
    """
    
    def __init__(
        self,
        sample_rate: int = 22050,
        n_mels: int = 80,
        hop_length: int = 256,
        win_length: int = 1024,
        n_fft: int = 1024,
        f_min: float = 0.0,
        f_max: Optional[float] = None,
        trim_silence: bool = True,
        silence_threshold: float = 0.01,
        silence_padding: int = 100,
    ):
        """
        Initialize the audio preprocessor.
        
        Args:
            sample_rate: Audio sample rate.
            n_mels: Number of mel bands.
            hop_length: Hop length for STFT.
            win_length: Window length for STFT.
            n_fft: FFT size.
            f_min: Minimum frequency for mel bands.
            f_max: Maximum frequency for mel bands. If None, defaults to sample_rate/2.
            trim_silence: Whether to trim silence from the audio.
            silence_threshold: Threshold for silence detection.
            silence_padding: Padding to add after trimming silence (in samples).
        """
        self.sample_rate = sample_rate
        self.n_mels = n_mels
        self.hop_length = hop_length
        self.win_length = win_length
        self.n_fft = n_fft
        self.f_min = f_min
        self.f_max = f_max if f_max is not None else sample_rate / 2
        self.trim_silence = trim_silence
        self.silence_threshold = silence_threshold
        self.silence_padding = silence_padding
        
        # Create mel spectrogram transform
        self.mel_transform = torchaudio.transforms.MelSpectrogram(
            sample_rate=sample_rate,
            n_fft=n_fft,
            win_length=win_length,
            hop_length=hop_length,
            f_min=f_min,
            f_max=self.f_max,
            n_mels=n_mels,
            power=1.0,
            normalized=True,
        )
    
    def preprocess_audio(
        self,
        audio_path: str,
        output_dir: Optional[str] = None,
        return_tensor: bool = True,
    ) -> Tuple[Union[np.ndarray, torch.Tensor], Union[np.ndarray, torch.Tensor]]:
        """
        Preprocess an audio file.
        
        Args:
            audio_path: Path to the audio file.
            output_dir: Directory to save preprocessed audio. If None, audio is not saved.
            return_tensor: Whether to return torch tensors or numpy arrays.
            
        Returns:
            Tuple containing:
                - Preprocessed audio waveform.
                - Mel spectrogram.
        """
        # Load audio
        audio = load_audio(
            audio_path,
            sample_rate=self.sample_rate,
            mono=True,
            normalize=True,
            return_tensor=True,
        )
        
        # Ensure audio is 2D [channels, samples]
        if audio.dim() == 1:
            audio = audio.unsqueeze(0)
        
        # Trim silence if requested
        if self.trim_silence:
            audio_np = audio.numpy()
            audio_np = self._trim_silence(audio_np)
            audio = torch.from_numpy(audio_np).float()
        
        # Compute mel spectrogram
        mel = self.mel_transform(audio)
        
        # Convert to log scale
        mel = torch.log(torch.clamp(mel, min=1e-5))
        
        # Save preprocessed audio if requested
        if output_dir is not None:
            os.makedirs(output_dir, exist_ok=True)
            
            # Get base filename
            base_filename = os.path.splitext(os.path.basename(audio_path))[0]
            
            # Save audio
            audio_output_path = os.path.join(output_dir, f"{base_filename}.wav")
            save_audio(audio.squeeze(0).numpy(), audio_output_path, self.sample_rate)
            
            # Save mel spectrogram
            mel_output_path = os.path.join(output_dir, f"{base_filename}.npy")
            np.save(mel_output_path, mel.numpy())
        
        # Convert to numpy if requested
        if not return_tensor:
            audio = audio.numpy()
            mel = mel.numpy()
        
        return audio, mel
    
    def _trim_silence(self, audio: np.ndarray) -> np.ndarray:
        """
        Trim silence from the beginning and end of an audio signal.
        
        Args:
            audio: Audio signal [channels, samples].
            
        Returns:
            Trimmed audio signal [channels, samples].
        """
        # Convert to mono for silence detection
        mono_audio = audio.mean(axis=0) if audio.ndim > 1 else audio
        
        # Trim silence
        trimmed_audio, _ = librosa.effects.trim(
            mono_audio,
            top_db=20,
            frame_length=self.win_length,
            hop_length=self.hop_length,
        )
        
        # Add padding
        trimmed_audio = np.pad(
            trimmed_audio,
            (self.silence_padding, self.silence_padding),
            mode='constant',
        )
        
        # If original audio was multi-channel, replicate the trimming
        if audio.ndim > 1:
            # Get the trimmed indices
            start_idx = max(0, len(mono_audio) - len(trimmed_audio) - self.silence_padding)
            end_idx = min(len(mono_audio), start_idx + len(trimmed_audio))
            
            # Apply to all channels
            trimmed_audio = audio[:, start_idx:end_idx]
        
        return trimmed_audio
    
    def batch_preprocess(
        self,
        audio_paths: List[str],
        output_dir: str,
        metadata_path: Optional[str] = None,
    ) -> Dict[str, Dict[str, str]]:
        """
        Preprocess a batch of audio files.
        
        Args:
            audio_paths: List of paths to audio files.
            output_dir: Directory to save preprocessed audio.
            metadata_path: Path to save metadata. If None, metadata is not saved.
            
        Returns:
            Dictionary mapping audio paths to preprocessing information.
        """
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize metadata
        metadata = {}
        
        # Process each audio file
        for audio_path in audio_paths:
            try:
                # Preprocess audio
                audio, mel = self.preprocess_audio(audio_path, output_dir, return_tensor=False)
                
                # Get base filename
                base_filename = os.path.splitext(os.path.basename(audio_path))[0]
                
                # Add to metadata
                metadata[audio_path] = {
                    'preprocessed_audio': os.path.join(output_dir, f"{base_filename}.wav"),
                    'preprocessed_mel': os.path.join(output_dir, f"{base_filename}.npy"),
                    'duration': audio.shape[1] / self.sample_rate,
                    'n_frames': mel.shape[2],
                }
            except Exception as e:
                print(f"Error processing {audio_path}: {e}")
        
        # Save metadata if requested
        if metadata_path is not None:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
        
        return metadata


class TextPreprocessor:
    """
    Preprocessor for text data.
    
    This class provides methods for preprocessing text data for TTS,
    including cleaning, normalization, and phoneme conversion.
    """
    
    def __init__(
        self,
        g2p: Optional[TwiG2P] = None,
        clean_text_flag: bool = True,
        normalize_text_flag: bool = True,
    ):
        """
        Initialize the text preprocessor.
        
        Args:
            g2p: Grapheme-to-phoneme converter. If None, a default TwiG2P converter is used.
            clean_text_flag: Whether to clean the text.
            normalize_text_flag: Whether to normalize the text.
        """
        self.g2p = g2p if g2p is not None else TwiG2P()
        self.clean_text_flag = clean_text_flag
        self.normalize_text_flag = normalize_text_flag
    
    def preprocess_text(self, text: str) -> Tuple[str, List[str], List[int]]:
        """
        Preprocess text for TTS.
        
        Args:
            text: Input text.
            
        Returns:
            Tuple containing:
                - Processed text.
                - List of phonemes.
                - Phoneme sequence (as IDs).
        """
        # Clean and normalize text
        processed_text = text
        if self.clean_text_flag:
            processed_text = clean_text(processed_text)
        if self.normalize_text_flag:
            processed_text = normalize_text(processed_text)
        
        # Convert to phonemes
        phonemes = self.g2p.text_to_phonemes(processed_text)
        
        # Convert to phoneme sequence
        phoneme_sequence = self.g2p.text_to_phoneme_sequence(processed_text)
        
        return processed_text, phonemes, phoneme_sequence
    
    def batch_preprocess(
        self,
        texts: List[str],
        output_path: Optional[str] = None,
    ) -> Dict[str, Dict[str, Union[str, List[str], List[int]]]]:
        """
        Preprocess a batch of texts.
        
        Args:
            texts: List of input texts.
            output_path: Path to save preprocessed texts. If None, texts are not saved.
            
        Returns:
            Dictionary mapping texts to preprocessing information.
        """
        # Initialize metadata
        metadata = {}
        
        # Process each text
        for text in texts:
            try:
                # Preprocess text
                processed_text, phonemes, phoneme_sequence = self.preprocess_text(text)
                
                # Add to metadata
                metadata[text] = {
                    'processed_text': processed_text,
                    'phonemes': phonemes,
                    'phoneme_sequence': phoneme_sequence,
                    'n_phonemes': len(phonemes),
                }
            except Exception as e:
                print(f"Error processing '{text}': {e}")
        
        # Save metadata if requested
        if output_path is not None:
            with open(output_path, 'w', encoding='utf-8') as f:
                # Convert lists to strings for JSON serialization
                serializable_metadata = {}
                for text, info in metadata.items():
                    serializable_info = info.copy()
                    serializable_info['phonemes'] = ' '.join(info['phonemes'])
                    serializable_info['phoneme_sequence'] = [int(x) for x in info['phoneme_sequence']]
                    serializable_metadata[text] = serializable_info
                
                json.dump(serializable_metadata, f, indent=2)
        
        return metadata