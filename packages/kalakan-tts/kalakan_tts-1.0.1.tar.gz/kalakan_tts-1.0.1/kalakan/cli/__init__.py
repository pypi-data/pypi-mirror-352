"""
Command-line interface for Kalakan TTS.
This package provides command-line interfaces for Kalakan TTS,
including synthesis, training, evaluation, demo, and API.
"""

import argparse
import sys

from kalakan.cli.synthesize import main as synthesize
from kalakan.cli.train import main as train
from kalakan.cli.demo import main as demo
from kalakan.cli.api import main as api
from kalakan.cli.norm import main as norm
from kalakan.cli.gen_metadata import main as gen_metadata
from kalakan.cli.train_tts import main as train_tts
from kalakan.cli.evaluate_tts import main as evaluate_tts
from kalakan.cli.train_extended import main as train_extended

__all__ = [
    "synthesize",
    "train",
    "demo",
    "api",
    "norm",
    "gen_metadata",
    "train_tts",
    "evaluate_tts",
    "train_extended",
    "main",
]

def main():
    #Main entry point for the Kalakan CLI.
    parser = argparse.ArgumentParser(
        description="Kalakan TTS - Text-to-Speech system for the Twi language"
    )

    parser.add_argument(
        "-V", "--version",
        action="store_true",
        help="Show version information and exit"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Synthesize command
    synth_parser = subparsers.add_parser("synthesize", help="Synthesize speech from text")
    from kalakan.cli.synthesize import add_synthesize_args
    add_synthesize_args(synth_parser)
    synth_parser.set_defaults(func=synthesize)

    # Train command
    train_parser = subparsers.add_parser("train", help="Train a TTS model")
    from kalakan.cli.train import add_train_args
    add_train_args(train_parser)
    train_parser.set_defaults(func=train)

    # Demo command
    demo_parser = subparsers.add_parser("demo", help="Run the interactive demo")
    from kalakan.cli.demo import add_demo_args
    add_demo_args(demo_parser)
    demo_parser.set_defaults(func=demo)

    # API command
    api_parser = subparsers.add_parser("api", help="Start the API server")
    from kalakan.cli.api import add_api_args
    add_api_args(api_parser)
    api_parser.set_defaults(func=api)

    # Normalize command
    norm_parser = subparsers.add_parser("norm", help="Normalize Twi text")
    from kalakan.cli.norm import add_norm_args
    add_norm_args(norm_parser)
    norm_parser.set_defaults(func=norm)

    # Generate metadata command
    gen_metadata_parser = subparsers.add_parser("gen-metadata", help="Generate metadata.csv for TTS datasets")
    from kalakan.cli.gen_metadata import add_gen_metadata_args
    add_gen_metadata_args(gen_metadata_parser)
    gen_metadata_parser.set_defaults(func=gen_metadata)

    # Train TTS command
    train_tts_parser = subparsers.add_parser("train-tts", help="Train a complete TTS model (acoustic + vocoder)")
    train_tts_parser.add_argument("--data-dir", required=True, help="Directory containing processed dataset")
    train_tts_parser.add_argument("--output-dir", required=True, help="Directory to save trained models")
    train_tts_parser.add_argument("--acoustic-config", required=True, help="Path to acoustic model training configuration")
    train_tts_parser.add_argument("--vocoder-config", required=True, help="Path to vocoder training configuration")
    train_tts_parser.add_argument("--resume-acoustic", help="Path to acoustic model checkpoint to resume training")
    train_tts_parser.add_argument("--resume-vocoder", help="Path to vocoder checkpoint to resume training")
    train_tts_parser.add_argument("--skip-acoustic", action="store_true", help="Skip acoustic model training")
    train_tts_parser.add_argument("--skip-vocoder", action="store_true", help="Skip vocoder training")
    train_tts_parser.add_argument("--skip-mel-computation", action="store_true", help="Skip mel spectrogram computation")
    train_tts_parser.add_argument("--test-sentences", help="Path to file containing test sentences")
    train_tts_parser.set_defaults(func=train_tts)

    # Evaluate TTS command
    evaluate_tts_parser = subparsers.add_parser("evaluate-tts", help="Evaluate a trained TTS model")
    evaluate_tts_parser.add_argument("--acoustic-model", required=True, help="Path to acoustic model checkpoint")
    evaluate_tts_parser.add_argument("--vocoder", required=True, help="Path to vocoder checkpoint")
    evaluate_tts_parser.add_argument("--test-data", help="Path to test data JSON file (for objective metrics)")
    evaluate_tts_parser.add_argument("--test-sentences", help="Path to file containing test sentences")
    evaluate_tts_parser.add_argument("--output-dir", default="evaluation_results", help="Directory to save evaluation results")
    evaluate_tts_parser.set_defaults(func=evaluate_tts)

    # Train Extended command
    train_extended_parser = subparsers.add_parser("train-extended", help="Train a TTS model with support for large audio files")
    from kalakan.cli.train_extended import add_train_args
    add_train_args(train_extended_parser)
    train_extended_parser.set_defaults(func=train_extended)

    args = parser.parse_args()

    if args.version:
        import kalakan
        print(f"Kalakan TTS version {kalakan.__version__}")
        return 0

    if not hasattr(args, "func"):
        parser.print_help()
        return 1

    # Check if the function expects arguments
    import inspect
    sig = inspect.signature(args.func)
    if len(sig.parameters) > 0:
        return args.func(args)
    else:
        return args.func()

if __name__ == "__main__":
    sys.exit(main())