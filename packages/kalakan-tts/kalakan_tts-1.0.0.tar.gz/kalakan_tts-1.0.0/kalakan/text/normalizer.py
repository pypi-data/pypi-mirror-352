"""
Text normalization for Twi language.

This module provides functions for normalizing Twi text, including handling
numbers, abbreviations, and special characters.
"""

import re
from typing import Dict, List, Tuple


# Twi number words
TWI_NUMBERS: Dict[int, str] = {
    0: "hwee",
    1: "baako",
    2: "mmienu",
    3: "mmiɛnsa",
    4: "nnan",
    5: "nnum",
    6: "nsia",
    7: "nson",
    8: "nwɔtwe",
    9: "nkron",
    10: "du",
    20: "aduonu",
    30: "aduasa",
    40: "aduanan",
    50: "aduonum",
    60: "aduosia",
    70: "aduoson",
    80: "aduowɔtwe",
    90: "aduɔkron",
    100: "ɔha",
    1000: "apem",
    1000000: "ɔpepem",
}

# Common Twi abbreviations
TWI_ABBREVIATIONS: Dict[str, str] = {
    "Dr.": "dɔkta",
    "Mr.": "owura",
    "Mrs.": "maame",
    "Prof.": "ɔbenfoɔ",
    "etc.": "ne nkaa",
    "e.g.": "sɛ",
    "i.e.": "ɛno ne",
}


def normalize_numbers(text: str) -> str:
    """
    Convert numbers in text to their Twi word equivalents.

    Args:
        text: The text containing numbers to normalize.

    Returns:
        Text with numbers converted to Twi words.
    """
    # Find all numbers in the text
    number_matches = re.finditer(r'\b\d+\b', text)

    # Replace each number with its Twi equivalent, starting from the end
    # to avoid index issues
    result = text
    for match in reversed(list(number_matches)):
        number = int(match.group())
        start, end = match.span()

        # Convert the number to Twi
        twi_number = number_to_twi(number)

        # Replace the number with its Twi equivalent
        result = result[:start] + twi_number + result[end:]

    return result


def number_to_twi(number: int) -> str:
    """
    Convert a number to its Twi word equivalent.

    Args:
        number: The number to convert.

    Returns:
        The Twi word representation of the number.
    """
    if number in TWI_NUMBERS:
        return TWI_NUMBERS[number]

    # Handle numbers not in the dictionary
    if number < 100:
        # Numbers between 11-99
        tens = (number // 10) * 10
        ones = number % 10

        if ones == 0:
            return TWI_NUMBERS[tens]
        else:
            return f"{TWI_NUMBERS[tens]} {TWI_NUMBERS[ones]}"

    elif number < 1000:
        # Numbers between 100-999
        hundreds = number // 100
        remainder = number % 100

        if hundreds == 1:
            hundreds_text = TWI_NUMBERS[100]
        else:
            hundreds_text = f"{TWI_NUMBERS[hundreds]} {TWI_NUMBERS[100]}"

        if remainder == 0:
            return hundreds_text
        else:
            return f"{hundreds_text} ne {number_to_twi(remainder)}"

    elif number < 1000000:
        # Numbers between 1,000-999,999
        thousands = number // 1000
        remainder = number % 1000

        if thousands == 1:
            thousands_text = TWI_NUMBERS[1000]
        else:
            thousands_text = f"{number_to_twi(thousands)} {TWI_NUMBERS[1000]}"

        if remainder == 0:
            return thousands_text
        else:
            return f"{thousands_text} ne {number_to_twi(remainder)}"

    else:
        # Numbers >= 1,000,000
        millions = number // 1000000
        remainder = number % 1000000

        if millions == 1:
            millions_text = TWI_NUMBERS[1000000]
        else:
            millions_text = f"{number_to_twi(millions)} {TWI_NUMBERS[1000000]}"

        if remainder == 0:
            return millions_text
        else:
            return f"{millions_text} ne {number_to_twi(remainder)}"


def normalize_abbreviations(text: str) -> str:
    """
    Expand abbreviations in text to their full Twi equivalents.

    Args:
        text: The text containing abbreviations to normalize.

    Returns:
        Text with abbreviations expanded to their Twi equivalents.
    """
    result = text

    # Sort abbreviations by length (longest first) to avoid partial matches
    sorted_abbrevs = sorted(TWI_ABBREVIATIONS.keys(), key=len, reverse=True)

    for abbrev in sorted_abbrevs:
        # Use lookahead/lookbehind for better word boundary detection with punctuation
        escaped_abbrev = re.escape(abbrev)
        pattern = r'(?<!\w)' + escaped_abbrev + r'(?=\s|$)'
        result = re.sub(pattern, TWI_ABBREVIATIONS[abbrev], result)

    return result


def normalize_punctuation(text: str) -> str:
    """
    Normalize punctuation in text for TTS processing.

    Args:
        text: The text containing punctuation to normalize.

    Returns:
        Text with normalized punctuation.
    """
    # Replace multiple spaces with a single space
    result = re.sub(r'\s+', ' ', text)

    # Add space after punctuation if not already present
    result = re.sub(r'([.,!?;:])(\S)', r'\1 \2', result)

    # Remove space before punctuation
    result = re.sub(r'\s+([.,!?;:])', r'\1', result)

    # Normalize quotes (using simple replacements instead of character sets)
    result = result.replace('"', '"').replace('"', '"')
    result = result.replace("'", "'").replace("'", "'")

    # Normalize dashes (using simple replacements instead of character sets)
    result = result.replace('–', '-').replace('—', '-')

    return result


def normalize_text(text: str) -> str:
    """
    Normalize Twi text for TTS processing.

    This function applies various normalization steps to prepare Twi text
    for TTS processing, including:
    - Expanding abbreviations
    - Converting numbers to words
    - Normalizing punctuation
    - Handling special characters

    Args:
        text: The Twi text to normalize.

    Returns:
        Normalized Twi text.
    """
    # Convert to lowercase
    result = text.lower()

    # Normalize punctuation
    result = normalize_punctuation(result)

    # Expand abbreviations
    result = normalize_abbreviations(result)

    # Convert numbers to words
    result = normalize_numbers(result)

    # Normalize special characters
    # Ensure consistent representation of special Twi characters
    result = result.replace('ε', 'ɛ')  # Normalize epsilon
    result = result.replace('Ε', 'Ɛ')  # Normalize capital epsilon
    result = result.replace('ο', 'ɔ')  # Normalize open o
    result = result.replace('Ο', 'Ɔ')  # Normalize capital open o

    # Trim whitespace
    result = result.strip()

    return result