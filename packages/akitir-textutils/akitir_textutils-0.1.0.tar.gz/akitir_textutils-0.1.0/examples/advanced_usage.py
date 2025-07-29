#!/usr/bin/env python3
"""
Advanced usage examples for the textutils library.

This script demonstrates more advanced features including
character analysis, text manipulation, and complex formatting.
"""

from textutils import (
    character_frequency,
    extract_numbers,
    reverse_words,
    truncate_text,
    is_palindrome,
    to_kebab_case,
    capitalize_words,
    remove_accents,
    validate_phone,
)


def analyze_text(text):
    """Perform comprehensive text analysis."""
    print(f"Analyzing: '{text}'")
    print("-" * 50)
    
    # Basic stats
    word_count = len(text.split())
    char_count = len(text)
    
    print(f"Characters: {char_count}")
    print(f"Words: {word_count}")
    
    # Character frequency
    freq = character_frequency(text, case_sensitive=False)
    most_common = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:5]
    
    print(f"Most common characters: {most_common}")
    
    # Extract numbers
    numbers = extract_numbers(text)
    if numbers:
        print(f"Numbers found: {numbers}")
    
    # Check if palindrome
    if is_palindrome(text):
        print("✓ This text is a palindrome!")
    
    print()


def demonstrate_formatting():
    """Demonstrate various text formatting options."""
    print("=== Advanced Formatting Examples ===\n")
    
    # Case conversions with special cases
    texts = [
        "XMLHttpRequest",
        "iPhone_app_development",
        "user-interface-design",
        "API_KEY_CONSTANT",
    ]
    
    print("Case Conversion Examples:")
    for text in texts:
        kebab = to_kebab_case(text)
        print(f"'{text}' -> '{kebab}'")
    print()
    
    # Title capitalization with exceptions
    print("Smart Capitalization:")
    title = "the lord of the rings: the fellowship of the ring"
    articles = ["the", "of", "and", "or", "but", "a", "an"]
    
    smart_title = capitalize_words(title, exceptions=articles)
    print(f"Original: '{title}'")
    print(f"Smart:    '{smart_title}'")
    print()
    
    # Accent removal
    print("Accent Removal:")
    accented_texts = [
        "café au lait",
        "résumé and curriculum vitæ",
        "naïve señorita",
        "Zürich, Köln, München",
    ]
    
    for text in accented_texts:
        clean = remove_accents(text)
        print(f"'{text}' -> '{clean}'")
    print()


def demonstrate_validation():
    """Demonstrate advanced validation features."""
    print("=== Advanced Validation Examples ===\n")
    
    # Phone number validation
    print("Phone Number Validation:")
    phone_numbers = [
        "(555) 123-4567",
        "555-123-4567",
        "+1-555-123-4567",
        "123-456-7890",
        "invalid-phone",
        "555.123.4567",
    ]
    
    for phone in phone_numbers:
        is_valid = validate_phone(phone)
        print(f"'{phone}' -> {'Valid' if is_valid else 'Invalid'}")
    print()
    
    # Palindrome detection with options
    print("Palindrome Detection:")
    test_phrases = [
        "A man a plan a canal Panama",
        "race a car",
        "Was it a car or a cat I saw?",
        "hello world",
        "Madam",
    ]
    
    for phrase in test_phrases:
        is_pal = is_palindrome(phrase, ignore_case=True, ignore_spaces=True)
        print(f"'{phrase}' -> {'Palindrome' if is_pal else 'Not palindrome'}")
    print()


def demonstrate_text_manipulation():
    """Demonstrate text manipulation features."""
    print("=== Text Manipulation Examples ===\n")
    
    # Text truncation
    print("Text Truncation:")
    long_text = "This is a very long sentence that needs to be truncated for display purposes."
    
    for length in [20, 30, 50]:
        truncated = truncate_text(long_text, length)
        print(f"Max {length}: '{truncated}'")
    
    # Custom suffix
    custom_truncated = truncate_text(long_text, 25, " [more...]")
    print(f"Custom:  '{custom_truncated}'")
    print()
    
    # Word reversal
    print("Word Reversal:")
    sentences = [
        "Hello world from Python",
        "The quick brown fox",
        "Reverse these words please",
    ]
    
    for sentence in sentences:
        reversed_sentence = reverse_words(sentence)
        print(f"'{sentence}' -> '{reversed_sentence}'")
    print()


def main():
    """Run all advanced examples."""
    print("=== TextUtils Advanced Usage Examples ===\n")
    
    # Text analysis examples
    print("=== Text Analysis ===\n")
    sample_texts = [
        "Hello world! This has 123 numbers and special chars.",
        "racecar",
        "The quick brown fox jumps over the lazy dog 42 times!",
    ]
    
    for text in sample_texts:
        analyze_text(text)
    
    # Run other demonstrations
    demonstrate_formatting()
    demonstrate_validation()
    demonstrate_text_manipulation()
    
    print("=== Examples Complete ===")


if __name__ == "__main__":
    main()
