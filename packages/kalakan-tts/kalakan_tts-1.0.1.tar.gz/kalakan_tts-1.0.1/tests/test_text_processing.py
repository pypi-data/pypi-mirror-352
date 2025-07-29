#!/usr/bin/env python3
"""
Test script for the text processing module.

This script tests the functionality of the text processing module
in the Kalakan TTS system.
"""

import os
import sys
import unittest

# Add parent directory to path to allow importing from kalakan
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kalakan.text.cleaner import clean_text
from kalakan.text.normalizer import normalize_text, normalize_numbers
from kalakan.text.phonemes import TwiPhonemes
from kalakan.text.tokenizer import TwiTokenizer
from kalakan.text.twi_g2p import TwiG2P


class TestTextProcessing(unittest.TestCase):
    """Test case for the text processing module."""
    
    def test_cleaner(self):
        """Test the text cleaner."""
        # Test basic cleaning
        text = "Hello, world! <html>test</html> https://example.com"
        cleaned_text = clean_text(text)
        self.assertNotIn("<html>", cleaned_text)
        self.assertNotIn("https://", cleaned_text)
        
        # Test with Twi text
        text = "Akwaaba! Wo ho te sɛn? 😊"
        cleaned_text = clean_text(text)
        self.assertIn("akwaaba", cleaned_text)
        self.assertIn("sɛn", cleaned_text)
        self.assertNotIn("😊", cleaned_text)
    
    def test_normalizer(self):
        """Test the text normalizer."""
        # Test number normalization
        text = "I have 3 apples and 5 oranges."
        normalized_text = normalize_numbers(text)
        self.assertNotIn("3", normalized_text)
        self.assertNotIn("5", normalized_text)
        
        # Test full normalization
        text = "Dr. Smith has 10 books."
        normalized_text = normalize_text(text)
        self.assertNotIn("Dr.", normalized_text)
        self.assertNotIn("10", normalized_text)
    
    def test_phonemes(self):
        """Test the phoneme system."""
        # Test vowel detection
        self.assertTrue(TwiPhonemes.is_vowel("a"))
        self.assertTrue(TwiPhonemes.is_vowel("ɛ"))
        self.assertFalse(TwiPhonemes.is_vowel("k"))
        
        # Test consonant detection
        self.assertTrue(TwiPhonemes.is_consonant("k"))
        self.assertTrue(TwiPhonemes.is_consonant("tw"))
        self.assertFalse(TwiPhonemes.is_consonant("a"))
        
        # Test phoneme validation
        self.assertTrue(TwiPhonemes.is_valid_phoneme("a"))
        self.assertTrue(TwiPhonemes.is_valid_phoneme("tw"))
        self.assertFalse(TwiPhonemes.is_valid_phoneme("x"))
        
        # Test phoneme conversion
        phoneme_sequence = TwiPhonemes.text_to_sequence("a b c")
        self.assertGreater(len(phoneme_sequence), 0)
        
        text = TwiPhonemes.sequence_to_text(phoneme_sequence)
        self.assertGreater(len(text), 0)
    
    def test_tokenizer(self):
        """Test the tokenizer."""
        tokenizer = TwiTokenizer()
        
        # Test tokenization
        text = "Akwaaba! Wo ho te sɛn?"
        tokens = tokenizer.tokenize(text)
        self.assertIn("akwaaba", tokens)
        self.assertIn("sɛn", tokens)
        self.assertIn("?", tokens)
        
        # Test word to syllables
        word = "akwaaba"
        syllables = tokenizer.word_to_syllables(word)
        self.assertGreater(len(syllables), 0)
        
        # Test word to phonemes
        phonemes = tokenizer.word_to_phonemes(word)
        self.assertGreater(len(phonemes), 0)
    
    def test_g2p(self):
        """Test the G2P converter."""
        g2p = TwiG2P()
        
        # Test word to phonemes
        word = "akwaaba"
        phonemes = g2p.word_to_phonemes(word)
        self.assertGreater(len(phonemes), 0)
        
        # Test text to phonemes
        text = "Akwaaba! Wo ho te sɛn?"
        phonemes = g2p.text_to_phonemes(text)
        self.assertGreater(len(phonemes), 0)
        
        # Test text to phoneme sequence
        phoneme_sequence = g2p.text_to_phoneme_sequence(text)
        self.assertGreater(len(phoneme_sequence), 0)


if __name__ == "__main__":
    unittest.main()