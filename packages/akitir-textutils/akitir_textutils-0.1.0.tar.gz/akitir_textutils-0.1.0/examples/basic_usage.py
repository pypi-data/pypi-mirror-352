#!/usr/bin/env python3
"""
Basic usage examples for the textutils library.

This script demonstrates the core functionality of textutils
including text cleaning, validation, and formatting.
"""

from textutils import (
    clean_text,
    word_count,
    validate_email,
    validate_url,
    to_camel_case,
    to_snake_case,
    remove_html_tags,
)


def main():
    """Demonstrate basic textutils functionality."""
    print("=== TextUtils Basic Usage Examples ===\n")
    
    # Text cleaning examples
    print("1. Text Cleaning:")
    dirty_text = "  Hello,   World!  \n\t  Extra   spaces  "
    cleaned = clean_text(dirty_text)
    print(f"Original: '{dirty_text}'")
    print(f"Cleaned:  '{cleaned}'")
    print()
    
    # Word counting examples
    print("2. Word Counting:")
    sample_text = "The quick brown fox jumps over the lazy dog"
    count = word_count(sample_text)
    print(f"Text: '{sample_text}'")
    print(f"Word count: {count}")
    print()
    
    # Email validation examples
    print("3. Email Validation:")
    emails = [
        "user@example.com",
        "invalid.email",
        "test.email@domain.org",
        "not_an_email",
    ]
    
    for email in emails:
        is_valid = validate_email(email)
        print(f"'{email}' -> {'Valid' if is_valid else 'Invalid'}")
    print()
    
    # URL validation examples
    print("4. URL Validation:")
    urls = [
        "https://www.example.com",
        "http://subdomain.site.org/path",
        "www.example.com",
        "not_a_url",
    ]
    
    for url in urls:
        is_valid = validate_url(url)
        print(f"'{url}' -> {'Valid' if is_valid else 'Invalid'}")
    print()
    
    # Case conversion examples
    print("5. Case Conversion:")
    text = "Hello World Example"
    
    camel = to_camel_case(text)
    snake = to_snake_case(text)
    
    print(f"Original:   '{text}'")
    print(f"camelCase:  '{camel}'")
    print(f"snake_case: '{snake}'")
    print()
    
    # HTML tag removal examples
    print("6. HTML Tag Removal:")
    html_text = "<p>This is <b>bold</b> and <i>italic</i> text.</p>"
    clean_html = remove_html_tags(html_text)
    
    print(f"HTML:  '{html_text}'")
    print(f"Clean: '{clean_html}'")
    print()


if __name__ == "__main__":
    main()
