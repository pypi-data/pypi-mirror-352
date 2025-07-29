"""
Text validation utilities.

This module provides various text validation functions for common formats
like email addresses, URLs, phone numbers, and other text patterns.
"""

import re
from typing import Optional


def validate_email(email: str) -> bool:
    """
    Validate email address format using regex.
    
    Args:
        email (str): Email address to validate
        
    Returns:
        bool: True if email format is valid, False otherwise
        
    Raises:
        TypeError: If input is not a string
        
    Example:
        >>> validate_email("user@example.com")
        True
        >>> validate_email("invalid.email")
        False
    """
    if not isinstance(email, str):
        raise TypeError("Email must be a string")
    
    # RFC 5322 compliant email regex (simplified)
    # Reject consecutive dots in local part
    if '..' in email.split('@')[0] if '@' in email else email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str, require_scheme: bool = True) -> bool:
    """
    Validate URL format.
    
    Args:
        url (str): URL to validate
        require_scheme (bool): Whether to require http/https scheme
        
    Returns:
        bool: True if URL format is valid, False otherwise
        
    Raises:
        TypeError: If input is not a string
        
    Example:
        >>> validate_url("https://www.example.com")
        True
        >>> validate_url("www.example.com", require_scheme=False)
        True
    """
    if not isinstance(url, str):
        raise TypeError("URL must be a string")
    
    if require_scheme:
        pattern = r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$'
    else:
        pattern = r'^(?:https?://)?(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$'
    
    return bool(re.match(pattern, url))


def validate_phone(phone: str, country_code: str = 'US') -> bool:
    """
    Validate phone number format for specified country.
    
    Args:
        phone (str): Phone number to validate
        country_code (str): Country code for validation rules (default: 'US')
        
    Returns:
        bool: True if phone number format is valid, False otherwise
        
    Raises:
        TypeError: If inputs are not strings
        
    Example:
        >>> validate_phone("(555) 123-4567")
        True
        >>> validate_phone("+1-555-123-4567")
        True
    """
    if not isinstance(phone, str):
        raise TypeError("Phone number must be a string")
    
    if not isinstance(country_code, str):
        raise TypeError("Country code must be a string")
    
    # Remove common formatting characters
    cleaned_phone = re.sub(r'[\s\-\(\)\+\.]', '', phone)
    
    if country_code.upper() == 'US':
        # US phone number: 10 digits, optionally starting with 1
        if len(cleaned_phone) == 10 and cleaned_phone.isdigit():
            return True
        elif len(cleaned_phone) == 11 and cleaned_phone.startswith('1') and cleaned_phone[1:].isdigit():
            return True
        # Reject if too short for US
        if len(cleaned_phone) < 10:
            return False
    
    # Basic international format: 7-15 digits
    if 7 <= len(cleaned_phone) <= 15 and cleaned_phone.isdigit():
        return True
    
    return False


def is_palindrome(text: str, ignore_case: bool = True, 
                  ignore_spaces: bool = True) -> bool:
    """
    Check if text is a palindrome.
    
    Args:
        text (str): Text to check
        ignore_case (bool): Whether to ignore case differences
        ignore_spaces (bool): Whether to ignore spaces and punctuation
        
    Returns:
        bool: True if text is a palindrome, False otherwise
        
    Raises:
        TypeError: If input is not a string
        
    Example:
        >>> is_palindrome("A man a plan a canal Panama")
        True
        >>> is_palindrome("hello")
        False
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    
    processed_text = text
    
    if ignore_case:
        processed_text = processed_text.lower()
    
    if ignore_spaces:
        processed_text = re.sub(r'[^a-zA-Z0-9]', '', processed_text)
    
    return processed_text == processed_text[::-1]


def contains_only_letters(text: str) -> bool:
    """
    Check if text contains only alphabetic characters.
    
    Args:
        text (str): Text to check
        
    Returns:
        bool: True if text contains only letters, False otherwise
        
    Raises:
        TypeError: If input is not a string
        
    Example:
        >>> contains_only_letters("HelloWorld")
        True
        >>> contains_only_letters("Hello123")
        False
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    
    return text.isalpha()


def contains_only_digits(text: str) -> bool:
    """
    Check if text contains only numeric digits.
    
    Args:
        text (str): Text to check
        
    Returns:
        bool: True if text contains only digits, False otherwise
        
    Raises:
        TypeError: If input is not a string
        
    Example:
        >>> contains_only_digits("12345")
        True
        >>> contains_only_digits("123abc")
        False
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    
    return text.isdigit()
