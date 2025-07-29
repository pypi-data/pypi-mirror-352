"""Tests for textutils.formatters module."""

import pytest
from textutils.formatters import (
    to_title_case,
    to_snake_case,
    to_camel_case,
    to_kebab_case,
    remove_html_tags,
    capitalize_words,
    remove_accents,
)


class TestToTitleCase:
    """Test cases for to_title_case function."""

    def test_to_title_case_basic(self):
        """Test basic title case conversion."""
        result = to_title_case("hello world")
        assert result == "Hello World"

    def test_to_title_case_already_title(self):
        """Test title case conversion on already title-cased text."""
        result = to_title_case("Hello World")
        assert result == "Hello World"

    def test_to_title_case_empty(self):
        """Test title case conversion on empty string."""
        result = to_title_case("")
        assert result == ""

    def test_to_title_case_invalid_input(self):
        """Test to_title_case with invalid input type."""
        with pytest.raises(TypeError):
            to_title_case(123)


class TestToSnakeCase:
    """Test cases for to_snake_case function."""

    def test_to_snake_case_spaces(self):
        """Test snake case conversion from spaces."""
        result = to_snake_case("Hello World")
        assert result == "hello_world"

    def test_to_snake_case_camel(self):
        """Test snake case conversion from camelCase."""
        result = to_snake_case("camelCaseText")
        assert result == "camel_case_text"

    def test_to_snake_case_pascal(self):
        """Test snake case conversion from PascalCase."""
        result = to_snake_case("PascalCaseText")
        assert result == "pascal_case_text"

    def test_to_snake_case_mixed(self):
        """Test snake case conversion from mixed format."""
        result = to_snake_case("mixed-Case_text")
        assert result == "mixed_case_text"

    def test_to_snake_case_invalid_input(self):
        """Test to_snake_case with invalid input type."""
        with pytest.raises(TypeError):
            to_snake_case(123)


class TestToCamelCase:
    """Test cases for to_camel_case function."""

    def test_to_camel_case_spaces(self):
        """Test camel case conversion from spaces."""
        result = to_camel_case("hello world")
        assert result == "helloWorld"

    def test_to_camel_case_snake(self):
        """Test camel case conversion from snake_case."""
        result = to_camel_case("snake_case_text")
        assert result == "snakeCaseText"

    def test_to_camel_case_kebab(self):
        """Test camel case conversion from kebab-case."""
        result = to_camel_case("kebab-case-text")
        assert result == "kebabCaseText"

    def test_to_camel_case_empty(self):
        """Test camel case conversion on empty string."""
        result = to_camel_case("")
        assert result == ""

    def test_to_camel_case_invalid_input(self):
        """Test to_camel_case with invalid input type."""
        with pytest.raises(TypeError):
            to_camel_case(123)


class TestToKebabCase:
    """Test cases for to_kebab_case function."""

    def test_to_kebab_case_spaces(self):
        """Test kebab case conversion from spaces."""
        result = to_kebab_case("Hello World")
        assert result == "hello-world"

    def test_to_kebab_case_camel(self):
        """Test kebab case conversion from camelCase."""
        result = to_kebab_case("camelCaseText")
        assert result == "camel-case-text"

    def test_to_kebab_case_snake(self):
        """Test kebab case conversion from snake_case."""
        result = to_kebab_case("snake_case_text")
        assert result == "snake-case-text"

    def test_to_kebab_case_invalid_input(self):
        """Test to_kebab_case with invalid input type."""
        with pytest.raises(TypeError):
            to_kebab_case(123)


class TestRemoveHtmlTags:
    """Test cases for remove_html_tags function."""

    def test_remove_html_tags_basic(self):
        """Test basic HTML tag removal."""
        result = remove_html_tags("<p>Hello <b>world</b></p>")
        assert result == "Hello world"

    def test_remove_html_tags_complex(self):
        """Test complex HTML tag removal."""
        html = '<div class="content"><h1>Title</h1><p>Paragraph with <a href="#">link</a></p></div>'
        result = remove_html_tags(html)
        assert result == "TitleParagraph with link"

    def test_remove_html_tags_entities(self):
        """Test HTML entity decoding."""
        result = remove_html_tags("Hello &amp; goodbye &lt;world&gt;")
        assert result == "Hello & goodbye <world>"

    def test_remove_html_tags_no_tags(self):
        """Test HTML tag removal on text without tags."""
        result = remove_html_tags("Plain text")
        assert result == "Plain text"

    def test_remove_html_tags_invalid_input(self):
        """Test remove_html_tags with invalid input type."""
        with pytest.raises(TypeError):
            remove_html_tags(123)


class TestCapitalizeWords:
    """Test cases for capitalize_words function."""

    def test_capitalize_words_basic(self):
        """Test basic word capitalization."""
        result = capitalize_words("the quick brown fox")
        assert result == "The Quick Brown Fox"

    def test_capitalize_words_with_exceptions(self):
        """Test word capitalization with exceptions."""
        result = capitalize_words("the quick brown fox", ["the", "of"])
        assert result == "The Quick Brown Fox"

    def test_capitalize_words_first_word_exception(self):
        """Test that first word is always capitalized even if in exceptions."""
        result = capitalize_words("the quick brown fox", ["the"])
        assert result == "The Quick Brown Fox"

    def test_capitalize_words_empty(self):
        """Test capitalize_words on empty string."""
        result = capitalize_words("")
        assert result == ""

    def test_capitalize_words_invalid_input(self):
        """Test capitalize_words with invalid input type."""
        with pytest.raises(TypeError):
            capitalize_words(123)


class TestRemoveAccents:
    """Test cases for remove_accents function."""

    def test_remove_accents_basic(self):
        """Test basic accent removal."""
        result = remove_accents("café résumé naïve")
        assert result == "cafe resume naive"

    def test_remove_accents_mixed(self):
        """Test accent removal with mixed characters."""
        result = remove_accents("Zürich über München")
        assert result == "Zurich uber Munchen"

    def test_remove_accents_no_accents(self):
        """Test accent removal on text without accents."""
        result = remove_accents("Hello World")
        assert result == "Hello World"

    def test_remove_accents_empty(self):
        """Test accent removal on empty string."""
        result = remove_accents("")
        assert result == ""

    def test_remove_accents_invalid_input(self):
        """Test remove_accents with invalid input type."""
        with pytest.raises(TypeError):
            remove_accents(123)
