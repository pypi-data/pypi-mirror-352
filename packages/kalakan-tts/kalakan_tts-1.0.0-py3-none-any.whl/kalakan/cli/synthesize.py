"""
Command-line interface for speech synthesis.

This module provides a command-line interface for synthesizing speech
using Kalakan TTS.
"""

import argparse
import os
import sys
from typing import List, Optional

from kalakan.synthesis.synthesizer import Synthesizer
from kalakan.utils.logging import setup_logger


def add_synthesize_args(parser):
    """Add synthesize arguments to the parser."""
    # Input arguments
    parser.add_argument("text", type=str, nargs="?", default=None,
                        help="Text to synthesize")
    parser.add_argument("--file", "-f", type=str, default=None,
                        help="File containing text to synthesize (one sentence per line)")

    # Model arguments
    parser.add_argument("--acoustic_model", "-a", type=str, default=None,
                        help="Path to acoustic model checkpoint")
    parser.add_argument("--vocoder", "-v", type=str, default=None,
                        help="Path to vocoder checkpoint")

    # Output arguments
    parser.add_argument("--output", "-o", type=str, default="output.wav",
                        help="Path to save synthesized audio")
    parser.add_argument("--output_dir", "-d", type=str, default=None,
                        help="Directory to save synthesized audio (for batch synthesis)")

    # Synthesis arguments
    parser.add_argument("--sample_rate", "-sr", type=int, default=22050,
                        help="Audio sample rate")
    parser.add_argument("--normalize", "-n", action="store_true",
                        help="Normalize text before synthesis")
    parser.add_argument("--clean", "-c", action="store_true",
                        help="Clean text before synthesis")

    # Device arguments
    parser.add_argument("--device", type=str, default=None,
                        help="Device to use for synthesis (e.g., 'cuda:0', 'cpu')")


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Synthesize speech using Kalakan TTS")
    add_synthesize_args(parser)
    return parser.parse_args()


def read_text_file(file_path: str) -> List[str]:
    """
    Read text from a file, one sentence per line.

    Args:
        file_path: Path to the text file.

    Returns:
        List of sentences.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Remove empty lines and strip whitespace
    lines = [line.strip() for line in lines if line.strip()]

    return lines


def main(args=None):
    """Main function."""
    # Parse arguments if not provided
    if args is None:
        args = parse_args()

    # Set up logger
    logger = setup_logger("synthesize")

    # Check input
    if args.text is None and args.file is None:
        logger.error("Either text or --file must be provided")
        sys.exit(1)

    # Create output directory if needed
    if args.output_dir is not None:
        os.makedirs(args.output_dir, exist_ok=True)

    # Create synthesizer
    logger.info("Creating synthesizer...")
    synthesizer = Synthesizer(
        acoustic_model=args.acoustic_model,
        vocoder=args.vocoder,
        device=args.device,
    )

    # Get text to synthesize
    texts = []
    if args.text is not None:
        texts.append(args.text)
    if args.file is not None:
        texts.extend(read_text_file(args.file))

    # Synthesize speech
    logger.info("Synthesizing speech...")
    for i, text in enumerate(texts):
        # Determine output filename
        if args.output_dir is not None:
            output_file = os.path.join(args.output_dir, f"synthesized_{i+1}.wav")
        else:
            output_file = args.output

        # Synthesize and save
        logger.info(f"Synthesizing: {text}")
        synthesizer.text_to_speech(
            text=text,
            output_file=output_file,
            normalize=args.normalize,
            clean=args.clean,
            sample_rate=args.sample_rate,
        )
        logger.info(f"Saved to: {output_file}")

    logger.info("Synthesis complete!")


if __name__ == "__main__":
    main()