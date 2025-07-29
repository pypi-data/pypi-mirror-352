"""Tests for textutils.core module."""

import pytest
from textutils.core import (
    clean_text,
    word_count,
    character_frequency,
    extract_numbers,
    reverse_words,
    truncate_text,
)


class TestCleanText:
    """Test cases for clean_text function."""

    def test_clean_text_basic(self):
        """Test basic text cleaning."""
        result = clean_text("  Hello,   World!  \n")
        assert result == "Hello, World!"

    def test_clean_text_remove_punctuation(self):
        """Test text cleaning with punctuation removal."""
        result = clean_text("Hello, World!", remove_punctuation=True)
        assert result == "Hello World"

    def test_clean_text_empty_string(self):
        """Test cleaning empty string."""
        result = clean_text("")
        assert result == ""

    def test_clean_text_invalid_input(self):
        """Test clean_text with invalid input type."""
        with pytest.raises(TypeError):
            clean_text(123)


class TestWordCount:
    """Test cases for word_count function."""

    def test_word_count_basic(self):
        """Test basic word counting."""
        result = word_count("The quick brown fox jumps")
        assert result == 5

    def test_word_count_empty_string(self):
        """Test word count of empty string."""
        result = word_count("")
        assert result == 0

    def test_word_count_whitespace_only(self):
        """Test word count of whitespace-only string."""
        result = word_count("   \n\t  ")
        assert result == 0

    def test_word_count_single_word(self):
        """Test word count of single word."""
        result = word_count("hello")
        assert result == 1

    def test_word_count_invalid_input(self):
        """Test word_count with invalid input type."""
        with pytest.raises(TypeError):
            word_count(123)


class TestCharacterFrequency:
    """Test cases for character_frequency function."""

    def test_character_frequency_basic(self):
        """Test basic character frequency analysis."""
        result = character_frequency("hello")
        expected = {'h': 1, 'e': 1, 'l': 2, 'o': 1}
        assert result == expected

    def test_character_frequency_case_sensitive(self):
        """Test character frequency with case sensitivity."""
        result = character_frequency("Hello", case_sensitive=True)
        expected = {'H': 1, 'e': 1, 'l': 2, 'o': 1}
        assert result == expected

    def test_character_frequency_empty_string(self):
        """Test character frequency of empty string."""
        result = character_frequency("")
        assert result == {}

    def test_character_frequency_invalid_input(self):
        """Test character_frequency with invalid input type."""
        with pytest.raises(TypeError):
            character_frequency(123)


class TestExtractNumbers:
    """Test cases for extract_numbers function."""

    def test_extract_numbers_basic(self):
        """Test basic number extraction."""
        result = extract_numbers("I have 5 apples and 2.5 oranges")
        assert result == [5, 2.5]

    def test_extract_numbers_negative(self):
        """Test extraction of negative numbers."""
        result = extract_numbers("Temperature is -10 degrees")
        assert result == [-10]

    def test_extract_numbers_no_numbers(self):
        """Test extraction when no numbers are present."""
        result = extract_numbers("No numbers here")
        assert result == []

    def test_extract_numbers_invalid_input(self):
        """Test extract_numbers with invalid input type."""
        with pytest.raises(TypeError):
            extract_numbers(123)


class TestReverseWords:
    """Test cases for reverse_words function."""

    def test_reverse_words_basic(self):
        """Test basic word reversal."""
        result = reverse_words("Hello world python")
        assert result == "python world Hello"

    def test_reverse_words_single_word(self):
        """Test reversal of single word."""
        result = reverse_words("hello")
        assert result == "hello"

    def test_reverse_words_empty_string(self):
        """Test reversal of empty string."""
        result = reverse_words("")
        assert result == ""

    def test_reverse_words_invalid_input(self):
        """Test reverse_words with invalid input type."""
        with pytest.raises(TypeError):
            reverse_words(123)


class TestTruncateText:
    """Test cases for truncate_text function."""

    def test_truncate_text_basic(self):
        """Test basic text truncation."""
        result = truncate_text("This is a long sentence", 10)
        assert result == "This is..."

    def test_truncate_text_no_truncation_needed(self):
        """Test when no truncation is needed."""
        result = truncate_text("Short", 10)
        assert result == "Short"

    def test_truncate_text_custom_suffix(self):
        """Test truncation with custom suffix."""
        result = truncate_text("Long text here", 8, "[...]")
        assert result == "Lon[...]"

    def test_truncate_text_invalid_length(self):
        """Test truncation with negative length."""
        with pytest.raises(ValueError):
            truncate_text("text", -1)

    def test_truncate_text_invalid_input_type(self):
        """Test truncate_text with invalid input types."""
        with pytest.raises(TypeError):
            truncate_text(123, 10)
        
        with pytest.raises(TypeError):
            truncate_text("text", "10")
