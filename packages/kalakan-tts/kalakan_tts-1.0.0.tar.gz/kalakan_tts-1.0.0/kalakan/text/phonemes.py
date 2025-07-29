"""
Phoneme mapping for Twi language.

This module defines the phoneme set for Twi language and provides utilities
for working with Twi phonemes.
"""

from typing import Dict, List, Optional, Set


class TwiPhonemes:
    """
    Phoneme set and utilities for the Twi language.
    
    This class defines the phoneme inventory for Twi and provides methods
    for converting between graphemes and phonemes, checking phoneme validity,
    and other phoneme-related operations.
    
    Twi has special characters like ɛ, ɔ, Ɔ, and tonal markers that require
    special handling.
    """
    
    # Vowels in Twi
    VOWELS: Set[str] = {
        'a', 'e', 'ɛ', 'i', 'o', 'ɔ', 'u',  # Basic vowels
        'á', 'é', 'ɛ́', 'í', 'ó', 'ɔ́', 'ú',  # High tone vowels
        'à', 'è', 'ɛ̀', 'ì', 'ò', 'ɔ̀', 'ù',  # Low tone vowels
    }
    
    # Consonants in Twi
    CONSONANTS: Set[str] = {
        'b', 'd', 'f', 'g', 'h', 'k', 'l', 'm', 'n', 'p', 'r', 's', 't', 'w', 'y',
        'ky', 'gy', 'hy', 'ny', 'tw', 'dw', 'kw', 'gw', 'hw', 'nw',
    }
    
    # Nasal consonants
    NASALS: Set[str] = {'m', 'n', 'ny', 'nw'}
    
    # Phoneme to IPA mapping
    PHONEME_TO_IPA: Dict[str, str] = {
        'a': 'a', 'e': 'e', 'ɛ': 'ɛ', 'i': 'i', 'o': 'o', 'ɔ': 'ɔ', 'u': 'u',
        'b': 'b', 'd': 'd', 'f': 'f', 'g': 'g', 'h': 'h', 'k': 'k', 'l': 'l',
        'm': 'm', 'n': 'n', 'p': 'p', 'r': 'r', 's': 's', 't': 't', 'w': 'w', 'y': 'j',
        'ky': 'tʃ', 'gy': 'dʒ', 'hy': 'ç', 'ny': 'ɲ', 'tw': 'tɥ', 'dw': 'dɥ',
        'kw': 'kɥ', 'gw': 'gɥ', 'hw': 'ɥ', 'nw': 'ɲɥ',
        # Tonal markers
        'á': 'á', 'é': 'é', 'ɛ́': 'ɛ́', 'í': 'í', 'ó': 'ó', 'ɔ́': 'ɔ́', 'ú': 'ú',
        'à': 'à', 'è': 'è', 'ɛ̀': 'ɛ̀', 'ì': 'ì', 'ò': 'ò', 'ɔ̀': 'ɔ̀', 'ù': 'ù',
    }
    
    # IPA to phoneme mapping (reverse of PHONEME_TO_IPA)
    IPA_TO_PHONEME: Dict[str, str] = {v: k for k, v in PHONEME_TO_IPA.items()}
    
    # All phonemes
    ALL_PHONEMES: Set[str] = VOWELS.union(CONSONANTS)
    
    # Special symbols for TTS
    PAD: str = '_'
    EOS: str = '~'
    UNK: str = '?'
    
    # Special symbols set
    SPECIAL_SYMBOLS: Set[str] = {PAD, EOS, UNK}
    
    # Complete symbol set including phonemes and special symbols
    SYMBOLS: List[str] = sorted(list(ALL_PHONEMES.union(SPECIAL_SYMBOLS)))
    
    # Symbol to ID mapping
    SYMBOL_TO_ID: Dict[str, int] = {s: i for i, s in enumerate(SYMBOLS)}
    
    # ID to symbol mapping
    ID_TO_SYMBOL: Dict[int, str] = {i: s for i, s in enumerate(SYMBOLS)}
    
    @classmethod
    def is_vowel(cls, phoneme: str) -> bool:
        """
        Check if a phoneme is a vowel.
        
        Args:
            phoneme: The phoneme to check.
            
        Returns:
            True if the phoneme is a vowel, False otherwise.
        """
        return phoneme in cls.VOWELS
    
    @classmethod
    def is_consonant(cls, phoneme: str) -> bool:
        """
        Check if a phoneme is a consonant.
        
        Args:
            phoneme: The phoneme to check.
            
        Returns:
            True if the phoneme is a consonant, False otherwise.
        """
        return phoneme in cls.CONSONANTS
    
    @classmethod
    def is_nasal(cls, phoneme: str) -> bool:
        """
        Check if a phoneme is a nasal consonant.
        
        Args:
            phoneme: The phoneme to check.
            
        Returns:
            True if the phoneme is a nasal consonant, False otherwise.
        """
        return phoneme in cls.NASALS
    
    @classmethod
    def is_valid_phoneme(cls, phoneme: str) -> bool:
        """
        Check if a string is a valid Twi phoneme.
        
        Args:
            phoneme: The string to check.
            
        Returns:
            True if the string is a valid Twi phoneme, False otherwise.
        """
        return phoneme in cls.ALL_PHONEMES or phoneme in cls.SPECIAL_SYMBOLS
    
    @classmethod
    def to_ipa(cls, phoneme: str) -> str:
        """
        Convert a Twi phoneme to IPA (International Phonetic Alphabet).
        
        Args:
            phoneme: The Twi phoneme to convert.
            
        Returns:
            The IPA representation of the phoneme.
            
        Raises:
            ValueError: If the phoneme is not valid.
        """
        if not cls.is_valid_phoneme(phoneme):
            raise ValueError(f"Invalid Twi phoneme: {phoneme}")
        
        if phoneme in cls.SPECIAL_SYMBOLS:
            return phoneme  # Special symbols remain unchanged
        
        return cls.PHONEME_TO_IPA.get(phoneme, phoneme)
    
    @classmethod
    def from_ipa(cls, ipa: str) -> str:
        """
        Convert an IPA symbol to the corresponding Twi phoneme.
        
        Args:
            ipa: The IPA symbol to convert.
            
        Returns:
            The corresponding Twi phoneme.
            
        Raises:
            ValueError: If the IPA symbol does not correspond to a Twi phoneme.
        """
        if ipa in cls.SPECIAL_SYMBOLS:
            return ipa  # Special symbols remain unchanged
        
        if ipa not in cls.IPA_TO_PHONEME:
            raise ValueError(f"IPA symbol does not correspond to a Twi phoneme: {ipa}")
        
        return cls.IPA_TO_PHONEME[ipa]
    
    @classmethod
    def text_to_sequence(cls, text: str) -> List[int]:
        """
        Convert a string of phonemes to a sequence of phoneme IDs.
        
        Args:
            text: A string of space-separated phonemes.
            
        Returns:
            A list of phoneme IDs.
        """
        phonemes = text.split()
        sequence = []
        
        for phoneme in phonemes:
            if not cls.is_valid_phoneme(phoneme):
                phoneme = cls.UNK
            
            sequence.append(cls.SYMBOL_TO_ID[phoneme])
        
        # Add EOS token
        sequence.append(cls.SYMBOL_TO_ID[cls.EOS])
        
        return sequence
    
    @classmethod
    def sequence_to_text(cls, sequence: List[int]) -> str:
        """
        Convert a sequence of phoneme IDs to a string of phonemes.
        
        Args:
            sequence: A list of phoneme IDs.
            
        Returns:
            A string of space-separated phonemes.
        """
        phonemes = []
        
        for phoneme_id in sequence:
            if phoneme_id >= len(cls.ID_TO_SYMBOL):
                phoneme = cls.UNK
            else:
                phoneme = cls.ID_TO_SYMBOL[phoneme_id]
                
            if phoneme == cls.EOS:
                break
                
            phonemes.append(phoneme)
        
        return ' '.join(phonemes)
    
    @classmethod
    def get_tone(cls, vowel: str) -> Optional[str]:
        """
        Get the tone of a vowel.
        
        Args:
            vowel: The vowel to check.
            
        Returns:
            'high' for high tone, 'low' for low tone, None for neutral tone.
            
        Raises:
            ValueError: If the input is not a vowel.
        """
        if not cls.is_vowel(vowel):
            raise ValueError(f"Input is not a vowel: {vowel}")
        
        high_tone_vowels = {'á', 'é', 'ɛ́', 'í', 'ó', 'ɔ́', 'ú'}
        low_tone_vowels = {'à', 'è', 'ɛ̀', 'ì', 'ò', 'ɔ̀', 'ù'}
        
        if vowel in high_tone_vowels:
            return 'high'
        elif vowel in low_tone_vowels:
            return 'low'
        else:
            return None  # Neutral tone