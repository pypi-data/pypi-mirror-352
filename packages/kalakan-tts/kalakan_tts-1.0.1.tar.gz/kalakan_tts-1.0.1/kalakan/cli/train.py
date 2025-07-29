"""
Command-line interface for model training.

This module provides a command-line interface for training models
using Kalakan TTS.
"""

import argparse
import os
import random
import sys
from typing import Dict, Optional

import numpy as np
import torch
import yaml

from kalakan.data.dataset import TTSDataset, TTSCollate
from kalakan.models.acoustic.tacotron2 import Tacotron2
from kalakan.models.vocoders.griffin_lim import GriffinLim
from kalakan.training.acoustic_trainer import AcousticTrainer
from kalakan.training.vocoder_trainer import VocoderTrainer
from kalakan.utils.config import Config
from kalakan.utils.device import get_device
from kalakan.utils.logging import setup_logger


def add_train_args(parser):
    """Add train arguments to the parser."""
    # Model type
    parser.add_argument("--model_type", "-t", type=str, required=True, choices=["acoustic", "vocoder"],
                        help="Type of model to train")

    # Data arguments
    parser.add_argument("--train_metadata", type=str, required=True,
                        help="Path to training metadata file")
    parser.add_argument("--val_metadata", type=str, default=None,
                        help="Path to validation metadata file")
    parser.add_argument("--audio_dir", type=str, default=None,
                        help="Root directory for audio files")

    # Model arguments
    parser.add_argument("--model_config", "-c", type=str, required=True,
                        help="Path to model configuration file")

    # Training arguments
    parser.add_argument("--training_config", type=str, required=True,
                        help="Path to training configuration file")
    parser.add_argument("--output_dir", "-o", type=str, default="models",
                        help="Directory to save model checkpoints")
    parser.add_argument("--experiment_name", "-n", type=str, default=None,
                        help="Name of the experiment")
    parser.add_argument("--checkpoint", type=str, default=None,
                        help="Path to checkpoint to resume training from")

    # Device arguments
    parser.add_argument("--device", type=str, default=None,
                        help="Device to use for training (e.g., 'cuda:0', 'cpu')")

    # Other arguments
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed")


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Train models for Kalakan TTS")
    add_train_args(parser)
    return parser.parse_args()


def load_config(config_path: str) -> Dict:
    """
    Load configuration from a YAML file.

    Args:
        config_path: Path to the configuration file.

    Returns:
        Configuration dictionary.
    """
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    return config


def set_seed(seed: int) -> None:
    """
    Set random seed for reproducibility.

    Args:
        seed: Random seed.
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def train_acoustic_model(args, logger):
    """
    Train an acoustic model.

    Args:
        args: Command-line arguments.
        logger: Logger instance.
    """
    # Load configurations
    model_config = Config(load_config(args.model_config))
    training_config = Config(load_config(args.training_config))

    # Set device
    device = get_device(args.device)
    logger.info(f"Using device: {device}")

    # Create datasets
    logger.info("Creating datasets...")
    train_dataset = TTSDataset(
        metadata_path=args.train_metadata,
        root_dir=args.audio_dir,
        sample_rate=22050,
        n_mels=model_config.get("model.n_mels", 80),
        hop_length=256,
        win_length=1024,
        n_fft=1024,
        clean_text_flag=True,
        normalize_text_flag=True,
    )

    val_dataset = None
    if args.val_metadata is not None:
        val_dataset = TTSDataset(
            metadata_path=args.val_metadata,
            root_dir=args.audio_dir,
            sample_rate=22050,
            n_mels=model_config.get("model.n_mels", 80),
            hop_length=256,
            win_length=1024,
            n_fft=1024,
            clean_text_flag=True,
            normalize_text_flag=True,
        )

    # Create data loaders
    logger.info("Creating data loaders...")
    collate_fn = TTSCollate()

    train_loader = torch.utils.data.DataLoader(
        train_dataset,
        batch_size=training_config.get("training.batch_size", 32),
        shuffle=True,
        collate_fn=collate_fn,
        num_workers=4,
        pin_memory=True,
        drop_last=True,
    )

    val_loader = None
    if val_dataset is not None:
        val_loader = torch.utils.data.DataLoader(
            val_dataset,
            batch_size=training_config.get("training.batch_size", 32),
            shuffle=False,
            collate_fn=collate_fn,
            num_workers=4,
            pin_memory=True,
        )

    # Create model
    logger.info("Creating model...")
    model = Tacotron2(
        embedding_dim=model_config.get("model.embedding_dim", 512),
        encoder_dim=model_config.get("model.encoder_dim", 512),
        encoder_conv_layers=model_config.get("model.encoder_conv_layers", 3),
        encoder_conv_kernel_size=model_config.get("model.encoder_conv_kernel_size", 5),
        encoder_conv_dropout=model_config.get("model.encoder_conv_dropout", 0.5),
        encoder_lstm_layers=model_config.get("model.encoder_lstm_layers", 1),
        encoder_lstm_dropout=model_config.get("model.encoder_lstm_dropout", 0.1),
        decoder_dim=model_config.get("model.decoder_dim", 1024),
        decoder_prenet_dim=model_config.get("model.decoder_prenet_dim", [256, 256]),
        decoder_lstm_layers=model_config.get("model.decoder_lstm_layers", 2),
        decoder_lstm_dropout=model_config.get("model.decoder_lstm_dropout", 0.1),
        decoder_zoneout=model_config.get("model.decoder_zoneout", 0.1),
        attention_dim=model_config.get("model.attention_dim", 128),
        attention_location_features_dim=model_config.get("model.attention_location_features_dim", 32),
        attention_location_kernel_size=model_config.get("model.attention_location_kernel_size", 31),
        postnet_dim=model_config.get("model.postnet_dim", 512),
        postnet_kernel_size=model_config.get("model.postnet_kernel_size", 5),
        postnet_layers=model_config.get("model.postnet_layers", 5),
        postnet_dropout=model_config.get("model.postnet_dropout", 0.5),
        n_mels=model_config.get("model.n_mels", 80),
        stop_threshold=model_config.get("model.stop_threshold", 0.5),
    )

    # Create trainer
    logger.info("Creating trainer...")
    trainer = AcousticTrainer(
        model=model,
        train_dataloader=train_loader,
        val_dataloader=val_loader,
        config=training_config,
        device=device,
        output_dir=args.output_dir,
        experiment_name=args.experiment_name,
    )

    # Load checkpoint if provided
    if args.checkpoint is not None:
        logger.info(f"Loading checkpoint: {args.checkpoint}")
        trainer.load_checkpoint(args.checkpoint)

    # Train model
    logger.info("Starting training...")
    trainer.train()

    logger.info("Training complete!")


def train_vocoder_model(args, logger):
    """
    Train a vocoder model.

    Args:
        args: Command-line arguments.
        logger: Logger instance.
    """
    # Load configurations
    model_config = Config(load_config(args.model_config))
    training_config = Config(load_config(args.training_config))

    # Set device
    device = get_device(args.device)
    logger.info(f"Using device: {device}")

    # Create datasets
    logger.info("Creating datasets...")
    train_dataset = TTSDataset(
        metadata_path=args.train_metadata,
        root_dir=args.audio_dir,
        sample_rate=22050,
        n_mels=model_config.get("model.n_mels", 80),
        hop_length=256,
        win_length=1024,
        n_fft=1024,
        clean_text_flag=True,
        normalize_text_flag=True,
    )

    val_dataset = None
    if args.val_metadata is not None:
        val_dataset = TTSDataset(
            metadata_path=args.val_metadata,
            root_dir=args.audio_dir,
            sample_rate=22050,
            n_mels=model_config.get("model.n_mels", 80),
            hop_length=256,
            win_length=1024,
            n_fft=1024,
            clean_text_flag=True,
            normalize_text_flag=True,
        )

    # Create data loaders
    logger.info("Creating data loaders...")
    collate_fn = TTSCollate()

    train_loader = torch.utils.data.DataLoader(
        train_dataset,
        batch_size=training_config.get("training.batch_size", 16),
        shuffle=True,
        collate_fn=collate_fn,
        num_workers=4,
        pin_memory=True,
        drop_last=True,
    )

    val_loader = None
    if val_dataset is not None:
        val_loader = torch.utils.data.DataLoader(
            val_dataset,
            batch_size=training_config.get("training.batch_size", 16),
            shuffle=False,
            collate_fn=collate_fn,
            num_workers=4,
            pin_memory=True,
        )

    # Create model
    logger.info("Creating model...")
    model = GriffinLim(
        n_mels=model_config.get("model.n_mels", 80),
        sample_rate=model_config.get("model.sample_rate", 22050),
        n_fft=model_config.get("model.n_fft", 1024),
        hop_length=model_config.get("model.hop_length", 256),
        win_length=model_config.get("model.win_length", 1024),
        power=model_config.get("model.power", 1.0),
        n_iter=model_config.get("model.n_iter", 60),
        momentum=model_config.get("model.momentum", 0.99),
        mel_fmin=model_config.get("model.mel_fmin", 0.0),
        mel_fmax=model_config.get("model.mel_fmax", 8000.0),
        normalized=model_config.get("model.normalized", True),
    )

    # Create trainer
    logger.info("Creating trainer...")
    trainer = VocoderTrainer(
        model=model,
        train_dataloader=train_loader,
        val_dataloader=val_loader,
        config=training_config,
        device=device,
        output_dir=args.output_dir,
        experiment_name=args.experiment_name,
    )

    # Load checkpoint if provided
    if args.checkpoint is not None:
        logger.info(f"Loading checkpoint: {args.checkpoint}")
        trainer.load_checkpoint(args.checkpoint)

    # Train model
    logger.info("Starting training...")
    trainer.train()

    logger.info("Training complete!")


def main(args=None):
    """Main function."""
    # Parse arguments if not provided
    if args is None:
        args = parse_args()

    # Set up logger
    logger = setup_logger("train")

    # Set random seed
    if args.seed is not None:
        set_seed(args.seed)

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Train model based on type
    if args.model_type == "acoustic":
        train_acoustic_model(args, logger)
    elif args.model_type == "vocoder":
        train_vocoder_model(args, logger)
    else:
        logger.error(f"Unsupported model type: {args.model_type}")
        sys.exit(1)


if __name__ == "__main__":
    main()