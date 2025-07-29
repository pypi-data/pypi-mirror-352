"""
Aligned dataset for Kalakan TTS.

This module provides dataset classes for loading and processing
text and audio data with phoneme-level alignment for TTS training.
"""

import os
import json
import random
import numpy as np
import torch
import torchaudio
from typing import Dict, List, Optional, Tuple, Union
from torch.utils.data import Dataset

from kalakan.audio.utils import load_audio
from kalakan.text.cleaner import clean_text
from kalakan.text.normalizer import normalize_text
from kalakan.text.enhanced_twi_g2p import EnhancedTwiG2P


class AlignedTTSDataset(Dataset):
    """
    Dataset for TTS training with phoneme-level alignment.

    This dataset loads text and audio pairs with phoneme-level alignment
    information for improved TTS training.
    """

    def __init__(
        self,
        metadata_path: str,
        root_dir: Optional[str] = None,
        g2p: Optional[EnhancedTwiG2P] = None,
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
        alignment_path: Optional[str] = None,
        use_pitch_contour: bool = True,
        use_energy_contour: bool = True,
        augmentation_config: Optional[Dict] = None,
    ):
        """
        Initialize the aligned TTS dataset.

        Args:
            metadata_path: Path to the metadata file.
            root_dir: Root directory for audio files. If None, paths in metadata are assumed to be absolute.
            g2p: Grapheme-to-phoneme converter. If None, a default EnhancedTwiG2P converter is used.
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
            alignment_path: Path to the phoneme-level alignment file.
            use_pitch_contour: Whether to include pitch contour information.
            use_energy_contour: Whether to include energy contour information.
            augmentation_config: Configuration for data augmentation.
        """
        self.root_dir = root_dir
        self.g2p = g2p if g2p is not None else EnhancedTwiG2P()
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
        self.use_pitch_contour = use_pitch_contour
        self.use_energy_contour = use_energy_contour
        self.augmentation_config = augmentation_config or {}

        # Load metadata
        self.metadata = self._load_metadata(metadata_path)

        # Load alignment data if provided
        self.alignments = {}
        if alignment_path and os.path.exists(alignment_path):
            self._load_alignments(alignment_path)

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

        # Create pitch extractor if needed
        if self.use_pitch_contour:
            self.pitch_extractor = self._create_pitch_extractor()

        # Create energy extractor if needed
        if self.use_energy_contour:
            self.energy_extractor = self._create_energy_extractor()

    def _create_pitch_extractor(self):
        """
        Create a pitch extractor.

        Returns:
            A function that extracts pitch from audio.
        """
        # We'll use a simple function that computes pitch using PyTorch's implementation
        def extract_pitch(audio: torch.Tensor) -> torch.Tensor:
            # Ensure audio is 2D [channels, samples]
            if audio.dim() == 1:
                audio = audio.unsqueeze(0)

            # Compute pitch using autocorrelation
            # This is a simplified implementation - in practice, you'd use a more robust method
            # like PYIN or CREPE
            frame_length = self.win_length
            hop_length = self.hop_length

            # Compute frames
            frames = audio.unfold(1, frame_length, hop_length)

            # Compute autocorrelation for each frame
            autocorr = torch.nn.functional.conv1d(
                frames.unsqueeze(1),
                frames.unsqueeze(1).flip(2),
                padding=frame_length-1
            )

            # Extract the relevant part of the autocorrelation
            autocorr = autocorr[:, :, frame_length-1:2*frame_length-1]

            # Find peaks in autocorrelation
            # For simplicity, we'll just take the maximum value
            _, peak_indices = torch.max(autocorr, dim=2)

            # Convert indices to frequencies
            pitch = self.sample_rate / (peak_indices + 1)

            # Normalize pitch
            pitch = (pitch - 50) / 500  # Normalize to roughly [-1, 1]

            return pitch.squeeze(0)

        return extract_pitch

    def _create_energy_extractor(self):
        """
        Create an energy extractor.

        Returns:
            A function that extracts energy from audio.
        """
        def extract_energy(audio: torch.Tensor) -> torch.Tensor:
            # Ensure audio is 2D [channels, samples]
            if audio.dim() == 1:
                audio = audio.unsqueeze(0)

            # Compute energy as the L2 norm of each frame
            frame_length = self.win_length
            hop_length = self.hop_length

            # Compute frames
            frames = audio.unfold(1, frame_length, hop_length)

            # Compute energy for each frame
            energy = torch.norm(frames, p=2, dim=2)

            # Normalize energy
            energy = energy / energy.max()

            return energy.squeeze(0)

        return extract_energy

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

    def _load_alignments(self, alignment_path: str) -> None:
        """
        Load phoneme-level alignments from a file.

        The alignment file should be a JSON file mapping audio file names to
        lists of (phoneme, start_time, end_time) tuples.

        Args:
            alignment_path: Path to the alignment file.
        """
        with open(alignment_path, 'r', encoding='utf-8') as f:
            self.alignments = json.load(f)

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

    def _process_audio(self, audio_path: str) -> Dict[str, torch.Tensor]:
        """
        Process audio for TTS.

        Args:
            audio_path: Path to the audio file.

        Returns:
            Dictionary containing:
                - audio: Audio waveform.
                - mels: Mel spectrogram.
                - pitch: Pitch contour (if enabled).
                - energy: Energy contour (if enabled).
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

        # Create output dictionary
        output = {
            'audio': audio.squeeze(0),
            'mels': mel,
        }

        # Extract pitch if enabled
        if self.use_pitch_contour:
            pitch = self.pitch_extractor(audio)
            output['pitch'] = pitch

        # Extract energy if enabled
        if self.use_energy_contour:
            energy = self.energy_extractor(audio)
            output['energy'] = energy

        return output

    def _get_alignment(self, audio_path: str, phoneme_sequence: List[int]) -> Optional[torch.Tensor]:
        """
        Get phoneme-level alignment for an audio file.

        Args:
            audio_path: Path to the audio file.
            phoneme_sequence: Sequence of phoneme IDs.

        Returns:
            Tensor of shape [num_phonemes, num_frames] containing the alignment
            probabilities. If no alignment is available, returns None.
        """
        # Get the base filename without extension
        base_filename = os.path.splitext(os.path.basename(audio_path))[0]

        # Check if alignment is available
        if base_filename not in self.alignments:
            return None

        # Get alignment
        alignment = self.alignments[base_filename]

        # Convert alignment to tensor
        # The alignment is a list of (phoneme, start_time, end_time) tuples
        # We need to convert it to a tensor of shape [num_phonemes, num_frames]
        num_phonemes = len(phoneme_sequence)
        num_frames = int(alignment[-1][2] * self.sample_rate / self.hop_length) + 1

        # Initialize alignment tensor
        alignment_tensor = torch.zeros(num_phonemes, num_frames)

        # Fill alignment tensor
        for phoneme, start_time, end_time in alignment:
            # Convert time to frame indices
            start_frame = int(start_time * self.sample_rate / self.hop_length)
            end_frame = int(end_time * self.sample_rate / self.hop_length) + 1

            # Find the corresponding phoneme index
            phoneme_idx = phoneme_sequence.index(phoneme)

            # Set alignment probability to 1.0 for the frames corresponding to this phoneme
            alignment_tensor[phoneme_idx, start_frame:end_frame] = 1.0

        return alignment_tensor

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
                - pitch: Pitch contour (if enabled).
                - energy: Energy contour (if enabled).
                - alignment: Phoneme-level alignment (if available).
        """
        # Get metadata
        item = self.metadata[idx]
        text = item['text']
        audio_path = self._get_audio_path(item['audio_path'])

        # Process text
        processed_text, phoneme_sequence = self._process_text(text)

        # Process audio
        audio_data = self._process_audio(audio_path)
        audio = audio_data['audio']
        mel = audio_data['mels']

        # Get alignment if available
        alignment = self._get_alignment(audio_path, phoneme_sequence)

        # Create output dictionary
        output = {
            'text': processed_text,
            'phonemes': torch.tensor(phoneme_sequence, dtype=torch.long),
            'phoneme_lengths': torch.tensor(len(phoneme_sequence), dtype=torch.long),
            'audio': audio,  # [samples]
            'mels': mel,  # [n_mels, time]
            'mel_lengths': torch.tensor(mel.size(1), dtype=torch.long),
            'audio_paths': audio_path,
        }

        # Add pitch if enabled
        if self.use_pitch_contour and 'pitch' in audio_data:
            output['pitch'] = audio_data['pitch']

        # Add energy if enabled
        if self.use_energy_contour and 'energy' in audio_data:
            output['energy'] = audio_data['energy']

        # Add alignment if available
        if alignment is not None:
            output['alignment'] = alignment

        return output


class AlignedTTSCollate:
    """
    Collate function for aligned TTS batches.

    This class provides a collate function for creating batches of aligned TTS data,
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
        Collate a batch of aligned TTS data.

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
        phonemes = torch.full(size=(batch_size, int(max_phoneme_length)), fill_value=self.pad_value, dtype=torch.long)
        mels = torch.zeros(size=(batch_size, batch[0]['mels'].size(0), int(max_mel_length)))
        audio = torch.zeros(size=(batch_size, int(max_audio_length)))

        # Initialize optional tensors
        has_pitch = 'pitch' in batch[0]
        has_energy = 'energy' in batch[0]
        has_alignment = 'alignment' in batch[0]

        if has_pitch:
            pitch = torch.zeros(size=(batch_size, int(max_mel_length)))
        if has_energy:
            energy = torch.zeros(size=(batch_size, int(max_mel_length)))
        if has_alignment:
            alignment = torch.zeros(size=(batch_size, int(max_phoneme_length), int(max_mel_length)))

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

            # Fill optional tensors
            if has_pitch:
                pitch[i, :mel_length] = item['pitch'][:mel_length]
            if has_energy:
                energy[i, :mel_length] = item['energy'][:mel_length]
            if has_alignment:
                alignment[i, :phoneme_length, :mel_length] = item['alignment'][:, :mel_length]

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

        # Add optional tensors
        if has_pitch:
            output['pitch'] = pitch
        if has_energy:
            output['energy'] = energy
        if has_alignment:
            output['alignment'] = alignment

        return output