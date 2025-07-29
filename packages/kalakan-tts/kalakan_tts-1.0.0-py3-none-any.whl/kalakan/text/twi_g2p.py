"""
Grapheme-to-Phoneme (G2P) conversion for Twi language.

This module provides a G2P converter for Twi language, which converts
Twi text (graphemes) to phonemes for TTS processing.
"""

import os
import re
from typing import Dict, List, Optional, Set, Tuple

from kalakan.text.phonemes import TwiPhonemes
from kalakan.text.tokenizer import TwiTokenizer


class TwiG2P:
    """
    Grapheme-to-Phoneme (G2P) converter for Twi language.
    
    This class provides methods for converting Twi text (graphemes) to
    phonemes for TTS processing. It handles the special characters and
    linguistic features of the Twi language.
    """
    
    def __init__(self, pronunciation_dict_path: Optional[str] = None):
        """
        Initialize the Twi G2P converter.
        
        Args:
            pronunciation_dict_path: Path to a pronunciation dictionary file.
                If provided, the dictionary will be loaded and used for G2P conversion.
        """
        self.tokenizer = TwiTokenizer()
        self.phonemes = TwiPhonemes
        
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
    
    def _apply_twi_g2p_rules(self, word: str) -> List[str]:
        """
        Apply Twi-specific G2P rules to convert a word to phonemes.
        
        Args:
            word: The Twi word to convert.
            
        Returns:
            A list of phonemes.
        """
        # First, try to tokenize the word into phonemes using the tokenizer
        phonemes = self.tokenizer.word_to_phonemes(word)
        
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
        
        # Rule 3: Handle tone marks
        # Tone marks are already part of the vowel characters in our phoneme set,
        # so no additional processing is needed here
        
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
        
        # Apply Twi G2P rules
        return self._apply_twi_g2p_rules(word)
    
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