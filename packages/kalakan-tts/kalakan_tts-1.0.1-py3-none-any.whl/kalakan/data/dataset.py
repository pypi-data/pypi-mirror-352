"""
Dataset classes for Kalakan TTS.

This module provides dataset classes for loading and processing
text and audio data for TTS training.
"""

import os
import json
import random
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import torch
import torchaudio
from torch.utils.data import Dataset

from kalakan.audio.utils import load_audio
from kalakan.text.cleaner import clean_text
from kalakan.text.normalizer import normalize_text
from kalakan.text.twi_g2p import TwiG2P


class TTSDataset(Dataset):
    """
    Dataset for TTS training.

    This dataset loads text and audio pairs from a metadata file and
    preprocesses them for TTS training.
    """

    def __init__(
        self,
        metadata_path: str,
        root_dir: Optional[str] = None,
        g2p: Optional[TwiG2P] = None,
        sample_rate: int = 22050,
        n_mels: int = 80,
        hop_length: int = 256,
        win_length: int = 1024,
        n_fft: int = 1024,
        clean_text_flag: bool = True,
        normalize_text_flag: bool = True,
        max_audio_length: Optional[int] = None,
        max_text_length: Optional[int] = None,
        return_segment: bool = False,
        segment_length: int = 8192,
    ):
        """
        Initialize the TTS dataset.

        Args:
            metadata_path: Path to the metadata file.
            root_dir: Root directory for audio files. If None, paths in metadata are assumed to be absolute.
            g2p: Grapheme-to-phoneme converter. If None, a default TwiG2P converter is used.
            sample_rate: Audio sample rate.
            n_mels: Number of mel bands.
            hop_length: Hop length for STFT.
            win_length: Window length for STFT.
            n_fft: FFT size.
            clean_text_flag: Whether to clean the text.
            normalize_text_flag: Whether to normalize the text.
            max_audio_length: Maximum audio length in samples. Longer audio will be filtered out.
            max_text_length: Maximum text length in characters. Longer text will be filtered out.
            return_segment: Whether to return a random segment of the audio.
            segment_length: Length of the audio segment in samples.
        """
        self.root_dir = root_dir
        self.g2p = g2p if g2p is not None else TwiG2P()
        self.sample_rate = sample_rate
        self.n_mels = n_mels
        self.hop_length = hop_length
        self.win_length = win_length
        self.n_fft = n_fft
        self.clean_text_flag = clean_text_flag
        self.normalize_text_flag = normalize_text_flag
        self.max_audio_length = max_audio_length
        self.max_text_length = max_text_length
        self.return_segment = return_segment
        self.segment_length = segment_length

        # Load metadata
        self.metadata = self._load_metadata(metadata_path)

        # Create mel spectrogram transform
        self.mel_transform = torchaudio.transforms.MelSpectrogram(
            sample_rate=sample_rate,
            n_fft=n_fft,
            win_length=win_length,
            hop_length=hop_length,
            f_min=0.0,
            f_max=sample_rate / 2,
            n_mels=n_mels,
            power=1.0,
            normalized=True,
        )

    def _load_metadata(self, metadata_path: str) -> List[Dict[str, str]]:
        """
        Load metadata from a file.

        The metadata file should be a JSON file containing a list of dictionaries,
        each with 'text' and 'audio_path' keys.

        Args:
            metadata_path: Path to the metadata file.

        Returns:
            List of metadata entries.
        """
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        # Filter metadata based on max lengths
        filtered_metadata = []
        for item in metadata:
            # Check text length
            if self.max_text_length is not None and len(item['text']) > self.max_text_length:
                continue

            # Check audio length
            if self.max_audio_length is not None:
                audio_path = self._get_audio_path(item['audio_path'])
                try:
                    info = torchaudio.info(audio_path)
                    if info.num_frames > self.max_audio_length:
                        continue
                except Exception:
                    # Skip if audio file is invalid
                    continue

            filtered_metadata.append(item)

        return filtered_metadata

    def _get_audio_path(self, audio_path: str) -> str:
        """
        Get the full audio path.

        Args:
            audio_path: Audio path from metadata.

        Returns:
            Full audio path.
        """
        if self.root_dir is not None:
            return os.path.join(self.root_dir, audio_path)
        else:
            return audio_path

    def _process_text(self, text: str) -> Tuple[str, List[int]]:
        """
        Process text for TTS.

        Args:
            text: Input text.

        Returns:
            Tuple containing:
                - Processed text.
                - Phoneme sequence.
        """
        # Clean and normalize text
        if self.clean_text_flag:
            text = clean_text(text)
        if self.normalize_text_flag:
            text = normalize_text(text)

        # Convert to phoneme sequence
        phoneme_sequence = self.g2p.text_to_phoneme_sequence(text)

        return text, phoneme_sequence

    def _process_audio(self, audio_path: str) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Process audio for TTS.

        Args:
            audio_path: Path to the audio file.

        Returns:
            Tuple containing:
                - Audio waveform.
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
        if isinstance(audio, np.ndarray):
            audio = torch.from_numpy(audio)

        if audio.dim() == 1:
            audio = audio.unsqueeze(0)

        # Get a random segment if requested
        if self.return_segment and audio.size(1) > self.segment_length:
            max_start = audio.size(1) - self.segment_length
            start = random.randint(0, max_start)
            audio = audio[:, start:start+self.segment_length]

        # Compute mel spectrogram
        mel = self.mel_transform(audio)

        # Convert to log scale
        mel = torch.log(torch.clamp(mel, min=1e-5))

        # Ensure both are torch tensors before returning
        if not isinstance(audio, torch.Tensor):
            audio = torch.from_numpy(audio)
        if not isinstance(mel, torch.Tensor):
            mel = torch.from_numpy(mel)

        return audio, mel

    def __len__(self) -> int:
        """
        Get the number of items in the dataset.

        Returns:
            Number of items.
        """
        return len(self.metadata)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """
        Get an item from the dataset.

        Args:
            idx: Item index.

        Returns:
            Dictionary containing:
                - text: Original text.
                - phonemes: Phoneme sequence.
                - phoneme_lengths: Length of the phoneme sequence.
                - audio: Audio waveform.
                - mels: Mel spectrogram.
                - mel_lengths: Length of the mel spectrogram.
                - audio_paths: Path to the audio file.
        """
        # Get metadata
        item = self.metadata[idx]
        text = item['text']
        audio_path = self._get_audio_path(item['audio_path'])

        # Process text
        processed_text, phoneme_sequence = self._process_text(text)

        # Process audio
        audio, mel = self._process_audio(audio_path)

        # Create output dictionary
        output = {
            'text': processed_text,
            'phonemes': torch.tensor(phoneme_sequence, dtype=torch.long),
            'phoneme_lengths': torch.tensor(len(phoneme_sequence), dtype=torch.long),
            'audio': audio.squeeze(0),  # [samples]
            'mels': mel,  # [n_mels, time]
            'mel_lengths': torch.tensor(mel.size(1), dtype=torch.long),
            'audio_paths': audio_path,
        }

        return output


class TTSCollate:
    """
    Collate function for TTS batches.

    This class provides a collate function for creating batches of TTS data,
    handling variable-length sequences by padding.
    """

    def __init__(self, pad_value: int = 0):
        """
        Initialize the collate function.

        Args:
            pad_value: Value to use for padding.
        """
        self.pad_value = pad_value

    def __call__(self, batch: List[Dict[str, torch.Tensor]]) -> Dict[str, torch.Tensor]:
        """
        Collate a batch of TTS data.

        Args:
            batch: List of data items.

        Returns:
            Batched data.
        """
        # Get batch size
        batch_size = len(batch)

        # Get maximum lengths
        max_phoneme_length = max(item['phoneme_lengths'].item() for item in batch)
        max_mel_length = max(item['mel_lengths'].item() for item in batch)
        max_audio_length = max(item['audio'].size(0) for item in batch)

        # Initialize tensors
        phonemes = torch.full(size=(int(batch_size), int(max_phoneme_length)), fill_value=self.pad_value, dtype=torch.long)
        mels = torch.zeros(size=(int(batch_size), int(batch[0]['mels'].size(0)), int(max_mel_length)))
        audio = torch.zeros(size=(int(batch_size), int(max_audio_length)))

        # Fill tensors
        phoneme_lengths = []
        mel_lengths = []
        texts = []
        audio_paths = []

        for i, item in enumerate(batch):
            phoneme_length = item['phoneme_lengths'].item()
            mel_length = item['mel_lengths'].item()
            audio_length = item['audio'].size(0)

            # Fill phonemes
            phonemes[i, :phoneme_length] = item['phonemes']

            # Fill mels
            mels[i, :, :mel_length] = item['mels']

            # Fill audio
            audio[i, :audio_length] = item['audio']

            # Add lengths
            phoneme_lengths.append(phoneme_length)
            mel_lengths.append(mel_length)

            # Add text and audio path
            texts.append(item['text'])
            audio_paths.append(item['audio_paths'])

        # Convert lists to tensors
        phoneme_lengths = torch.tensor(phoneme_lengths, dtype=torch.long)
        mel_lengths = torch.tensor(mel_lengths, dtype=torch.long)

        # Create output dictionary
        output = {
            'texts': texts,
            'phonemes': phonemes,
            'phoneme_lengths': phoneme_lengths,
            'audio': audio,
            'mels': mels,
            'mel_lengths': mel_lengths,
            'audio_paths': audio_paths,
        }

        return output


class VocoderDataset(Dataset):
    """
    Dataset for vocoder training.

    This dataset loads audio files and their corresponding mel spectrograms
    for training vocoder models (mel-to-audio).
    """

    def __init__(
        self,
        metadata_path: str,
        root_dir: Optional[str] = None,
        sample_rate: int = 22050,
        n_mels: int = 80,
        hop_length: int = 256,
        win_length: int = 1024,
        n_fft: int = 1024,
        segment_length: int = 8192,
        random_seed: int = 1234,
    ):
        """
        Initialize the vocoder dataset.

        Args:
            metadata_path: Path to the metadata file.
            root_dir: Root directory for audio files. If None, paths in metadata are assumed to be absolute.
            sample_rate: Audio sample rate.
            n_mels: Number of mel bands.
            hop_length: Hop length for STFT.
            win_length: Window length for STFT.
            n_fft: FFT size.
            segment_length: Length of audio segments to extract.
            random_seed: Random seed for reproducibility.
        """
        self.metadata_path = metadata_path
        self.root_dir = root_dir
        self.sample_rate = sample_rate
        self.n_mels = n_mels
        self.hop_length = hop_length
        self.win_length = win_length
        self.n_fft = n_fft
        self.segment_length = segment_length

        # Set random seed
        random.seed(random_seed)

        # Load metadata
        with open(metadata_path, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)

        # Filter out items with audio shorter than segment_length
        self.valid_indices = []
        for i, item in enumerate(self.metadata):
            audio_path = item['audio_path']
            if root_dir is not None:
                audio_path = os.path.join(root_dir, audio_path)

            # Check audio length
            info = torchaudio.info(audio_path)
            if info.num_frames >= segment_length:
                self.valid_indices.append(i)

        # Setup mel spectrogram transform
        self.mel_transform = torchaudio.transforms.MelSpectrogram(
            sample_rate=sample_rate,
            n_fft=n_fft,
            win_length=win_length,
            hop_length=hop_length,
            f_min=0.0,
            f_max=None,
            n_mels=n_mels,
            power=1.0,
            normalized=False,
        )

    def __len__(self) -> int:
        """
        Get the number of valid items in the dataset.

        Returns:
            Number of valid items.
        """
        return len(self.valid_indices)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """
        Get an item from the dataset.

        Args:
            idx: Item index.

        Returns:
            Dictionary containing:
                - audio: Audio waveform segment.
                - mel: Mel spectrogram of the audio segment.
        """
        # Get metadata item
        metadata_idx = self.valid_indices[idx]
        item = self.metadata[metadata_idx]

        # Get audio path
        audio_path = item['audio_path']
        if self.root_dir is not None:
            audio_path = os.path.join(self.root_dir, audio_path)

        # Load audio
        audio = load_audio(
            audio_path,
            sample_rate=self.sample_rate,
            mono=True,
            normalize=True,
            return_tensor=True
        )

        # Ensure audio is a torch tensor and 2D [channels, samples]
        if isinstance(audio, np.ndarray):
            audio = torch.from_numpy(audio)

        if audio.dim() == 1:
            audio = audio.unsqueeze(0)

        # Extract segment
        if audio.size(1) > self.segment_length:
            max_start = audio.size(1) - self.segment_length
            start = random.randint(0, max_start)
            audio = audio[:, start:start+self.segment_length]
        else:
            # Pad if needed (should not happen due to filtering in __init__)
            padding = self.segment_length - audio.size(1)
            audio = torch.nn.functional.pad(audio, (0, padding))

        # Compute mel spectrogram
        mel = self.mel_transform(audio)

        # Convert to log scale
        mel = torch.log(torch.clamp(mel, min=1e-5))

        # Ensure all return values are torch tensors
        if not isinstance(audio, torch.Tensor):
            audio = torch.from_numpy(audio)
        if not isinstance(mel, torch.Tensor):
            mel = torch.from_numpy(mel)

        return {
            'audio': audio.squeeze(0),  # Remove channel dimension
            'mel': mel,
        }

    @staticmethod
    def collate_fn(batch: List[Dict[str, torch.Tensor]]) -> Dict[str, torch.Tensor]:
        """
        Collate function for DataLoader.

        Args:
            batch: List of items from __getitem__.

        Returns:
            Dictionary containing batched tensors.
        """
        # Stack tensors
        audio = torch.stack([item['audio'] for item in batch])
        mel = torch.stack([item['mel'] for item in batch])

        return {
            'audio': audio,
            'mel': mel,
        }