#!/usr/bin/env python
#kalakan
"""
Debug utility for Grapheme-to-Phoneme (G2P) conversion.

This module provides utilities for debugging the G2P conversion process,
including visualization of phoneme sequences and intermediate steps.
"""

import argparse
import logging
import sys
from typing import Dict, List, Optional, Set, Tuple

from kalakan.text.normalizer import normalize_text
from kalakan.text.cleaner import clean_text
from kalakan.text.twi_g2p import TwiG2P
from kalakan.text.phonemes import TwiPhonemes
from kalakan.text.tokenizer import TwiTokenizer


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def debug_g2p_conversion(
    text: str,
    normalize: bool = True,
    clean: bool = True,
    verbose: bool = True,
) -> Tuple[List[str], List[int]]:
    """
    Debug the G2P conversion process for a given text.
    
    Args:
        text: Input text to convert.
        normalize: Whether to normalize the text.
        clean: Whether to clean the text.
        verbose: Whether to print debug information.
        
    Returns:
        A tuple containing:
            - A list of phonemes.
            - A list of phoneme IDs.
    """
    # Process text
    if verbose:
        logger.info(f"Original text: {text}")
    
    if clean:
        text = clean_text(text)
        if verbose:
            logger.info(f"Cleaned text: {text}")
    
    if normalize:
        text = normalize_text(text)
        if verbose:
            logger.info(f"Normalized text: {text}")
    
    # Tokenize text
    tokenizer = TwiTokenizer()
    tokens = tokenizer.tokenize(text)
    if verbose:
        logger.info(f"Tokens: {tokens}")
    
    # Convert tokens to phonemes
    g2p = TwiG2P()
    all_phonemes = []
    
    if verbose:
        logger.info("Token-to-phoneme conversion:")
    
    for token in tokens:
        # Skip punctuation
        if token in ".,!?;:\"'()[]{}":
            if verbose:
                logger.info(f"  Skipping punctuation: {token}")
            continue
        
        # Convert token to phonemes
        phonemes = g2p.word_to_phonemes(token)
        if verbose:
            logger.info(f"  Token: {token} -> Phonemes: {phonemes}")
        
        all_phonemes.extend(phonemes)
    
    # Convert phonemes to phoneme IDs
    phoneme_sequence = TwiPhonemes.text_to_sequence(' '.join(all_phonemes))
    
    if verbose:
        # Map phoneme IDs back to phonemes for verification
        phoneme_names = [TwiPhonemes.ID_TO_SYMBOL.get(pid, '?') for pid in phoneme_sequence]
        logger.info(f"Phoneme sequence: {phoneme_sequence}")
        logger.info(f"Phoneme names: {phoneme_names}")
    
    return all_phonemes, phoneme_sequence


def main():
    """Run the G2P debug utility."""
    parser = argparse.ArgumentParser(description="Debug G2P conversion")
    parser.add_argument(
        "--text",
        type=str,
        default="Agoo Kalculus, mepa wo kyɛw, wo ho te sɛn?",
        help="Text to convert",
    )
    parser.add_argument(
        "--no-normalize",
        action="store_true",
        help="Disable text normalization",
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="Disable text cleaning",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress debug output",
    )
    args = parser.parse_args()
    
    # Debug G2P conversion
    phonemes, phoneme_ids = debug_g2p_conversion(
        text=args.text,
        normalize=not args.no_normalize,
        clean=not args.no_clean,
        verbose=not args.quiet,
    )
    
    # Print summary
    if not args.quiet:
        logger.info(f"Total phonemes: {len(phonemes)}")
        logger.info(f"Total phoneme IDs: {len(phoneme_ids)}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())