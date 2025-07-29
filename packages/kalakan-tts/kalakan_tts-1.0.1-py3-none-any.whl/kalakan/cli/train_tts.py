#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kalakan TTS Training CLI

This module provides a command-line interface for training TTS models
using the Kalakan framework.
"""

import os
import sys
import argparse
import logging
import yaml
import torch
import numpy as np
import random
from pathlib import Path

from kalakan.training.acoustic_trainer import AcousticTrainer
from kalakan.training.vocoder_trainer import VocoderTrainer
from kalakan.utils.audio import AudioProcessor
from kalakan.utils.data import DataProcessor
from kalakan.utils.logging import setup_logger

logger = setup_logger("KalakanTraining")

def set_seed(seed):
    """Set random seed for reproducibility."""
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic = True

def load_config(config_path):
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def prepare_output_dirs(output_dir):
    """Prepare output directories for training."""
    os.makedirs(output_dir, exist_ok=True)

    # Create subdirectories
    acoustic_dir = os.path.join(output_dir, "acoustic")
    vocoder_dir = os.path.join(output_dir, "vocoder")
    samples_dir = os.path.join(output_dir, "samples")

    os.makedirs(acoustic_dir, exist_ok=True)
    os.makedirs(vocoder_dir, exist_ok=True)
    os.makedirs(samples_dir, exist_ok=True)

    return acoustic_dir, vocoder_dir, samples_dir

def compute_mel_spectrograms(data_dir, config, output_dir):
    """Compute mel spectrograms for the dataset."""
    logger.info("Computing mel spectrograms...")

    # Initialize audio processor
    audio_processor = AudioProcessor(
        sample_rate=config['data']['sample_rate'],
        n_fft=config['data']['filter_length'],
        hop_length=config['data']['hop_length'],
        win_length=config['data']['win_length'],
        n_mels=config['model']['n_mels'],
        mel_fmin=config['data']['mel_fmin'],
        mel_fmax=config['data']['mel_fmax']
    )

    # Initialize data processor
    data_processor = DataProcessor(
        data_dir=data_dir,
        output_dir=output_dir,
        audio_processor=audio_processor
    )

    # Compute mel spectrograms
    data_processor.compute_mel_spectrograms()

    logger.info("Mel spectrogram computation complete.")

def train_acoustic_model(data_dir, acoustic_dir, config_path, resume_checkpoint=None):
    """Train the acoustic model."""
    logger.info("Starting acoustic model training...")

    # Load configuration
    config = load_config(config_path)

    # Set random seed
    set_seed(config['training']['seed'])

    # Initialize trainer
    # Create model and dataloaders
    from kalakan.utils.model_factory import ModelFactory

    # Define functions to create dataloaders
    def create_dataloaders(data_dir, config):
        """Create dataloaders for acoustic model training."""
        from torch.utils.data import DataLoader
        from kalakan.data.dataset import TTSDataset

        # Create datasets
        train_dataset = TTSDataset(
            metadata_path=os.path.join(data_dir, "train", "metadata.json"),
            root_dir=os.path.join(data_dir, "train"),
            sample_rate=config['data']['sample_rate'],
            n_mels=config['model']['n_mels'],
            hop_length=config['data']['hop_length'],
            win_length=config['data']['win_length'],
            n_fft=config['data']['filter_length']
        )
        val_dataset = TTSDataset(
            metadata_path=os.path.join(data_dir, "val", "metadata.json"),
            root_dir=os.path.join(data_dir, "val"),
            sample_rate=config['data']['sample_rate'],
            n_mels=config['model']['n_mels'],
            hop_length=config['data']['hop_length'],
            win_length=config['data']['win_length'],
            n_fft=config['data']['filter_length']
        )

        # Create dataloaders
        train_dataloader = DataLoader(
            train_dataset,
            batch_size=config['training']['batch_size'],
            shuffle=True,
            num_workers=config['training'].get('num_workers', 4),
            pin_memory=True,
            drop_last=True
        )

        val_dataloader = DataLoader(
            val_dataset,
            batch_size=config['training']['batch_size'],
            shuffle=False,
            num_workers=config['training'].get('num_workers', 4),
            pin_memory=True
        )

        return train_dataloader, val_dataloader

    model = ModelFactory.create_acoustic_model(config=config)
    train_dataloader, val_dataloader = create_dataloaders(data_dir, config)

    trainer = AcousticTrainer(
        config=config,
        model=model,
        train_dataloader=train_dataloader,
        val_dataloader=val_dataloader,
        output_dir=acoustic_dir
    )

    # Load checkpoint if provided
    if resume_checkpoint:
        trainer.load_checkpoint(resume_checkpoint)

    # Train the model
    trainer.train()

    logger.info("Acoustic model training complete.")

    return os.path.join(acoustic_dir, "best_model.pt")

def train_vocoder(data_dir, vocoder_dir, config_path, resume_checkpoint=None):
    """Train the vocoder model."""
    logger.info("Starting vocoder training...")

    # Load configuration
    config = load_config(config_path)

    # Set random seed
    set_seed(config['training']['seed'])

    # Initialize trainer
    # Create model and dataloaders
    from kalakan.utils.model_factory import ModelFactory

    # Define function to create vocoder dataloaders
    def create_vocoder_dataloaders(data_dir, config):
        """Create dataloaders for vocoder training."""
        from torch.utils.data import DataLoader
        from kalakan.data.dataset import VocoderDataset

        # Create datasets
        train_dataset = VocoderDataset(
            metadata_path=os.path.join(data_dir, "train", "metadata.json"),
            root_dir=os.path.join(data_dir, "train"),
            sample_rate=config['data']['sample_rate'],
            n_mels=config['model']['n_mels'],
            hop_length=config['data']['hop_length'],
            win_length=config['data']['win_length'],
            n_fft=config['data']['filter_length'],
            segment_length=config['training'].get('segment_length', 8192)
        )
        val_dataset = VocoderDataset(
            metadata_path=os.path.join(data_dir, "val", "metadata.json"),
            root_dir=os.path.join(data_dir, "val"),
            sample_rate=config['data']['sample_rate'],
            n_mels=config['model']['n_mels'],
            hop_length=config['data']['hop_length'],
            win_length=config['data']['win_length'],
            n_fft=config['data']['filter_length'],
            segment_length=config['training'].get('segment_length', 8192)
        )

        # Create dataloaders
        train_dataloader = DataLoader(
            train_dataset,
            batch_size=config['training']['batch_size'],
            shuffle=True,
            num_workers=config['training'].get('num_workers', 4),
            pin_memory=True,
            drop_last=True,
            collate_fn=VocoderDataset.collate_fn
        )

        val_dataloader = DataLoader(
            val_dataset,
            batch_size=config['training']['batch_size'],
            shuffle=False,
            num_workers=config['training'].get('num_workers', 4),
            pin_memory=True,
            collate_fn=VocoderDataset.collate_fn
        )

        return train_dataloader, val_dataloader

    model = ModelFactory.create_vocoder(config=config)
    train_dataloader, val_dataloader = create_vocoder_dataloaders(data_dir, config)

    trainer = VocoderTrainer(
        config=config,
        model=model,
        train_dataloader=train_dataloader,
        val_dataloader=val_dataloader,
        output_dir=vocoder_dir
    )

    # Load checkpoint if provided
    if resume_checkpoint:
        trainer.load_checkpoint(resume_checkpoint)

    # Train the model
    trainer.train()

    logger.info("Vocoder training complete.")

    return os.path.join(vocoder_dir, "best_model.pt")

def generate_samples(acoustic_model_path, vocoder_model_path, samples_dir, test_sentences):
    """Generate audio samples using the trained models."""
    logger.info("Generating audio samples...")

    # Import synthesis module
    from kalakan.synthesis.synthesizer import Synthesizer

    # Initialize synthesizer
    synthesizer = Synthesizer(
        acoustic_model=acoustic_model_path,
        vocoder=vocoder_model_path
    )

    # Generate samples
    for i, text in enumerate(test_sentences):
        output_path = os.path.join(samples_dir, f"sample_{i+1}.wav")
        audio = synthesizer.synthesize(text)
        synthesizer.save_audio(audio, output_path)
        logger.info(f"Generated sample: {output_path}")

    logger.info("Sample generation complete.")

def main():
    parser = argparse.ArgumentParser(description="Train a TTS model using Kalakan")
    parser.add_argument("--data-dir", required=True, help="Directory containing processed dataset")
    parser.add_argument("--output-dir", required=True, help="Directory to save trained models")
    parser.add_argument("--acoustic-config", required=True, help="Path to acoustic model training configuration")
    parser.add_argument("--vocoder-config", required=True, help="Path to vocoder training configuration")
    parser.add_argument("--resume-acoustic", help="Path to acoustic model checkpoint to resume training")
    parser.add_argument("--resume-vocoder", help="Path to vocoder checkpoint to resume training")
    parser.add_argument("--skip-acoustic", action="store_true", help="Skip acoustic model training")
    parser.add_argument("--skip-vocoder", action="store_true", help="Skip vocoder training")
    parser.add_argument("--skip-mel-computation", action="store_true", help="Skip mel spectrogram computation")
    parser.add_argument("--test-sentences", help="Path to file containing test sentences")
    args = parser.parse_args()

    # Prepare output directories
    acoustic_dir, vocoder_dir, samples_dir = prepare_output_dirs(args.output_dir)

    # Load acoustic configuration
    acoustic_config = load_config(args.acoustic_config)

    # Compute mel spectrograms if needed
    if not args.skip_mel_computation:
        compute_mel_spectrograms(args.data_dir, acoustic_config, args.data_dir)

    # Train acoustic model if not skipped
    acoustic_model_path = None
    if not args.skip_acoustic:
        acoustic_model_path = train_acoustic_model(
            args.data_dir,
            acoustic_dir,
            args.acoustic_config,
            args.resume_acoustic
        )
    else:
        logger.info("Skipping acoustic model training.")
        if args.resume_acoustic:
            acoustic_model_path = args.resume_acoustic

    # Train vocoder if not skipped
    vocoder_model_path = None
    if not args.skip_vocoder:
        vocoder_model_path = train_vocoder(
            args.data_dir,
            vocoder_dir,
            args.vocoder_config,
            args.resume_vocoder
        )
    else:
        logger.info("Skipping vocoder training.")
        if args.resume_vocoder:
            vocoder_model_path = args.resume_vocoder

    # Generate samples if both models are available
    if acoustic_model_path and vocoder_model_path:
        # Load test sentences
        test_sentences = []
        if args.test_sentences:
            with open(args.test_sentences, 'r', encoding='utf-8') as f:
                test_sentences = [line.strip() for line in f if line.strip()]

        # Use default test sentences if none provided
        if not test_sentences:
            test_sentences = [
                "Hello, this is a test sentence for the Kalakan TTS system.",
                "The quick brown fox jumps over the lazy dog.",
                "Kalakan is a powerful text-to-speech framework.",
            ]

        generate_samples(acoustic_model_path, vocoder_model_path, samples_dir, test_sentences)

    logger.info(f"Training complete. Models saved to {args.output_dir}")

if __name__ == "__main__":
    main()