"""
Enhanced Grapheme-to-Phoneme (G2P) conversion for Twi language.

This module provides an improved G2P converter for Twi language, which converts
Twi text (graphemes) to phonemes for TTS processing with better handling of
tonal and prosodic features.
"""

import os
import re
import json
from typing import Dict, List, Optional, Set, Tuple

from kalakan.text.phonemes import TwiPhonemes
from kalakan.text.tokenizer import TwiTokenizer
from kalakan.text.cleaner import clean_text
from kalakan.text.normalizer import normalize_text


class EnhancedTwiG2P:
    """
    Enhanced Grapheme-to-Phoneme (G2P) converter for Twi language.

    This class provides improved methods for converting Twi text to phonemes,
    with better handling of tonal patterns, vowel lengthening, and other
    prosodic features specific to Twi.
    """

    def __init__(
        self,
        pronunciation_dict_path: Optional[str] = None,
        tone_markers: bool = True,
        vowel_lengthening: bool = True,
        clean_text_flag: bool = True,
        normalize_text_flag: bool = True
    ):
        """
        Initialize the Enhanced Twi G2P converter.

        Args:
            pronunciation_dict_path: Path to a pronunciation dictionary file.
                If provided, the dictionary will be loaded and used for G2P conversion.
            tone_markers: Whether to include tone markers in the phoneme output.
            vowel_lengthening: Whether to model vowel lengthening in the phoneme output.
            clean_text_flag: Whether to clean text before processing.
            normalize_text_flag: Whether to normalize text before processing.
        """
        self.tokenizer = TwiTokenizer()
        self.phonemes = TwiPhonemes
        self.tone_markers = tone_markers
        self.vowel_lengthening = vowel_lengthening
        self.clean_text_flag = clean_text_flag
        self.normalize_text_flag = normalize_text_flag

        # Pronunciation dictionary (word -> phoneme sequence)
        self.pronunciation_dict: Dict[str, List[str]] = {}

        # Load pronunciation dictionary if provided
        if pronunciation_dict_path and os.path.exists(pronunciation_dict_path):
            self._load_pronunciation_dict(pronunciation_dict_path)

    def _load_pronunciation_dict(self, dict_path: str) -> None:
        """
        Load a pronunciation dictionary from a file.

        The file should have one word per line, with the word and its
        pronunciation separated by a tab or multiple spaces.

        Args:
            dict_path: Path to the pronunciation dictionary file.
        """
        with open(dict_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                parts = re.split(r'\s+', line, maxsplit=1)
                if len(parts) != 2:
                    continue

                word, pronunciation = parts
                self.pronunciation_dict[word.lower()] = pronunciation.split()

    def _detect_vowel_length(self, word: str) -> List[Tuple[int, int]]:
        """
        Detect vowel lengthening in a word.

        In Twi, vowel lengthening is often indicated by repeated vowels
        or has semantic significance.

        Args:
            word: The Twi word to analyze.

        Returns:
            List of tuples (start_index, length) for lengthened vowels.
        """
        lengthened_vowels = []
        i = 0

        while i < len(word):
            if self.phonemes.is_vowel(word[i]):
                # Found a vowel
                start = i
                current_vowel = word[i]
                length = 1

                # Check for repeated vowels
                j = i + 1
                while j < len(word) and word[j] == current_vowel:
                    length += 1
                    j += 1

                if length > 1:
                    lengthened_vowels.append((start, length))

                i = j
            else:
                i += 1

        return lengthened_vowels

    def _detect_tone_pattern(self, word: str) -> List[str]:
        """
        Detect tone patterns in a word.

        Twi is a tonal language, and tone can distinguish meaning.
        This method detects high, low, and neutral tones.

        Args:
            word: The Twi word to analyze.

        Returns:
            List of tone markers ('H' for high, 'L' for low, 'N' for neutral)
            for each vowel in the word.
        """
        tones = []

        for char in word:
            if not self.phonemes.is_vowel(char):
                continue

            tone = self.phonemes.get_tone(char)
            if tone == 'high':
                tones.append('H')
            elif tone == 'low':
                tones.append('L')
            else:
                tones.append('N')  # Neutral tone

        return tones

    def _apply_enhanced_twi_g2p_rules(self, word: str) -> List[str]:
        """
        Apply enhanced Twi-specific G2P rules to convert a word to phonemes.

        Args:
            word: The Twi word to convert.

        Returns:
            A list of phonemes.
        """
        # First, try to tokenize the word into phonemes using the tokenizer
        phonemes = self.tokenizer.word_to_phonemes(word)

        # Apply additional Twi-specific G2P rules

        # Rule 1: Handle vowel lengthening
        if self.vowel_lengthening:
            lengthened_vowels = self._detect_vowel_length(word)

            # Mark lengthened vowels with a special tag
            # We'll use the same vowel phoneme but add a length marker
            for start, length in lengthened_vowels:
                # Find the corresponding position in the phoneme list
                phoneme_pos = 0
                char_pos = 0

                while char_pos < start and phoneme_pos < len(phonemes):
                    # Skip consonant clusters (they count as one phoneme but multiple chars)
                    if phoneme_pos < len(phonemes) - 1 and phonemes[phoneme_pos] + phonemes[phoneme_pos + 1] in self.tokenizer.CONSONANT_CLUSTERS:
                        char_pos += 2
                        phoneme_pos += 1
                    else:
                        char_pos += 1
                        phoneme_pos += 1

                # Add length marker to the vowel phoneme
                if phoneme_pos < len(phonemes) and self.phonemes.is_vowel(phonemes[phoneme_pos]):
                    # Replace with lengthened version (we'll use a colon to indicate length)
                    phonemes[phoneme_pos] = phonemes[phoneme_pos] + ":"

        # Rule 2: Handle tone patterns
        if self.tone_markers:
            tones = self._detect_tone_pattern(word)

            # Apply tone markers to vowels
            tone_idx = 0
            for i, phoneme in enumerate(phonemes):
                if self.phonemes.is_vowel(phoneme):
                    if tone_idx < len(tones):
                        # Only add explicit tone marker if it's not already in the vowel
                        # (some vowels already have tone markers in Unicode)
                        if tones[tone_idx] == 'H' and not phoneme.endswith('́'):
                            phonemes[i] = phoneme + "́"  # Add high tone marker
                        elif tones[tone_idx] == 'L' and not phoneme.endswith('̀'):
                            phonemes[i] = phoneme + "̀"  # Add low tone marker
                        # Neutral tone doesn't need a marker

                        tone_idx += 1

        # Rule 3: Handle nasal sounds
        i = 0
        while i < len(phonemes):
            if (i < len(phonemes) - 1 and
                self.phonemes.is_nasal(phonemes[i]) and
                not self.phonemes.is_vowel(phonemes[i+1])):
                # Nasal followed by a consonant - in Twi, this often nasalizes the consonant
                # Mark the consonant as nasalized
                phonemes[i+1] = phonemes[i+1] + "̃"  # Add nasalization marker
            i += 1

        return phonemes

    def word_to_phonemes(self, word: str) -> List[str]:
        """
        Convert a Twi word to phonemes.

        Args:
            word: The Twi word to convert.

        Returns:
            A list of phonemes.
        """
        # Convert to lowercase
        word = word.lower()

        # Check if the word is in the pronunciation dictionary
        if word in self.pronunciation_dict:
            return self.pronunciation_dict[word]

        # Apply enhanced Twi G2P rules
        return self._apply_enhanced_twi_g2p_rules(word)

    def text_to_phonemes(self, text: str) -> List[str]:
        """
        Convert Twi text to phonemes.

        Args:
            text: The Twi text to convert.

        Returns:
            A list of phonemes.
        """
        # Clean and normalize text if requested
        if self.clean_text_flag:
            text = clean_text(text)
        if self.normalize_text_flag:
            text = normalize_text(text)

        # Tokenize the text
        tokens = self.tokenizer.tokenize(text)

        # Convert each token to phonemes
        all_phonemes = []
        for token in tokens:
            # Skip punctuation
            if re.match(r'^[.,!?;:"\'\(\)\[\]\{\}]$', token):
                continue

            # Convert the token to phonemes
            phonemes = self.word_to_phonemes(token)
            all_phonemes.extend(phonemes)

            # Add a word boundary marker
            all_phonemes.append('|')

        # Remove the last word boundary marker
        if all_phonemes and all_phonemes[-1] == '|':
            all_phonemes.pop()

        return all_phonemes

    def text_to_phoneme_sequence(self, text: str) -> List[int]:
        """
        Convert Twi text to a sequence of phoneme IDs.

        Args:
            text: The Twi text to convert.

        Returns:
            A list of phoneme IDs.
        """
        phonemes = self.text_to_phonemes(text)
        return self.phonemes.text_to_sequence(' '.join(phonemes))

    def save_pronunciation_dict(self, output_path: str) -> None:
        """
        Save the pronunciation dictionary to a file.

        Args:
            output_path: Path to save the pronunciation dictionary.
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            for word, phonemes in self.pronunciation_dict.items():
                f.write(f"{word}\t{' '.join(phonemes)}\n")

    def add_to_pronunciation_dict(self, word: str, phonemes: List[str]) -> None:
        """
        Add a word and its pronunciation to the dictionary.

        Args:
            word: The word to add.
            phonemes: The phoneme sequence for the word.
        """
        self.pronunciation_dict[word.lower()] = phonemes