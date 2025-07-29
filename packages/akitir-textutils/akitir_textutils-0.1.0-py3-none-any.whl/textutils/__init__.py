"""
TextUtils: A comprehensive text processing utility library.

This library provides various text processing utilities including:
- Text validation (email, URL, phone numbers)
- Text formatting (case conversion, cleaning)
- Text analysis (word count, character frequency)
- String manipulation utilities

Example:
    >>> from textutils import validate_email, clean_text
    >>> validate_email("user@example.com")
    True
    >>> clean_text("  Hello,   World!  ")
    'Hello, World!'
"""

from .core import (
    clean_text,
    word_count,
    character_frequency,
    extract_numbers,
    reverse_words,
    truncate_text,
)

from .validators import (
    validate_email,
    validate_url,
    validate_phone,
    is_palindrome,
    contains_only_letters,
    contains_only_digits,
)

from .formatters import (
    to_title_case,
    to_snake_case,
    to_camel_case,
    to_kebab_case,
    remove_html_tags,
    capitalize_words,
    remove_accents,
)

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"
__description__ = "A comprehensive text processing utility library"

__all__ = [
    # Core functions
    "clean_text",
    "word_count",
    "character_frequency",
    "extract_numbers",
    "reverse_words",
    "truncate_text",
    # Validators
    "validate_email",
    "validate_url", 
    "validate_phone",
    "is_palindrome",
    "contains_only_letters",
    "contains_only_digits",
    # Formatters
    "to_title_case",
    "to_snake_case",
    "to_camel_case",
    "to_kebab_case",
    "remove_html_tags",
    "capitalize_words",
    "remove_accents",
]
