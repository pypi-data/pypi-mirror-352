"""Tests for textutils.validators module."""

import pytest
from textutils.validators import (
    validate_email,
    validate_url,
    validate_phone,
    is_palindrome,
    contains_only_letters,
    contains_only_digits,
)


class TestValidateEmail:
    """Test cases for validate_email function."""

    def test_validate_email_valid(self):
        """Test validation of valid email addresses."""
        valid_emails = [
            "user@example.com",
            "test.email@domain.org",
            "user+tag@example.co.uk",
            "123@example.com",
        ]
        for email in valid_emails:
            assert validate_email(email) is True

    def test_validate_email_invalid(self):
        """Test validation of invalid email addresses."""
        invalid_emails = [
            "invalid.email",
            "@example.com",
            "user@",
            "user@.com",
            "user..name@example.com",
        ]
        for email in invalid_emails:
            assert validate_email(email) is False

    def test_validate_email_invalid_input(self):
        """Test validate_email with invalid input type."""
        with pytest.raises(TypeError):
            validate_email(123)


class TestValidateUrl:
    """Test cases for validate_url function."""

    def test_validate_url_valid_with_scheme(self):
        """Test validation of valid URLs with scheme."""
        valid_urls = [
            "https://www.example.com",
            "http://example.org",
            "https://subdomain.example.com/path",
        ]
        for url in valid_urls:
            assert validate_url(url) is True

    def test_validate_url_valid_without_scheme(self):
        """Test validation of URLs without scheme."""
        url = "www.example.com"
        assert validate_url(url, require_scheme=False) is True
        assert validate_url(url, require_scheme=True) is False

    def test_validate_url_invalid(self):
        """Test validation of invalid URLs."""
        invalid_urls = [
            "not_a_url",
            "http://",
            "https://",
        ]
        for url in invalid_urls:
            assert validate_url(url) is False

    def test_validate_url_invalid_input(self):
        """Test validate_url with invalid input type."""
        with pytest.raises(TypeError):
            validate_url(123)


class TestValidatePhone:
    """Test cases for validate_phone function."""

    def test_validate_phone_us_format(self):
        """Test validation of US phone numbers."""
        valid_phones = [
            "(555) 123-4567",
            "555-123-4567",
            "5551234567",
            "+1-555-123-4567",
            "1-555-123-4567",
        ]
        for phone in valid_phones:
            assert validate_phone(phone) is True

    def test_validate_phone_invalid(self):
        """Test validation of invalid phone numbers."""
        invalid_phones = [
            "123",
            "abc-def-ghij",
            "555-123-456",  # Too short
        ]
        for phone in invalid_phones:
            assert validate_phone(phone) is False

    def test_validate_phone_international(self):
        """Test validation of international phone numbers."""
        # Basic international format validation
        phone = "1234567890"  # 10 digits
        assert validate_phone(phone) is True

    def test_validate_phone_invalid_input(self):
        """Test validate_phone with invalid input types."""
        with pytest.raises(TypeError):
            validate_phone(123)
        
        with pytest.raises(TypeError):
            validate_phone("123", 123)


class TestIsPalindrome:
    """Test cases for is_palindrome function."""

    def test_is_palindrome_true(self):
        """Test palindrome detection for true cases."""
        palindromes = [
            "racecar",
            "A man a plan a canal Panama",
            "race a ecar",  # With ignore_spaces=True
        ]
        for text in palindromes:
            assert is_palindrome(text) is True

    def test_is_palindrome_false(self):
        """Test palindrome detection for false cases."""
        non_palindromes = [
            "hello",
            "python",
            "not a palindrome",
        ]
        for text in non_palindromes:
            assert is_palindrome(text) is False

    def test_is_palindrome_case_sensitive(self):
        """Test palindrome detection with case sensitivity."""
        text = "Aa"
        assert is_palindrome(text, ignore_case=True) is True
        assert is_palindrome(text, ignore_case=False) is False

    def test_is_palindrome_invalid_input(self):
        """Test is_palindrome with invalid input type."""
        with pytest.raises(TypeError):
            is_palindrome(123)


class TestContainsOnlyLetters:
    """Test cases for contains_only_letters function."""

    def test_contains_only_letters_true(self):
        """Test detection of text with only letters."""
        letter_texts = [
            "HelloWorld",
            "abcdef",
            "XYZ",
        ]
        for text in letter_texts:
            assert contains_only_letters(text) is True

    def test_contains_only_letters_false(self):
        """Test detection of text with non-letters."""
        non_letter_texts = [
            "Hello123",
            "text with spaces",
            "hello!",
            "123",
        ]
        for text in non_letter_texts:
            assert contains_only_letters(text) is False

    def test_contains_only_letters_empty(self):
        """Test contains_only_letters with empty string."""
        assert contains_only_letters("") is False

    def test_contains_only_letters_invalid_input(self):
        """Test contains_only_letters with invalid input type."""
        with pytest.raises(TypeError):
            contains_only_letters(123)


class TestContainsOnlyDigits:
    """Test cases for contains_only_digits function."""

    def test_contains_only_digits_true(self):
        """Test detection of text with only digits."""
        digit_texts = [
            "12345",
            "0",
            "999",
        ]
        for text in digit_texts:
            assert contains_only_digits(text) is True

    def test_contains_only_digits_false(self):
        """Test detection of text with non-digits."""
        non_digit_texts = [
            "123abc",
            "12.34",
            "1 2 3",
            "hello",
        ]
        for text in non_digit_texts:
            assert contains_only_digits(text) is False

    def test_contains_only_digits_empty(self):
        """Test contains_only_digits with empty string."""
        assert contains_only_digits("") is False

    def test_contains_only_digits_invalid_input(self):
        """Test contains_only_digits with invalid input type."""
        with pytest.raises(TypeError):
            contains_only_digits(123)
