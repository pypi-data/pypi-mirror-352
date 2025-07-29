"""
Text formatting utilities.

This module provides various text formatting functions including
case conversion, HTML processing, and text normalization.
"""

import re
import unicodedata
from typing import Optional


def to_title_case(text: str) -> str:
    """
    Convert text to proper title case.
    
    Args:
        text (str): Text to convert
        
    Returns:
        str: Text in title case
        
    Raises:
        TypeError: If input is not a string
        
    Example:
        >>> to_title_case("hello world")
        'Hello World'
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    
    return text.title()


def to_snake_case(text: str) -> str:
    """
    Convert text to snake_case format.
    
    Args:
        text (str): Text to convert
        
    Returns:
        str: Text in snake_case format
        
    Raises:
        TypeError: If input is not a string
        
    Example:
        >>> to_snake_case("Hello World")
        'hello_world'
        >>> to_snake_case("CamelCaseText")
        'camel_case_text'
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    
    # Handle camelCase and PascalCase
    text = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', text)
    
    # Replace spaces and other separators with underscores
    text = re.sub(r'[\s\-\.]+', '_', text)
    
    # Remove special characters except underscores
    text = re.sub(r'[^\w]', '', text)
    
    return text.lower()


def to_camel_case(text: str) -> str:
    """
    Convert text to camelCase format.
    
    Args:
        text (str): Text to convert
        
    Returns:
        str: Text in camelCase format
        
    Raises:
        TypeError: If input is not a string
        
    Example:
        >>> to_camel_case("hello world")
        'helloWorld'
        >>> to_camel_case("snake_case_text")
        'snakeCaseText'
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    
    # Split on common separators
    words = re.split(r'[\s\-_\.]+', text)
    
    if not words:
        return ""
    
    # First word lowercase, rest title case
    camel_case = words[0].lower()
    for word in words[1:]:
        if word:
            camel_case += word.capitalize()
    
    return camel_case


def to_kebab_case(text: str) -> str:
    """
    Convert text to kebab-case format.
    
    Args:
        text (str): Text to convert
        
    Returns:
        str: Text in kebab-case format
        
    Raises:
        TypeError: If input is not a string
        
    Example:
        >>> to_kebab_case("Hello World")
        'hello-world'
        >>> to_kebab_case("CamelCaseText")
        'camel-case-text'
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    
    # Handle camelCase and PascalCase
    text = re.sub(r'([a-z0-9])([A-Z])', r'\1-\2', text)
    
    # Replace spaces and other separators with hyphens
    text = re.sub(r'[\s_\.]+', '-', text)
    
    # Remove special characters except hyphens
    text = re.sub(r'[^\w\-]', '', text)
    
    return text.lower()


def remove_html_tags(html: str) -> str:
    """
    Remove HTML tags from text while preserving content.
    
    Args:
        html (str): HTML text to clean
        
    Returns:
        str: Text with HTML tags removed
        
    Raises:
        TypeError: If input is not a string
        
    Example:
        >>> remove_html_tags("<p>Hello <b>world</b></p>")
        'Hello world'
    """
    if not isinstance(html, str):
        raise TypeError("Input must be a string")
    
    # Remove HTML tags
    clean_text = re.sub(r'<[^>]+>', '', html)
    
    # Decode common HTML entities
    html_entities = {
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&quot;': '"',
        '&#39;': "'",
        '&nbsp;': ' ',
    }
    
    for entity, char in html_entities.items():
        clean_text = clean_text.replace(entity, char)
    
    return clean_text.strip()


def capitalize_words(text: str, exceptions: Optional[list] = None) -> str:
    """
    Capitalize words in text with optional exceptions.
    
    Args:
        text (str): Text to capitalize
        exceptions (list, optional): List of words to keep lowercase
        
    Returns:
        str: Text with capitalized words
        
    Raises:
        TypeError: If input is not a string
        
    Example:
        >>> capitalize_words("the quick brown fox")
        'The Quick Brown Fox'
        >>> capitalize_words("the quick brown fox", ["the", "of"])
        'the Quick Brown Fox'
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    
    if exceptions is None:
        exceptions = []
    
    words = text.split()
    capitalized_words = []
    
    for i, word in enumerate(words):
        if i == 0:  # Always capitalize first word
            capitalized_words.append(word.capitalize())
        elif word.lower() not in exceptions:
            capitalized_words.append(word.capitalize())
        else:
            capitalized_words.append(word.lower())
    
    return ' '.join(capitalized_words)


def remove_accents(text: str) -> str:
    """
    Remove accents and diacritical marks from text.
    
    Args:
        text (str): Text with potential accents
        
    Returns:
        str: Text with accents removed
        
    Raises:
        TypeError: If input is not a string
        
    Example:
        >>> remove_accents("café résumé naïve")
        'cafe resume naive'
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    
    # Normalize unicode characters and remove combining characters
    normalized = unicodedata.normalize('NFD', text)
    ascii_text = normalized.encode('ascii', 'ignore').decode('ascii')
    
    return ascii_text
