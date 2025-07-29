"""
Command-line interface for generating metadata.csv files.

This module provides a command-line interface for generating metadata.csv files
for Twi TTS datasets, making it easy for users to prepare their data for training.
"""

import argparse
import csv
import json
import logging
import os
import random
import re
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog
from typing import Dict, List, Optional, Tuple, Union

import librosa
import numpy as np
import soundfile as sf
from tqdm import tqdm

from kalakan.text.cleaner import clean_text
from kalakan.text.normalizer import normalize_text
from kalakan.text.enhanced_g2p import EnhancedTwiG2P
from kalakan.utils.logging import setup_logger


def add_gen_metadata_args(parser):
    """Add metadata generation arguments to the parser."""
    # Input arguments
    parser.add_argument("--input-dir", "-i", type=str, required=True,
                        help="Input directory containing audio files and transcripts")
    parser.add_argument("--output-dir", "-o", type=str, default=None,
                        help="Output directory for generated metadata (default: same as input)")

    # Audio file arguments
    parser.add_argument("--audio-dir", type=str, default=None,
                        help="Audio files directory (default: input-dir/wavs or input-dir)")
    parser.add_argument("--audio-ext", type=str, default="wav",
                        help="Audio file extension (default: wav)")
    parser.add_argument("--recursive", action="store_true",
                        help="Search for audio files recursively")

    # Transcript arguments
    parser.add_argument("--transcript-file", "-t", type=str, default=None,
                        help="Transcript file path (auto-detect if not specified)")
    parser.add_argument("--transcript-format", choices=["csv", "txt", "json"], default="auto",
                        help="Transcript file format (default: auto-detect)")
    parser.add_argument("--transcript-delimiter", type=str, default="|",
                        help="CSV delimiter for transcript file (default: |)")
    parser.add_argument("--text-column", type=int, default=1,
                        help="Text column index in CSV (0-based, default: 1)")
    parser.add_argument("--id-column", type=int, default=0,
                        help="ID column index in CSV (0-based, default: 0)")

    # Audio processing arguments
    parser.add_argument("--sample-rate", type=int, default=22050,
                        help="Target sample rate (default: 22050)")
    parser.add_argument("--min-duration", type=float, default=0.5,
                        help="Minimum audio duration in seconds (default: 0.5)")
    parser.add_argument("--max-duration", type=float, default=10.0,
                        help="Maximum audio duration in seconds (default: 10.0)")
    parser.add_argument("--trim-silence", action="store_true",
                        help="Trim silence from audio files")
    parser.add_argument("--normalize-audio", action="store_true",
                        help="Normalize audio amplitude")

    # Text processing arguments
    parser.add_argument("--clean-text", action="store_true", default=True,
                        help="Clean text before processing (default: True)")
    parser.add_argument("--normalize-text", action="store_true", default=True,
                        help="Normalize text before processing (default: True)")
    parser.add_argument("--generate-phonemes", action="store_true",
                        help="Generate phonemes using G2P")
    parser.add_argument("--min-text-length", type=int, default=5,
                        help="Minimum text length in characters (default: 5)")
    parser.add_argument("--max-text-length", type=int, default=200,
                        help="Maximum text length in characters (default: 200)")

    # Dataset splitting arguments
    parser.add_argument("--split-dataset", action="store_true",
                        help="Split dataset into train/validation sets")
    parser.add_argument("--val-ratio", type=float, default=0.1,
                        help="Validation set ratio (default: 0.1)")
    parser.add_argument("--test-ratio", type=float, default=0.0,
                        help="Test set ratio (default: 0.0)")
    parser.add_argument("--random-seed", type=int, default=42,
                        help="Random seed for dataset splitting (default: 42)")

    # Output format arguments
    parser.add_argument("--output-format", choices=["csv", "json", "both"], default="csv",
                        help="Output format (default: csv)")
    parser.add_argument("--csv-delimiter", type=str, default="|",
                        help="CSV delimiter for output (default: |)")
    parser.add_argument("--include-stats", action="store_true",
                        help="Include dataset statistics in output")

    # Quality control arguments
    parser.add_argument("--validate-audio", action="store_true",
                        help="Validate audio files (check for corruption)")
    parser.add_argument("--check-duplicates", action="store_true",
                        help="Check for duplicate texts")
    parser.add_argument("--remove-duplicates", action="store_true",
                        help="Remove duplicate entries")

    # Advanced options
    parser.add_argument("--speaker-id", type=str, default=None,
                        help="Speaker ID to add to metadata")
    parser.add_argument("--language", type=str, default="twi",
                        help="Language code (default: twi)")
    parser.add_argument("--encoding", type=str, default="utf-8",
                        help="Text file encoding (default: utf-8)")
    parser.add_argument("--parallel-jobs", type=int, default=1,
                        help="Number of parallel jobs for processing (default: 1)")

    # Display options
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Verbose output")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Quiet mode (minimal output)")
    parser.add_argument("--progress", action="store_true", default=True,
                        help="Show progress bar (default: True)")


def find_audio_files(audio_dir: str, audio_ext: str, recursive: bool = False) -> List[str]:
    """
    Find audio files in the specified directory.

    Args:
        audio_dir: Directory to search for audio files.
        audio_ext: Audio file extension.
        recursive: Whether to search recursively.

    Returns:
        List of audio file paths.
    """
    audio_files = []
    pattern = f"*.{audio_ext}"

    if recursive:
        audio_files = list(Path(audio_dir).rglob(pattern))
    else:
        audio_files = list(Path(audio_dir).glob(pattern))

    return [str(f) for f in sorted(audio_files)]


def detect_transcript_file(input_dir: str) -> Optional[str]:
    """
    Auto-detect transcript file in the input directory.

    Args:
        input_dir: Input directory to search.

    Returns:
        Path to transcript file or None if not found.
    """
    possible_names = [
        "metadata.csv", "transcript.csv", "transcripts.csv",
        "metadata.txt", "transcript.txt", "transcripts.txt",
        "metadata.json", "transcript.json", "transcripts.json"
    ]

    for name in possible_names:
        path = os.path.join(input_dir, name)
        if os.path.exists(path):
            return path

    return None


def load_transcripts(
    transcript_file: str,
    format_type: str = "auto",
    delimiter: str = "|",
    text_column: int = 1,
    id_column: int = 0,
    encoding: str = "utf-8"
) -> Dict[str, str]:
    """
    Load transcripts from file.

    Args:
        transcript_file: Path to transcript file.
        format_type: File format (auto, csv, txt, json).
        delimiter: CSV delimiter.
        text_column: Text column index for CSV.
        id_column: ID column index for CSV.
        encoding: File encoding.

    Returns:
        Dictionary mapping audio IDs to texts.
    """
    transcripts = {}

    # Auto-detect format
    if format_type == "auto":
        ext = os.path.splitext(transcript_file)[1].lower()
        if ext == ".csv":
            format_type = "csv"
        elif ext == ".json":
            format_type = "json"
        else:
            format_type = "txt"

    if format_type == "csv":
        with open(transcript_file, "r", encoding=encoding) as f:
            reader = csv.reader(f, delimiter=delimiter)
            for row in reader:
                if len(row) > max(text_column, id_column):
                    audio_id = row[id_column].strip()
                    text = row[text_column].strip()
                    transcripts[audio_id] = text

    elif format_type == "json":
        with open(transcript_file, "r", encoding=encoding) as f:
            data = json.load(f)
            if isinstance(data, dict):
                transcripts = data
            elif isinstance(data, list):
                for item in data:
                    if "id" in item and "text" in item:
                        transcripts[item["id"]] = item["text"]

    else:  # txt format
        with open(transcript_file, "r", encoding=encoding) as f:
            for line in f:
                line = line.strip()
                if delimiter in line:
                    parts = line.split(delimiter, 1)
                    if len(parts) == 2:
                        audio_id, text = parts
                        transcripts[audio_id.strip()] = text.strip()

    return transcripts


def process_audio_file(
    audio_path: str,
    target_sr: int = 22050,
    min_duration: float = 0.5,
    max_duration: float = 10.0,
    trim_silence: bool = False,
    normalize_audio: bool = False,
    validate: bool = False
) -> Tuple[bool, float, Optional[str]]:
    """
    Process and validate an audio file.

    Args:
        audio_path: Path to audio file.
        target_sr: Target sample rate.
        min_duration: Minimum duration in seconds.
        max_duration: Maximum duration in seconds.
        trim_silence: Whether to trim silence.
        normalize_audio: Whether to normalize audio.
        validate: Whether to validate audio file.

    Returns:
        Tuple of (is_valid, duration, error_message).
    """
    try:
        # Load audio
        audio, sr = librosa.load(audio_path, sr=target_sr)
        duration = len(audio) / sr

        # Check duration
        if duration < min_duration or duration > max_duration:
            return False, duration, f"Duration {duration:.2f}s outside range [{min_duration}, {max_duration}]"

        # Validate audio if requested
        if validate:
            if np.all(audio == 0):
                return False, duration, "Audio contains only silence"
            if np.any(np.isnan(audio)) or np.any(np.isinf(audio)):
                return False, duration, "Audio contains NaN or Inf values"

        return True, duration, None

    except Exception as e:
        return False, 0.0, f"Error loading audio: {str(e)}"


def process_text(
    text: str,
    clean: bool = True,
    normalize: bool = True,
    min_length: int = 5,
    max_length: int = 200,
    g2p: Optional[EnhancedTwiG2P] = None
) -> Tuple[bool, str, Optional[List[str]], Optional[str]]:
    """
    Process and validate text.

    Args:
        text: Input text.
        clean: Whether to clean text.
        normalize: Whether to normalize text.
        min_length: Minimum text length.
        max_length: Maximum text length.
        g2p: G2P model for phoneme generation.

    Returns:
        Tuple of (is_valid, processed_text, phonemes, error_message).
    """
    try:
        processed_text = text

        # Clean text
        if clean:
            processed_text = clean_text(processed_text)

        # Normalize text
        if normalize:
            processed_text = normalize_text(processed_text)

        # Check length
        if len(processed_text) < min_length or len(processed_text) > max_length:
            return False, processed_text, None, f"Text length {len(processed_text)} outside range [{min_length}, {max_length}]"

        # Generate phonemes
        phonemes = None
        if g2p is not None:
            try:
                phonemes = g2p.text_to_phonemes(processed_text)
            except Exception as e:
                return False, processed_text, None, f"G2P error: {str(e)}"

        return True, processed_text, phonemes, None

    except Exception as e:
        return False, text, None, f"Error processing text: {str(e)}"


def generate_metadata(args) -> int:
    """
    Generate metadata for TTS dataset.

    Args:
        args: Command-line arguments.

    Returns:
        Exit code.
    """
    # Set up logger
    if args.quiet:
        log_level = logging.WARNING
    elif args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logger = setup_logger("gen_metadata", level=log_level)

    # Validate input directory
    if not os.path.exists(args.input_dir):
        logger.error(f"Input directory does not exist: {args.input_dir}")
        return 1

    # Set output directory
    output_dir = args.output_dir or args.input_dir
    os.makedirs(output_dir, exist_ok=True)

    # Set audio directory
    audio_dir = args.audio_dir
    if audio_dir is None:
        # Try common audio directory names
        for dirname in ["wavs", "audio", "sounds"]:
            candidate = os.path.join(args.input_dir, dirname)
            if os.path.exists(candidate):
                audio_dir = candidate
                break
        else:
            audio_dir = args.input_dir

    logger.info(f"Audio directory: {audio_dir}")

    # Find audio files
    logger.info("Finding audio files...")
    audio_files = find_audio_files(audio_dir, args.audio_ext, args.recursive)
    logger.info(f"Found {len(audio_files)} audio files")

    if not audio_files:
        logger.error("No audio files found")
        return 1

    # Load transcripts
    transcript_file = args.transcript_file
    if transcript_file is None:
        transcript_file = detect_transcript_file(args.input_dir)
        if transcript_file is None:
            logger.error("No transcript file found. Please specify --transcript-file")
            return 1

    logger.info(f"Loading transcripts from: {transcript_file}")
    transcripts = load_transcripts(
        transcript_file,
        args.transcript_format,
        args.transcript_delimiter,
        args.text_column,
        args.id_column,
        args.encoding
    )
    logger.info(f"Loaded {len(transcripts)} transcripts")

    # Initialize G2P if needed
    g2p = None
    if args.generate_phonemes:
        logger.info("Initializing G2P model...")
        try:
            g2p = EnhancedTwiG2P()
        except Exception as e:
            logger.warning(f"Failed to initialize G2P: {e}")

    # Process files
    logger.info("Processing files...")
    processed_entries = []
    skipped_entries = []

    # Set up progress bar
    if args.progress and not args.quiet:
        audio_files = tqdm(audio_files, desc="Processing")

    for audio_path in audio_files:
        # Get audio ID from filename
        audio_id = os.path.splitext(os.path.basename(audio_path))[0]

        # Check if transcript exists
        if audio_id not in transcripts:
            skipped_entries.append((audio_id, "No transcript found"))
            continue

        text = transcripts[audio_id]

        # Process audio
        audio_valid, duration, audio_error = process_audio_file(
            audio_path,
            args.sample_rate,
            args.min_duration,
            args.max_duration,
            args.trim_silence,
            args.normalize_audio,
            args.validate_audio
        )

        if not audio_valid:
            skipped_entries.append((audio_id, f"Audio: {audio_error}"))
            continue

        # Process text
        text_valid, processed_text, phonemes, text_error = process_text(
            text,
            args.clean_text,
            args.normalize_text,
            args.min_text_length,
            args.max_text_length,
            g2p
        )

        if not text_valid:
            skipped_entries.append((audio_id, f"Text: {text_error}"))
            continue

        # Create entry
        entry = {
            "id": audio_id,
            "audio_path": os.path.relpath(audio_path, output_dir),
            "duration": duration,
            "text": processed_text,
            "original_text": text,
            "phonemes": phonemes or [],
        }

        # Add optional fields
        if args.speaker_id:
            entry["speaker_id"] = args.speaker_id
        if args.language:
            entry["language"] = args.language

        processed_entries.append(entry)

    logger.info(f"Processed {len(processed_entries)} entries")
    logger.info(f"Skipped {len(skipped_entries)} entries")

    if args.verbose and skipped_entries:
        logger.info("Skipped entries:")
        for audio_id, reason in skipped_entries[:10]:  # Show first 10
            logger.info(f"  {audio_id}: {reason}")
        if len(skipped_entries) > 10:
            logger.info(f"  ... and {len(skipped_entries) - 10} more")

    if not processed_entries:
        logger.error("No valid entries found")
        return 1

    # Check for duplicates
    if args.check_duplicates or args.remove_duplicates:
        logger.info("Checking for duplicates...")
        text_counts = {}
        for entry in processed_entries:
            text = entry["text"]
            if text in text_counts:
                text_counts[text].append(entry)
            else:
                text_counts[text] = [entry]

        duplicates = {text: entries for text, entries in text_counts.items() if len(entries) > 1}

        if duplicates:
            logger.warning(f"Found {len(duplicates)} duplicate texts")
            if args.verbose:
                for text, entries in list(duplicates.items())[:5]:  # Show first 5
                    ids = [e["id"] for e in entries]
                    logger.warning(f"  '{text[:50]}...': {ids}")

            if args.remove_duplicates:
                logger.info("Removing duplicates (keeping first occurrence)...")
                unique_entries = []
                seen_texts = set()
                for entry in processed_entries:
                    if entry["text"] not in seen_texts:
                        unique_entries.append(entry)
                        seen_texts.add(entry["text"])
                processed_entries = unique_entries
                logger.info(f"Kept {len(processed_entries)} unique entries")

    # Split dataset if requested
    if args.split_dataset:
        logger.info("Splitting dataset...")
        random.seed(args.random_seed)
        random.shuffle(processed_entries)

        total_size = len(processed_entries)
        val_size = int(total_size * args.val_ratio)
        test_size = int(total_size * args.test_ratio)
        train_size = total_size - val_size - test_size

        train_set = processed_entries[:train_size]
        val_set = processed_entries[train_size:train_size + val_size]
        test_set = processed_entries[train_size + val_size:]

        splits = {"train": train_set, "val": val_set}
        if test_set:
            splits["test"] = test_set

        logger.info(f"Dataset split: train={len(train_set)}, val={len(val_set)}, test={len(test_set)}")
    else:
        splits = {"metadata": processed_entries}

    # Save metadata
    for split_name, split_data in splits.items():
        if args.output_format in ["csv", "both"]:
            csv_path = os.path.join(output_dir, f"{split_name}.csv")
            logger.info(f"Saving CSV metadata to: {csv_path}")

            with open(csv_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f, delimiter=args.csv_delimiter)

                # Write header
                header = ["id", "audio_path", "duration", "text"]
                if args.generate_phonemes:
                    header.append("phonemes")
                if args.speaker_id:
                    header.append("speaker_id")
                if args.language:
                    header.append("language")

                writer.writerow(header)

                # Write data
                for entry in split_data:
                    row = [
                        entry["id"],
                        entry["audio_path"],
                        f"{entry['duration']:.2f}",
                        entry["text"]
                    ]
                    if args.generate_phonemes:
                        row.append(" ".join(entry["phonemes"]))
                    if args.speaker_id:
                        row.append(entry["speaker_id"])
                    if args.language:
                        row.append(entry["language"])

                    writer.writerow(row)

        if args.output_format in ["json", "both"]:
            json_path = os.path.join(output_dir, f"{split_name}.json")
            logger.info(f"Saving JSON metadata to: {json_path}")

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(split_data, f, ensure_ascii=False, indent=2)

    # Save dataset statistics
    if args.include_stats:
        stats = {
            "total_entries": len(processed_entries),
            "skipped_entries": len(skipped_entries),
            "total_duration": sum(entry["duration"] for entry in processed_entries),
            "avg_duration": np.mean([entry["duration"] for entry in processed_entries]),
            "min_duration": min(entry["duration"] for entry in processed_entries),
            "max_duration": max(entry["duration"] for entry in processed_entries),
            "avg_text_length": np.mean([len(entry["text"]) for entry in processed_entries]),
            "min_text_length": min(len(entry["text"]) for entry in processed_entries),
            "max_text_length": max(len(entry["text"]) for entry in processed_entries),
        }

        if args.split_dataset:
            for split_name, split_data in splits.items():
                stats[f"{split_name}_size"] = len(split_data)

        stats_path = os.path.join(output_dir, "dataset_stats.json")
        logger.info(f"Saving dataset statistics to: {stats_path}")

        with open(stats_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)

        # Print summary
        logger.info("Dataset Statistics:")
        logger.info(f"  Total entries: {stats['total_entries']}")
        logger.info(f"  Total duration: {stats['total_duration']:.2f} seconds ({stats['total_duration']/3600:.2f} hours)")
        logger.info(f"  Average duration: {stats['avg_duration']:.2f} seconds")
        logger.info(f"  Average text length: {stats['avg_text_length']:.1f} characters")

    logger.info("Metadata generation completed successfully!")
    return 0


def main(args=None):
    """Main function."""
    if args is None:
        parser = argparse.ArgumentParser(description="Generate metadata.csv for Twi TTS datasets")
        add_gen_metadata_args(parser)
        args = parser.parse_args()

    return generate_metadata(args)


if __name__ == "__main__":
    sys.exit(main())