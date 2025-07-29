"""
Extended dataset for handling large audio files for TTS training.

This module extends the TTSDataset to handle large audio files
by segmenting them into smaller chunks for training.
"""

import os
import random
import torch
import torchaudio
import numpy as np
from typing import Dict, List, Tuple, Optional, Union

from kalakan.data.dataset import TTSDataset, TTSCollate
from kalakan.audio.utils import load_audio
from kalakan.text.twi_g2p import TwiG2P


class ExtendedTTSDataset(TTSDataset):
    """
    Extended dataset for TTS training with large audio files.

    This dataset extends TTSDataset to handle large audio files
    by segmenting them into smaller chunks for training.
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
        return_segment: bool = True,
        segment_length: int = 16000,  # ~0.7 seconds at 22050Hz
        max_mel_length: int = 1000,   # Maximum mel spectrogram length to avoid memory issues
        max_audio_length: Optional[int] = None,
        max_text_length: Optional[int] = None,
    ):
        """
        Initialize the dataset.

        Args:
            metadata_path: Path to metadata file.
            root_dir: Root directory for audio files.
            g2p: Grapheme-to-phoneme converter.
            sample_rate: Audio sample rate.
            n_mels: Number of mel bands.
            hop_length: Hop length for STFT.
            win_length: Window length for STFT.
            n_fft: FFT size.
            clean_text_flag: Whether to clean text.
            normalize_text_flag: Whether to normalize text.
            return_segment: Whether to return a segment of audio.
            segment_length: Length of audio segment in samples.
            max_mel_length: Maximum mel spectrogram length to avoid memory issues.
            max_audio_length: Maximum audio length in samples.
            max_text_length: Maximum text length in characters.
        """
        super().__init__(
            metadata_path=metadata_path,
            root_dir=root_dir,
            g2p=g2p,
            sample_rate=sample_rate,
            n_mels=n_mels,
            hop_length=hop_length,
            win_length=win_length,
            n_fft=n_fft,
            clean_text_flag=clean_text_flag,
            normalize_text_flag=normalize_text_flag,
            max_audio_length=max_audio_length,
            max_text_length=max_text_length,
            return_segment=return_segment,
            segment_length=segment_length,
        )

        self.max_mel_length = max_mel_length

    def _process_audio(self, audio_path: str) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Process audio file.

        This method loads an audio file, segments it if necessary,
        and computes the mel spectrogram.

        Args:
            audio_path: Path to audio file.

        Returns:
            Tuple containing:
                - Audio waveform.
                - Mel spectrogram.
        """
        try:
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

            # Create a custom mel spectrogram transform to ensure consistent dimensions
            custom_mel_transform = torchaudio.transforms.MelSpectrogram(
                sample_rate=self.sample_rate,
                n_fft=self.n_fft,
                win_length=self.win_length,
                hop_length=self.hop_length,
                f_min=0.0,
                f_max=None,
                n_mels=self.n_mels,
                power=1.0,
            )

            # Compute mel spectrogram
            mel = custom_mel_transform(audio)

            # Ensure mel has the correct shape [n_mels, time]
            if mel.dim() == 3:  # If shape is [batch, n_mels, time]
                mel = mel.squeeze(0)  # Convert to [n_mels, time]

            # If mel is too long, segment it
            if mel.size(1) > self.max_mel_length:
                # Calculate how many frames to keep
                start_frame = random.randint(0, mel.size(1) - self.max_mel_length)
                mel = mel[:, start_frame:start_frame + self.max_mel_length]

                # Calculate corresponding audio segment
                audio_start = start_frame * self.hop_length
                audio_end = min((start_frame + self.max_mel_length) * self.hop_length, audio.size(1))
                audio = audio[:, audio_start:audio_end]

            # Final verification
            assert mel.size(0) == self.n_mels, f"Mel spectrogram has {mel.size(0)} channels, expected {self.n_mels}"

            return audio.squeeze(0), mel  # Ensure audio is [samples] not [1, samples]

        except Exception as e:
            print(f"Error processing audio file {audio_path}: {str(e)}")
            # Return dummy tensors with correct dimensions
            dummy_audio = torch.zeros(self.segment_length)
            dummy_mel = torch.zeros(self.n_mels, min(self.max_mel_length, 100))
            return dummy_audio, dummy_mel


class ExtendedTTSCollate(TTSCollate):
    """
    Extended collate function for batching large audio TTS data.

    This collate function ensures that batches don't exceed memory limits
    by enforcing maximum lengths for audio and mel spectrograms.
    """

    def __init__(self, pad_value: int = 0, max_mel_length: int = 1000):
        """
        Initialize the collate function.

        Args:
            pad_value: Value to use for padding.
            max_mel_length: Maximum mel spectrogram length to allow in a batch.
        """
        super().__init__(pad_value=pad_value)
        self.max_mel_length = max_mel_length

    def __call__(self, batch: List[Dict[str, torch.Tensor]]) -> Dict[str, torch.Tensor]:
        """
        Collate a batch of TTS data.

        Args:
            batch: List of data items.

        Returns:
            Batched data.
        """
        try:
            # Filter out any problematic items
            valid_batch = []
            for item in batch:
                # Check if mel spectrogram has the correct number of channels
                if item['mels'].size(0) == 80:  # Ensure n_mels is 80
                    valid_batch.append(item)
                else:
                    print(f"Skipping item with incorrect mel dimensions: {item['mels'].size()}")

            # If no valid items, create a dummy batch
            if len(valid_batch) == 0:
                print("No valid items in batch, creating dummy batch")
                dummy_item = {
                    'phonemes': torch.zeros(10, dtype=torch.long),
                    'phoneme_lengths': torch.tensor(10, dtype=torch.long),
                    'audio': torch.zeros(16000),
                    'mels': torch.zeros(80, 100),
                    'mel_lengths': torch.tensor(100, dtype=torch.long),
                    'text': "dummy text",
                    'audio_paths': "dummy_path"
                }
                valid_batch = [dummy_item]

            # Use the valid batch instead of the original
            batch = valid_batch

            # Get batch size
            batch_size = len(batch)

            # Get maximum lengths
            max_phoneme_length = min(max(item['phoneme_lengths'].item() for item in batch), 200)
            max_mel_length = min(max(item['mel_lengths'].item() for item in batch), self.max_mel_length)
            max_audio_length = min(max(item['audio'].size(0) for item in batch), self.max_mel_length * 256)  # Approximate

            # Initialize tensors
            phonemes = torch.full(
                size=[int(batch_size), int(max_phoneme_length)],
                fill_value=self.pad_value,
                dtype=torch.long
            )
            mels = torch.zeros(
                size=[int(batch_size), 80, int(max_mel_length)]  # Hardcode n_mels=80 for safety
            )
            audio = torch.zeros(
                size=[int(batch_size), int(max_audio_length)]
            )
        except Exception as e:
            print(f"Error in collate initialization: {str(e)}")
            # Create minimal batch with safe dimensions
            batch_size = 1
            max_phoneme_length = 10
            max_mel_length = 100
            max_audio_length = 16000

            phonemes = torch.full(
                size=[batch_size, max_phoneme_length],
                fill_value=self.pad_value,
                dtype=torch.long
            )
            mels = torch.zeros(
                size=[batch_size, 80, max_mel_length]
            )
            audio = torch.zeros(
                size=[batch_size, max_audio_length]
            )

        # Fill tensors
        phoneme_lengths = []
        mel_lengths = []
        texts = []
        audio_paths = []

        try:
            for i, item in enumerate(batch):
                try:
                    phoneme_length = min(item['phoneme_lengths'].item(), max_phoneme_length)
                    mel_length = min(item['mel_lengths'].item(), max_mel_length)
                    audio_length = min(item['audio'].size(0), max_audio_length)

                    # Fill phonemes
                    phonemes[i, :phoneme_length] = item['phonemes'][:phoneme_length]

                    # Fill mels - ensure dimensions match
                    mel_data = item['mels']

                    # Make sure we don't exceed the dimensions of the target tensor
                    actual_mel_length = min(mel_length, mel_data.size(1))
                    mels[i, :, :actual_mel_length] = mel_data[:, :actual_mel_length]

                    # Fill audio
                    audio[i, :audio_length] = item['audio'][:audio_length]

                    # Add lengths
                    phoneme_lengths.append(phoneme_length)
                    mel_lengths.append(mel_length)

                    # Add text and audio path
                    texts.append(item['text'])
                    audio_paths.append(item['audio_paths'])
                except Exception as e:
                    print(f"Error processing batch item {i}: {str(e)}")
                    # Skip this item
                    continue

            # If no items were processed successfully, add a dummy item
            if len(phoneme_lengths) == 0:
                print("No items were processed successfully, adding dummy item")
                phoneme_lengths.append(10)
                mel_lengths.append(100)
                texts.append("dummy text")
                audio_paths.append("dummy_path")

                # Fill with zeros
                phonemes[0, :10] = 0
                mels[0, :, :100] = 0
                audio[0, :16000] = 0

        except Exception as e:
            print(f"Error filling tensors: {str(e)}")
            # Create minimal dummy data
            phoneme_lengths = [10]
            mel_lengths = [100]
            texts = ["dummy text"]
            audio_paths = ["dummy_path"]

        # Convert lists to tensors
        phoneme_lengths = torch.tensor(phoneme_lengths, dtype=torch.long)
        mel_lengths = torch.tensor(mel_lengths, dtype=torch.long)

        # Create output dictionary
        output = {
            'phonemes': phonemes,
            'phoneme_lengths': phoneme_lengths,
            'mels': mels,
            'mel_lengths': mel_lengths,
            'audio': audio,
            'texts': texts,
            'audio_paths': audio_paths,
        }

        return output