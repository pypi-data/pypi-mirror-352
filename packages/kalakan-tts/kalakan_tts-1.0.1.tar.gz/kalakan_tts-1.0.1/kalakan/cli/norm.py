"""
Command-line interface for text normalization.

This module provides a command-line interface for normalizing Twi text
using Kalakan TTS text processing capabilities.
"""

import argparse
import logging
import os
import sys
import tkinter as tk
from tkinter import filedialog
from typing import List, Optional

from kalakan.text.normalizer import normalize_text
from kalakan.utils.logging import setup_logger


def add_norm_args(parser):
    """Add normalization arguments to the parser."""
    # Input arguments (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("-T", "--text", type=str,
                            help="Direct Twi text input to normalize")
    input_group.add_argument("-S", "--select", action="store_true",
                            help="Open file dialog to select Twi text file")
    input_group.add_argument("-f", "--file", type=str,
                            help="Path to text file to normalize")

    # Output arguments
    parser.add_argument("-o", "--output", type=str, default=None,
                        help="Output file path (default: print to stdout)")
    parser.add_argument("--output-dir", type=str, default=None,
                        help="Output directory for batch processing")

    # Processing options
    parser.add_argument("--no-numbers", action="store_true",
                        help="Skip number normalization")
    parser.add_argument("--no-abbreviations", action="store_true",
                        help="Skip abbreviation expansion")
    parser.add_argument("--no-punctuation", action="store_true",
                        help="Skip punctuation normalization")
    parser.add_argument("--preserve-case", action="store_true",
                        help="Preserve original case (don't convert to lowercase)")

    # Format options
    parser.add_argument("--format", choices=["text", "json", "csv"], default="text",
                        help="Output format (default: text)")
    parser.add_argument("--encoding", default="utf-8",
                        help="File encoding (default: utf-8)")

    # Batch processing
    parser.add_argument("--batch", action="store_true",
                        help="Process multiple files (when using --select)")
    parser.add_argument("--recursive", action="store_true",
                        help="Process files recursively in directories")

    # Display options
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Verbose output")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Quiet mode (minimal output)")
    parser.add_argument("--show-diff", action="store_true",
                        help="Show differences between original and normalized text")


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Normalize Twi text using Kalakan TTS")
    add_norm_args(parser)
    return parser.parse_args()


def select_file(batch_mode: bool = False) -> Optional[List[str]]:
    """
    Open file dialog to select text file(s).

    Args:
        batch_mode: Whether to allow multiple file selection.

    Returns:
        List of selected file paths, or None if cancelled.
    """
    # Create a root window and hide it
    root = tk.Tk()
    root.withdraw()

    try:
        if batch_mode:
            # Allow multiple file selection
            file_paths = filedialog.askopenfilenames(
                title="Select Twi text files to normalize",
                filetypes=[
                    ("Text files", "*.txt"),
                    ("All files", "*.*")
                ]
            )
            return list(file_paths) if file_paths else None
        else:
            # Single file selection
            file_path = filedialog.askopenfilename(
                title="Select Twi text file to normalize",
                filetypes=[
                    ("Text files", "*.txt"),
                    ("All files", "*.*")
                ]
            )
            return [file_path] if file_path else None
    finally:
        root.destroy()


def read_text_file(file_path: str, encoding: str = "utf-8") -> str:
    """
    Read text from a file.

    Args:
        file_path: Path to the text file.
        encoding: File encoding.

    Returns:
        File content as string.
    """
    try:
        with open(file_path, "r", encoding=encoding) as f:
            return f.read()
    except UnicodeDecodeError:
        # Try with different encodings if UTF-8 fails
        for enc in ["latin-1", "cp1252", "iso-8859-1"]:
            try:
                with open(file_path, "r", encoding=enc) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        raise


def write_text_file(file_path: str, content: str, encoding: str = "utf-8") -> None:
    """
    Write text to a file.

    Args:
        file_path: Path to the output file.
        content: Content to write.
        encoding: File encoding.
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding=encoding) as f:
        f.write(content)


def normalize_text_custom(text: str, args) -> str:
    """
    Normalize text with custom options.

    Args:
        text: Text to normalize.
        args: Command-line arguments.

    Returns:
        Normalized text.
    """
    from kalakan.text.normalizer import (
        normalize_numbers, normalize_abbreviations,
        normalize_punctuation
    )

    result = text

    # Apply normalization steps based on arguments
    # Normalize abbreviations first (before lowercasing)
    if not args.no_abbreviations:
        result = normalize_abbreviations(result)

    if not args.preserve_case:
        result = result.lower()

    if not args.no_punctuation:
        result = normalize_punctuation(result)

    if not args.no_numbers:
        result = normalize_numbers(result)

    # Normalize special characters (always applied)
    result = result.replace('ε', 'ɛ')  # Normalize epsilon
    result = result.replace('Ε', 'Ɛ')  # Normalize capital epsilon
    result = result.replace('ο', 'ɔ')  # Normalize open o
    result = result.replace('Ο', 'Ɔ')  # Normalize capital open o

    return result.strip()


def format_output(original: str, normalized: str, format_type: str, show_diff: bool = False) -> str:
    """
    Format the output according to the specified format.

    Args:
        original: Original text.
        normalized: Normalized text.
        format_type: Output format.
        show_diff: Whether to show differences.

    Returns:
        Formatted output string.
    """
    if format_type == "json":
        import json
        from typing import Dict, Union, Any
        data: Dict[str, Any] = {
            "original": original,
            "normalized": normalized
        }
        if show_diff:
            data["changed"] = original != normalized
        return json.dumps(data, ensure_ascii=False, indent=2)

    elif format_type == "csv":
        import csv
        import io
        output = io.StringIO()
        writer = csv.writer(output)
        if show_diff:
            writer.writerow(["Original", "Normalized", "Changed"])
            writer.writerow([original, normalized, original != normalized])
        else:
            writer.writerow(["Original", "Normalized"])
            writer.writerow([original, normalized])
        return output.getvalue()

    else:  # text format
        if show_diff and original != normalized:
            return f"Original:   {original}\nNormalized: {normalized}\n"
        else:
            return normalized


def main(args=None):
    """Main function."""
    # Parse arguments if not provided
    if args is None:
        args = parse_args()

    # Set up logger
    if args.quiet:
        log_level = logging.WARNING
    elif args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logger = setup_logger("norm", level=log_level)

    # Get input text(s)
    texts_to_process = []
    file_paths = []

    if args.text:
        # Direct text input
        texts_to_process.append(("direct_input", args.text))

    elif args.select:
        # File dialog selection
        selected_files = select_file(batch_mode=args.batch)
        if not selected_files:
            logger.error("No files selected")
            sys.exit(1)
        file_paths = selected_files

    elif args.file:
        # File path provided
        if os.path.isdir(args.file) and args.recursive:
            # Process directory recursively
            for root, dirs, files in os.walk(args.file):
                for file in files:
                    if file.endswith('.txt'):
                        file_paths.append(os.path.join(root, file))
        else:
            file_paths = [args.file]

    # Read files
    for file_path in file_paths:
        try:
            content = read_text_file(file_path, args.encoding)
            texts_to_process.append((file_path, content))
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            continue

    if not texts_to_process:
        logger.error("No text to process")
        sys.exit(1)

    # Process texts
    results = []
    for source, text in texts_to_process:
        if not args.quiet:
            logger.info(f"Processing: {source}")

        # Normalize text
        normalized = normalize_text_custom(text, args)

        # Format output
        formatted_output = format_output(text, normalized, args.format, args.show_diff)
        results.append((source, formatted_output))

        if not args.quiet:
            logger.info(f"Normalized {len(text)} -> {len(normalized)} characters")

    # Output results
    if args.output or args.output_dir:
        # Save to file(s)
        for i, (source, result) in enumerate(results):
            if args.output_dir:
                # Generate output filename
                if source == "direct_input":
                    output_file = os.path.join(args.output_dir, f"normalized_{i+1}.txt")
                else:
                    base_name = os.path.splitext(os.path.basename(source))[0]
                    ext = ".json" if args.format == "json" else ".csv" if args.format == "csv" else ".txt"
                    output_file = os.path.join(args.output_dir, f"{base_name}_normalized{ext}")
            else:
                output_file = args.output

            try:
                write_text_file(output_file, result, args.encoding)
                if not args.quiet:
                    logger.info(f"Saved to: {output_file}")
            except Exception as e:
                logger.error(f"Error writing to {output_file}: {e}")
    else:
        # Print to stdout
        for source, result in results:
            if len(results) > 1 and not args.quiet:
                print(f"\n--- {source} ---")
            print(result)

    if not args.quiet:
        logger.info(f"Processed {len(results)} text(s)")


if __name__ == "__main__":
    main()