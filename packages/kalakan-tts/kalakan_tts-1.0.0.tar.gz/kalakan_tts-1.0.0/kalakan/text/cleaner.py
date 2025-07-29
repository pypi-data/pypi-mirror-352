"""
Text cleaning utilities for Twi language.

This module provides functions for cleaning Twi text, including removing
unwanted characters, handling special cases, and preparing text for TTS.
"""

import re
import unicodedata
from typing import List, Optional, Set


def remove_extra_whitespace(text: str) -> str:
    """
    Remove extra whitespace from text.
    
    Args:
        text: The text to clean.
        
    Returns:
        Text with normalized whitespace.
    """
    # Replace multiple spaces, tabs, and newlines with a single space
    return re.sub(r'\s+', ' ', text).strip()


def remove_non_twi_characters(text: str, keep_punctuation: bool = True) -> str:
    """
    Remove characters that are not used in Twi language.
    
    Args:
        text: The text to clean.
        keep_punctuation: Whether to keep punctuation marks.
        
    Returns:
        Text with only Twi characters and optionally punctuation.
    """
    # Define the set of valid Twi characters
    twi_chars = set('abcdefghijklmnopqrstuvwxyzɛɔƆ')
    
    # Add uppercase versions
    twi_chars.update('ABCDEFGHIJKLMNOPQRSTUVWXYZƐƆƆ')
    
    # Add diacritical marks for tones
    twi_chars.update('\u0300\u0301\u0302\u0303\u0304\u0308\u030C')
    
    # Add punctuation if requested
    if keep_punctuation:
        twi_chars.update('.,!?;:"\'\(\)\[\]\{\}-')
    
    # Add space
    twi_chars.add(' ')
    
    # Filter out non-Twi characters
    result = ''.join(c for c in text if c in twi_chars)
    
    return result


def normalize_unicode(text: str) -> str:
    """
    Normalize Unicode characters to their canonical form.
    
    Args:
        text: The text to normalize.
        
    Returns:
        Text with normalized Unicode characters.
    """
    return unicodedata.normalize('NFC', text)


def remove_urls(text: str) -> str:
    """
    Remove URLs from text.
    
    Args:
        text: The text to clean.
        
    Returns:
        Text with URLs removed.
    """
    # Simple URL pattern
    url_pattern = r'https?://\S+|www\.\S+'
    return re.sub(url_pattern, '', text)


def remove_html_tags(text: str) -> str:
    """
    Remove HTML tags from text.
    
    Args:
        text: The text to clean.
        
    Returns:
        Text with HTML tags removed.
    """
    return re.sub(r'<.*?>', '', text)


def remove_emojis(text: str) -> str:
    """
    Remove emojis from text.
    
    Args:
        text: The text to clean.
        
    Returns:
        Text with emojis removed.
    """
    # Pattern to match emojis
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251" 
        "]+"
    )
    return emoji_pattern.sub('', text)


def clean_text(text: str, 
               remove_urls_flag: bool = True,
               remove_html: bool = True,
               remove_emojis_flag: bool = True,
               keep_punctuation: bool = True) -> str:
    """
    Clean Twi text for TTS processing.
    
    This function applies various cleaning steps to prepare Twi text
    for TTS processing, including:
    - Removing URLs
    - Removing HTML tags
    - Removing emojis
    - Removing non-Twi characters
    - Normalizing whitespace
    - Normalizing Unicode characters
    
    Args:
        text: The Twi text to clean.
        remove_urls_flag: Whether to remove URLs.
        remove_html: Whether to remove HTML tags.
        remove_emojis_flag: Whether to remove emojis.
        keep_punctuation: Whether to keep punctuation marks.
        
    Returns:
        Cleaned Twi text.
    """
    # Convert to lowercase
    result = text.lower()
    
    # Remove URLs if requested
    if remove_urls_flag:
        result = remove_urls(result)
    
    # Remove HTML tags if requested
    if remove_html:
        result = remove_html_tags(result)
    
    # Remove emojis if requested
    if remove_emojis_flag:
        result = remove_emojis(result)
    
    # Normalize Unicode characters
    result = normalize_unicode(result)
    
    # Remove non-Twi characters
    result = remove_non_twi_characters(result, keep_punctuation)
    
    # Remove extra whitespace
    result = remove_extra_whitespace(result)
    
    return result