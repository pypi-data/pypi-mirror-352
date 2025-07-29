"""
Tokenizer for Twi text.

This module provides a tokenizer for Twi text, which handles the special
characters and linguistic features of the Twi language.
"""

import re
from typing import List, Optional, Set

from kalakan.text.phonemes import TwiPhonemes


class TwiTokenizer:
    """
    Tokenizer for Twi text.
    
    This class provides methods for tokenizing Twi text into words, syllables,
    and phonemes, handling the special characters and linguistic features of
    the Twi language.
    """
    
    # Regex patterns for tokenization
    WORD_PATTERN = r'[a-zA-ZɛɔƆ\u0300\u0301\u0302\u0303\u0304\u0308\u030C]+'
    PUNCTUATION_PATTERN = r'[.,!?;:"\'\(\)\[\]\{\}]'
    WHITESPACE_PATTERN = r'\s+'
    NUMBER_PATTERN = r'\d+'
    
    # Combined pattern for tokenization
    TOKEN_PATTERN = f"({WORD_PATTERN}|{PUNCTUATION_PATTERN}|{NUMBER_PATTERN}|{WHITESPACE_PATTERN})"
    
    # Consonant clusters in Twi
    CONSONANT_CLUSTERS: Set[str] = {
        'ky', 'gy', 'hy', 'ny', 'tw', 'dw', 'kw', 'gw', 'hw', 'nw'
    }
    
    def __init__(self):
        """Initialize the Twi tokenizer."""
        self.token_regex = re.compile(self.TOKEN_PATTERN)
        self.phonemes = TwiPhonemes
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize Twi text into words and punctuation.
        
        Args:
            text: The Twi text to tokenize.
            
        Returns:
            A list of tokens (words and punctuation).
        """
        # Convert to lowercase
        text = text.lower()
        
        # Find all tokens
        tokens = self.token_regex.findall(text)
        
        # Filter out whitespace tokens
        tokens = [token for token in tokens if not re.match(r'^\s+$', token)]
        
        return tokens
    
    def word_to_syllables(self, word: str) -> List[str]:
        """
        Split a Twi word into syllables.
        
        Twi syllable structure is typically CV (consonant-vowel) or V (vowel).
        Consonant clusters like 'ky', 'tw', etc. are treated as single consonants.
        
        Args:
            word: The Twi word to split into syllables.
            
        Returns:
            A list of syllables.
        """
        syllables = []
        i = 0
        
        while i < len(word):
            # Check for consonant clusters first
            if i < len(word) - 1:
                potential_cluster = word[i:i+2]
                if potential_cluster in self.CONSONANT_CLUSTERS:
                    # Found a consonant cluster
                    consonant = potential_cluster
                    i += 2
                else:
                    # Single consonant or vowel
                    consonant = word[i] if not self.phonemes.is_vowel(word[i]) else ''
                    i += 1 if consonant else 0
            else:
                # Last character
                consonant = word[i] if not self.phonemes.is_vowel(word[i]) else ''
                i += 1 if consonant else 0
            
            # Find the vowel(s)
            vowel = ''
            while i < len(word) and self.phonemes.is_vowel(word[i]):
                vowel += word[i]
                i += 1
            
            # If we have a consonant, a vowel, or both, add as a syllable
            if consonant or vowel:
                syllables.append(consonant + vowel)
        
        return syllables
    
    def word_to_phonemes(self, word: str) -> List[str]:
        """
        Convert a Twi word to a list of phonemes.
        
        Args:
            word: The Twi word to convert.
            
        Returns:
            A list of phonemes.
        """
        phonemes = []
        i = 0
        
        while i < len(word):
            # Check for consonant clusters first
            if i < len(word) - 1:
                potential_cluster = word[i:i+2]
                if potential_cluster in self.CONSONANT_CLUSTERS:
                    # Found a consonant cluster
                    phonemes.append(potential_cluster)
                    i += 2
                    continue
            
            # Single character (consonant or vowel)
            phonemes.append(word[i])
            i += 1
        
        return phonemes
    
    def text_to_phonemes(self, text: str) -> List[str]:
        """
        Convert Twi text to a list of phonemes.
        
        Args:
            text: The Twi text to convert.
            
        Returns:
            A list of phonemes.
        """
        tokens = self.tokenize(text)
        phonemes = []
        
        for token in tokens:
            # Skip punctuation and whitespace
            if re.match(f"^({self.PUNCTUATION_PATTERN}|{self.WHITESPACE_PATTERN})$", token):
                continue
                
            # Handle numbers (spell them out)
            if re.match(self.NUMBER_PATTERN, token):
                # For now, just add the digits as separate tokens
                # In a real implementation, this would convert numbers to Twi words
                for digit in token:
                    phonemes.extend(self.word_to_phonemes(digit))
            else:
                # Regular word
                phonemes.extend(self.word_to_phonemes(token))
        
        return phonemes
    
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