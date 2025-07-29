"""
Core text processing utilities.

This module contains fundamental text processing functions including
text cleaning, analysis, and basic manipulation operations.
"""

import re
import string
from typing import Dict, List, Union


def clean_text(text: str, remove_extra_spaces: bool = True, 
               remove_punctuation: bool = False) -> str:
    """
    Clean and normalize text by removing extra whitespace and optionally punctuation.
    
    Args:
        text (str): The input text to clean
        remove_extra_spaces (bool): Whether to remove extra spaces (default: True)
        remove_punctuation (bool): Whether to remove punctuation (default: False)
        
    Returns:
        str: The cleaned text
        
    Raises:
        TypeError: If input is not a string
        
    Example:
        >>> clean_text("  Hello,   World!  \\n")
        'Hello, World!'
        >>> clean_text("Hello, World!", remove_punctuation=True)
        'Hello World'
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Remove extra spaces if requested
    if remove_extra_spaces:
        text = re.sub(r'\s+', ' ', text)
    
    # Remove punctuation if requested
    if remove_punctuation:
        text = text.translate(str.maketrans('', '', string.punctuation))
        # Clean up extra spaces that might have been created
        text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def word_count(text: str) -> int:
    """
    Count the number of words in the given text.
    
    Args:
        text (str): The input text
        
    Returns:
        int: Number of words in the text
        
    Raises:
        TypeError: If input is not a string
        
    Example:
        >>> word_count("The quick brown fox jumps")
        5
        >>> word_count("")
        0
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    
    if not text.strip():
        return 0
    
    # Split by whitespace and filter out empty strings
    words = [word for word in text.split() if word]
    return len(words)


def character_frequency(text: str, case_sensitive: bool = False) -> Dict[str, int]:
    """
    Analyze character frequency in the given text.
    
    Args:
        text (str): The input text
        case_sensitive (bool): Whether to treat uppercase and lowercase as different
        
    Returns:
        dict: Dictionary mapping characters to their frequencies
        
    Raises:
        TypeError: If input is not a string
        
    Example:
        >>> character_frequency("hello")
        {'h': 1, 'e': 1, 'l': 2, 'o': 1}
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    
    if not case_sensitive:
        text = text.lower()
    
    frequency = {}
    for char in text:
        frequency[char] = frequency.get(char, 0) + 1
    
    return frequency


def extract_numbers(text: str) -> List[Union[int, float]]:
    """
    Extract all numbers (integers and floats) from text.
    
    Args:
        text (str): The input text
        
    Returns:
        list: List of numbers found in the text
        
    Raises:
        TypeError: If input is not a string
        
    Example:
        >>> extract_numbers("I have 5 apples and 2.5 oranges")
        [5, 2.5]
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    
    # Pattern to match integers and floats
    number_pattern = r'-?\d+\.?\d*'
    matches = re.findall(number_pattern, text)
    
    numbers = []
    for match in matches:
        try:
            # Try to convert to int first, then float
            if '.' in match:
                numbers.append(float(match))
            else:
                numbers.append(int(match))
        except ValueError:
            # Skip invalid matches
            continue
    
    return numbers


def reverse_words(text: str) -> str:
    """
    Reverse the order of words in the text.
    
    Args:
        text (str): The input text
        
    Returns:
        str: Text with words in reversed order
        
    Raises:
        TypeError: If input is not a string
        
    Example:
        >>> reverse_words("Hello world python")
        'python world Hello'
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    
    words = text.split()
    return ' '.join(reversed(words))


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length with optional suffix.
    
    Args:
        text (str): The input text
        max_length (int): Maximum length of the result
        suffix (str): Suffix to add when truncating (default: "...")
        
    Returns:
        str: Truncated text
        
    Raises:
        TypeError: If text is not a string or max_length is not an integer
        ValueError: If max_length is negative
        
    Example:
        >>> truncate_text("This is a long sentence", 10)
        'This is...'
    """
    if not isinstance(text, str):
        raise TypeError("Text must be a string")
    
    if not isinstance(max_length, int):
        raise TypeError("max_length must be an integer")
    
    if max_length < 0:
        raise ValueError("max_length must be non-negative")
    
    if len(text) <= max_length:
        return text
    
    if max_length <= len(suffix):
        return suffix[:max_length]
    
    return text[:max_length - len(suffix)] + suffix
