"""
Data processing utilities for Kalakan TTS.

This module provides data processing functionality for the Kalakan TTS system,
including dataset preparation, mel-spectrogram computation, and data augmentation.
"""

import os
import json
import csv
import logging
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any

import numpy as np
import torch
import tqdm
import pandas as pd
import librosa
from concurrent.futures import ProcessPoolExecutor, as_completed

from kalakan.utils.audio import AudioProcessor


class DataProcessor:
    """
    Data processor for Kalakan TTS.

    This class provides methods for processing TTS datasets, including
    mel-spectrogram computation, data augmentation, and dataset splitting.
    """

    def __init__(
        self,
        data_dir: str,
        output_dir: Optional[str] = None,
        audio_processor: Optional[AudioProcessor] = None,
        num_workers: int = 4,
        metadata_filename: str = "metadata.csv",
    ):
        """
        Initialize the data processor.

        Args:
            data_dir: Directory containing the dataset.
            output_dir: Directory to save processed data. If None, uses data_dir.
            audio_processor: Audio processor instance. If None, creates a default one.
            num_workers: Number of workers for parallel processing.
            metadata_filename: Name of the metadata file.
        """
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir) if output_dir is not None else self.data_dir
        self.audio_processor = audio_processor if audio_processor is not None else AudioProcessor()
        self.num_workers = num_workers
        self.metadata_filename = metadata_filename

        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.output_dir / "mels", exist_ok=True)

        # Set up logging
        self.logger = logging.getLogger("DataProcessor")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def load_metadata(self) -> pd.DataFrame:
        """
        Load metadata from CSV or JSON file.

        Returns:
            DataFrame containing metadata.
        """
        # Check for CSV metadata
        csv_path = self.data_dir / self.metadata_filename
        if csv_path.exists():
            self.logger.info(f"Loading metadata from {csv_path}")
            return pd.read_csv(csv_path, sep='|')

        # Check for JSON metadata
        json_path = self.data_dir / "metadata.json"
        if json_path.exists():
            self.logger.info(f"Loading metadata from {json_path}")
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return pd.DataFrame(data)

        # Check for train.csv
        train_csv_path = self.data_dir / "train.csv"
        if train_csv_path.exists():
            self.logger.info(f"Loading metadata from {train_csv_path}")
            return pd.read_csv(train_csv_path, sep='|')

        # Check for train.json
        train_json_path = self.data_dir / "train.json"
        if train_json_path.exists():
            self.logger.info(f"Loading metadata from {train_json_path}")
            with open(train_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return pd.DataFrame(data)

        raise FileNotFoundError(f"No metadata file found in {self.data_dir}")

    def compute_mel_spectrograms(self) -> None:
        """
        Compute mel spectrograms for all audio files in the dataset.

        This method loads the metadata, computes mel spectrograms for all audio files,
        and saves them to disk.
        """
        self.logger.info("Computing mel spectrograms...")

        # Load metadata
        metadata = self.load_metadata()

        # Get audio paths
        audio_paths = []
        for _, row in metadata.iterrows():
            if 'audio_path' in row:
                audio_path = row['audio_path']
                if not os.path.isabs(audio_path):
                    audio_path = os.path.join(self.data_dir, audio_path)
                audio_paths.append(audio_path)

        self.logger.info(f"Found {len(audio_paths)} audio files")

        # Compute mel spectrograms in parallel
        with ProcessPoolExecutor(max_workers=self.num_workers) as executor:
            futures = []
            for audio_path in audio_paths:
                future = executor.submit(self._compute_and_save_mel, audio_path)
                futures.append(future)

            # Process results
            for i, future in enumerate(tqdm.tqdm(as_completed(futures), total=len(futures), desc="Computing mels")):
                try:
                    future.result()
                except Exception as e:
                    self.logger.error(f"Error computing mel spectrogram: {str(e)}")

        self.logger.info("Mel spectrogram computation complete")

    def _compute_and_save_mel(self, audio_path: str) -> None:
        """
        Compute and save mel spectrogram for a single audio file.

        Args:
            audio_path: Path to the audio file.
        """
        try:
            # Get output path
            filename = os.path.basename(audio_path)
            base_name = os.path.splitext(filename)[0]
            output_path = os.path.join(self.output_dir, "mels", f"{base_name}.npy")

            # Skip if already computed
            if os.path.exists(output_path):
                return

            # Compute mel spectrogram
            mel = self.audio_processor.extract_mel_from_file(audio_path, return_tensor=False)

            # Save mel spectrogram
            np.save(output_path, mel)

        except Exception as e:
            self.logger.error(f"Error processing {audio_path}: {str(e)}")
            raise

    def split_dataset(
        self,
        train_ratio: float = 0.8,
        val_ratio: float = 0.1,
        test_ratio: float = 0.1,
        random_seed: int = 42,
    ) -> None:
        """
        Split the dataset into training, validation, and test sets.

        Args:
            train_ratio: Ratio of training data.
            val_ratio: Ratio of validation data.
            test_ratio: Ratio of test data.
            random_seed: Random seed for reproducibility.
        """
        self.logger.info("Splitting dataset...")

        # Load metadata
        metadata = self.load_metadata()

        # Set random seed
        random.seed(random_seed)

        # Shuffle data
        indices = list(range(len(metadata)))
        random.shuffle(indices)

        # Calculate split indices
        train_end = int(len(indices) * train_ratio)
        val_end = train_end + int(len(indices) * val_ratio)

        # Split data
        train_indices = indices[:train_end]
        val_indices = indices[train_end:val_end]
        test_indices = indices[val_end:]

        # Create split datasets
        train_data = metadata.iloc[train_indices].reset_index(drop=True)
        val_data = metadata.iloc[val_indices].reset_index(drop=True)
        test_data = metadata.iloc[test_indices].reset_index(drop=True)

        # Save split datasets
        os.makedirs(self.output_dir / "splits", exist_ok=True)

        # Save as CSV
        train_data.to_csv(self.output_dir / "splits" / "train.csv", sep='|', index=False)
        val_data.to_csv(self.output_dir / "splits" / "val.csv", sep='|', index=False)
        test_data.to_csv(self.output_dir / "splits" / "test.csv", sep='|', index=False)

        # Save as JSON
        train_data_dict = train_data.to_dict('records')
        val_data_dict = val_data.to_dict('records')
        test_data_dict = test_data.to_dict('records')

        with open(self.output_dir / "splits" / "train.json", 'w', encoding='utf-8') as f:
            json.dump(train_data_dict, f, ensure_ascii=False, indent=2)

        with open(self.output_dir / "splits" / "val.json", 'w', encoding='utf-8') as f:
            json.dump(val_data_dict, f, ensure_ascii=False, indent=2)

        with open(self.output_dir / "splits" / "test.json", 'w', encoding='utf-8') as f:
            json.dump(test_data_dict, f, ensure_ascii=False, indent=2)

        self.logger.info(f"Dataset split complete: train={len(train_data)}, val={len(val_data)}, test={len(test_data)}")

    def augment_data(
        self,
        pitch_shift_range: Optional[Tuple[float, float]] = None,
        tempo_range: Optional[Tuple[float, float]] = None,
        noise_level: Optional[float] = None,
        augmentation_factor: int = 1,
        random_seed: int = 42,
    ) -> None:
        """
        Augment the dataset with pitch shifting, time stretching, and noise.

        Args:
            pitch_shift_range: Range of pitch shifting in semitones (min, max).
            tempo_range: Range of tempo adjustment (min, max).
            noise_level: Level of white noise to add (0.0 to 1.0).
            augmentation_factor: Number of augmented samples to generate per original sample.
            random_seed: Random seed for reproducibility.
        """
        self.logger.info("Augmenting dataset...")

        # Load metadata
        metadata = self.load_metadata()

        # Set random seed
        random.seed(random_seed)
        np.random.seed(random_seed)

        # Create output directory
        os.makedirs(self.output_dir / "augmented" / "wavs", exist_ok=True)

        # Augment data
        augmented_metadata = []

        for _, row in tqdm.tqdm(metadata.iterrows(), total=len(metadata), desc="Augmenting data"):
            # Get audio path
            audio_path = row['audio_path']
            if not os.path.isabs(audio_path):
                audio_path = os.path.join(self.data_dir, audio_path)

            # Load audio
            audio = self.audio_processor.load_audio(
                file_path=audio_path,
                target_sr=self.audio_processor.sample_rate,
                mono=True,
                normalize=True,
                return_tensor=False,
            )

            # Create augmented samples
            for i in range(augmentation_factor):
                # Apply augmentations
                # Create a copy of the audio array
                if isinstance(audio, np.ndarray):
                    augmented_audio = audio.copy()
                else:
                    augmented_audio = audio.clone().numpy() if isinstance(audio, torch.Tensor) else np.array(audio)

                # Apply pitch shifting
                if pitch_shift_range is not None:
                    pitch_shift = random.uniform(pitch_shift_range[0], pitch_shift_range[1])
                    augmented_audio = librosa.effects.pitch_shift(
                        augmented_audio,
                        sr=self.audio_processor.sample_rate,
                        n_steps=pitch_shift,
                    )

                # Apply time stretching
                if tempo_range is not None:
                    tempo = random.uniform(tempo_range[0], tempo_range[1])
                    augmented_audio = librosa.effects.time_stretch(
                        augmented_audio,
                        rate=tempo,
                    )

                # Apply noise
                if noise_level is not None:
                    noise = np.random.randn(*augmented_audio.shape) * noise_level
                    augmented_audio = augmented_audio + noise
                    augmented_audio = np.clip(augmented_audio, -1.0, 1.0)

                # Save augmented audio
                filename = os.path.basename(audio_path)
                base_name = os.path.splitext(filename)[0]
                output_path = os.path.join(self.output_dir, "augmented", "wavs", f"{base_name}_aug_{i+1}.wav")

                self.audio_processor.save_audio(
                    audio=augmented_audio,
                    file_path=output_path,
                    sample_rate=self.audio_processor.sample_rate,
                    normalize=True,
                )

                # Create metadata entry
                augmented_row = row.copy()
                augmented_row['audio_path'] = os.path.join("augmented", "wavs", f"{base_name}_aug_{i+1}.wav")
                augmented_row['id'] = f"{base_name}_aug_{i+1}"
                augmented_metadata.append(augmented_row)

        # Combine original and augmented metadata
        combined_metadata = pd.concat([metadata, pd.DataFrame(augmented_metadata)], ignore_index=True)

        # Save combined metadata
        combined_metadata.to_csv(self.output_dir / "augmented" / "metadata.csv", sep='|', index=False)
        combined_metadata.to_dict('records')

        with open(self.output_dir / "augmented" / "metadata.json", 'w', encoding='utf-8') as f:
            json.dump(combined_metadata.to_dict('records'), f, ensure_ascii=False, indent=2)

        self.logger.info(f"Data augmentation complete: original={len(metadata)}, augmented={len(augmented_metadata)}, total={len(combined_metadata)}")

    def analyze_dataset(self) -> Dict[str, Any]:
        """
        Analyze the dataset and return statistics.

        Returns:
            Dictionary containing dataset statistics.
        """
        self.logger.info("Analyzing dataset...")

        # Load metadata
        metadata = self.load_metadata()

        # Calculate statistics
        stats = {
            "num_samples": len(metadata),
            "total_duration": 0.0,
            "min_duration": float('inf'),
            "max_duration": 0.0,
            "avg_duration": 0.0,
            "num_speakers": 0,
            "num_unique_texts": 0,
        }

        # Calculate duration statistics
        if 'duration' in metadata.columns:
            durations = metadata['duration'].to_numpy()  # Convert to numpy array
            stats["total_duration"] = float(durations.sum())
            stats["min_duration"] = float(durations.min())
            stats["max_duration"] = float(durations.max())
            stats["avg_duration"] = float(durations.mean())

        # Calculate speaker statistics
        if 'speaker_id' in metadata.columns:
            stats["num_speakers"] = len(metadata['speaker_id'].unique())
            stats["speakers"] = metadata['speaker_id'].value_counts().to_dict()

        # Calculate text statistics
        if 'text' in metadata.columns:
            stats["num_unique_texts"] = len(metadata['text'].unique())
            stats["avg_text_length"] = float(metadata['text'].str.len().mean())
            stats["min_text_length"] = int(metadata['text'].str.len().min())
            stats["max_text_length"] = int(metadata['text'].str.len().max())

        # Save statistics
        with open(self.output_dir / "dataset_stats.json", 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)

        self.logger.info(f"Dataset analysis complete: {stats['num_samples']} samples, {stats['total_duration']:.2f} seconds total")

        return stats