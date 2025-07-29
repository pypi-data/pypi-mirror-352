"""
Enhanced Grapheme-to-Phoneme (G2P) conversion for Twi language.

This module provides an enhanced G2P converter for Twi language with
improved handling of special characters, tone marks, and phoneme mapping.
"""

import os
import re
import logging
from typing import Dict, List, Optional, Set, Tuple

from kalakan.text.phonemes import TwiPhonemes
from kalakan.text.tokenizer import TwiTokenizer


logger = logging.getLogger(__name__)


class EnhancedTwiG2P:
    """
    Enhanced Grapheme-to-Phoneme (G2P) converter for Twi language.
    
    This class provides improved methods for converting Twi text to phonemes,
    with better handling of special characters, tone marks, and phoneme mapping.
    """
    
    # Common Twi words and their phoneme sequences
    COMMON_WORDS: Dict[str, List[str]] = {
        "agoo": ["a", "g", "o", "o"],
        "mepa": ["m", "e", "p", "a"],
        "wo": ["w", "o"],
        "kyɛw": ["ky", "ɛ", "w"],
        "ho": ["h", "o"],
        "te": ["t", "e"],
        "sɛn": ["s", "ɛ", "n"],
        "kalculus": ["k", "a", "l", "k", "u", "l", "u", "s"],
        "akwaaba": ["a", "kw", "a", "a", "b", "a"],
        "ɛte": ["ɛ", "t", "e"],
        "sɛn": ["s", "ɛ", "n"],
        "yɛ": ["y", "ɛ"],
        "da": ["d", "a"],
        "ase": ["a", "s", "e"],
        "me": ["m", "e"],
        "wo": ["w", "o"],
        "ne": ["n", "e"],
        "anaa": ["a", "n", "a", "a"],
        "ɔno": ["ɔ", "n", "o"],
        "ɛno": ["ɛ", "n", "o"],
        "na": ["n", "a"],
        "wɔ": ["w", "ɔ"],
        "hɔ": ["h", "ɔ"],
        "bra": ["b", "r", "a"],
        "kɔ": ["k", "ɔ"],
        "ba": ["b", "a"],
        "ma": ["m", "a"],
        "fa": ["f", "a"],
        "bɔ": ["b", "ɔ"],
        "di": ["d", "i"],
        "hwɛ": ["hw", "ɛ"],
        "ka": ["k", "a"],
        "pa": ["p", "a"],
        "so": ["s", "o"],
        "tu": ["t", "u"],
        "yi": ["y", "i"],
        "de": ["d", "e"],
        "fi": ["f", "i"],
        "hu": ["h", "u"],
        "su": ["s", "u"],
        "to": ["t", "o"],
        "twi": ["tw", "i"],
        "akan": ["a", "k", "a", "n"],
        "ghana": ["g", "a", "n", "a"],
        "asante": ["a", "s", "a", "n", "t", "e"],
        "fante": ["f", "a", "n", "t", "e"],
        "akuapem": ["a", "kw", "a", "p", "e", "m"],
    }
    
    # Fallback phoneme mapping for characters not in the phoneme set
    FALLBACK_MAPPING: Dict[str, str] = {
        "c": "k",  # Map 'c' to 'k'
        "j": "gy",  # Map 'j' to 'gy'
        "q": "kw",  # Map 'q' to 'kw'
        "v": "f",  # Map 'v' to 'f'
        "x": "ks",  # Map 'x' to 'ks'
        "z": "s",  # Map 'z' to 's'
    }
    
    def __init__(self, pronunciation_dict_path: Optional[str] = None):
        """
        Initialize the enhanced Twi G2P converter.
        
        Args:
            pronunciation_dict_path: Path to a pronunciation dictionary file.
                If provided, the dictionary will be loaded and used for G2P conversion.
        """
        self.tokenizer = TwiTokenizer()
        self.phonemes = TwiPhonemes
        
        # Pronunciation dictionary (word -> phoneme sequence)
        self.pronunciation_dict: Dict[str, List[str]] = self.COMMON_WORDS.copy()
        
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
        try:
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
            
            logger.info(f"Loaded {len(self.pronunciation_dict) - len(self.COMMON_WORDS)} additional words from pronunciation dictionary")
        except Exception as e:
            logger.error(f"Error loading pronunciation dictionary: {e}")
    
    def _handle_unknown_character(self, char: str) -> List[str]:
        """
        Handle an unknown character by mapping it to known phonemes.
        
        Args:
            char: The unknown character.
            
        Returns:
            A list of phonemes.
        """
        # Check if we have a fallback mapping
        if char.lower() in self.FALLBACK_MAPPING:
            fallback = self.FALLBACK_MAPPING[char.lower()]
            if len(fallback) == 1:
                return [fallback]
            else:
                return list(fallback)
        
        # For other characters, use the UNK token
        logger.warning(f"Unknown character: {char}")
        return [self.phonemes.UNK]
    
    def _apply_enhanced_g2p_rules(self, word: str) -> List[str]:
        """
        Apply enhanced Twi-specific G2P rules to convert a word to phonemes.
        
        Args:
            word: The Twi word to convert.
            
        Returns:
            A list of phonemes.
        """
        # First, try to tokenize the word into phonemes using the tokenizer
        phonemes = []
        i = 0
        
        while i < len(word):
            # Check for consonant clusters first
            if i < len(word) - 1:
                potential_cluster = word[i:i+2]
                if potential_cluster in self.tokenizer.CONSONANT_CLUSTERS:
                    # Found a consonant cluster
                    phonemes.append(potential_cluster)
                    i += 2
                    continue
            
            # Single character (consonant or vowel)
            char = word[i]
            
            # Check if the character is a valid phoneme
            if self.phonemes.is_valid_phoneme(char):
                phonemes.append(char)
            else:
                # Handle unknown character
                phonemes.extend(self._handle_unknown_character(char))
            
            i += 1
        
        # Apply additional Twi-specific G2P rules
        
        # Rule 1: Handle vowel sequences
        i = 0
        while i < len(phonemes):
            if (i < len(phonemes) - 1 and 
                self.phonemes.is_vowel(phonemes[i]) and 
                self.phonemes.is_vowel(phonemes[i+1])):
                # Two consecutive vowels - in Twi, these are typically pronounced separately
                # but we might want to add a glide or handle them specially
                # For now, we'll keep them as separate phonemes
                pass
            i += 1
        
        # Rule 2: Handle nasal sounds
        i = 0
        while i < len(phonemes):
            if (i < len(phonemes) - 1 and 
                self.phonemes.is_nasal(phonemes[i]) and 
                not self.phonemes.is_vowel(phonemes[i+1])):
                # Nasal followed by a consonant - in Twi, this often nasalizes the consonant
                # For now, we'll keep them as separate phonemes
                pass
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
        return self._apply_enhanced_g2p_rules(word)
    
    def text_to_phonemes(self, text: str) -> List[str]:
        """
        Convert Twi text to phonemes.
        
        Args:
            text: The Twi text to convert.
            
        Returns:
            A list of phonemes.
        """
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