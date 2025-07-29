"""
Demo CLI for Kalakan TTS.

This module provides a command-line interface for demonstrating Kalakan TTS.
"""

import argparse
import os
import sys
from typing import Optional

import torch

from kalakan.synthesis.synthesizer import Synthesizer
from kalakan.utils.device import get_device
from kalakan.utils.logging import setup_logger


def add_demo_args(parser):
    """Add demo arguments to the parser."""
    # Input arguments
    parser.add_argument("--text", "-t", type=str, required=True,
                        help="Text to synthesize")
    parser.add_argument("--output", "-o", type=str, default="output.wav",
                        help="Output audio file")

    # Model arguments
    parser.add_argument("--acoustic_model", "-a", type=str, default=None,
                        help="Path to acoustic model checkpoint or model name")
    parser.add_argument("--vocoder", "-v", type=str, default=None,
                        help="Path to vocoder checkpoint or model name")

    # Text processing arguments
    parser.add_argument("--normalize", action="store_true",
                        help="Normalize text before synthesis")
    parser.add_argument("--clean", action="store_true",
                        help="Clean text before synthesis")

    # Device arguments
    parser.add_argument("--device", type=str, default=None,
                        help="Device to use for inference (e.g., 'cuda:0', 'cpu')")

    # Synthesis arguments
    parser.add_argument("--speed", type=float, default=1.0,
                        help="Speech speed factor (1.0 = normal speed)")
    parser.add_argument("--pitch", type=float, default=1.0,
                        help="Pitch factor (1.0 = normal pitch)")
    parser.add_argument("--energy", type=float, default=1.0,
                        help="Energy factor (1.0 = normal energy)")


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Kalakan TTS Demo")
    add_demo_args(parser)
    return parser.parse_args()


def main(args=None):
    """Main function."""
    # Parse arguments if not provided
    if args is None:
        args = parse_args()

    # Set up logger
    logger = setup_logger("demo")

    # Create synthesizer
    logger.info("Creating synthesizer...")

    # Get environment variables if not provided
    acoustic_model = args.acoustic_model
    if acoustic_model is None:
        acoustic_model = os.environ.get("KALAKAN_ACOUSTIC_MODEL")
        if acoustic_model is None:
            logger.error("No acoustic model specified. Use --acoustic_model or set KALAKAN_ACOUSTIC_MODEL environment variable.")
            sys.exit(1)

    vocoder = args.vocoder
    if vocoder is None:
        vocoder = os.environ.get("KALAKAN_VOCODER")
        if vocoder is None:
            logger.error("No vocoder specified. Use --vocoder or set KALAKAN_VOCODER environment variable.")
            sys.exit(1)

    device = get_device(args.device)

    # Create synthesizer
    synthesizer = Synthesizer(
        acoustic_model=acoustic_model,
        vocoder=vocoder,
        device=device,
    )

    # Synthesize speech
    logger.info(f"Synthesizing: {args.text}")
    audio = synthesizer.synthesize(
        text=args.text,
        normalize=args.normalize,
        clean=args.clean,
        speed=args.speed,
        pitch=args.pitch,
        energy=args.energy,
    )

    # Save audio
    logger.info(f"Saving audio to: {args.output}")
    synthesizer.save_audio(audio, args.output)

    logger.info("Done!")


if __name__ == "__main__":
    main()