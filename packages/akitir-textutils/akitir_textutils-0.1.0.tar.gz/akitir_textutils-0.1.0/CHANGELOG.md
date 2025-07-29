# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Nothing yet

### Changed
- Nothing yet

### Deprecated
- Nothing yet

### Removed
- Nothing yet

### Fixed
- Nothing yet

### Security
- Nothing yet

## [0.1.0] - 2024-01-01

### Added
- Initial release of textutils library
- Core text processing functions:
  - `clean_text()` - Text cleaning and normalization
  - `word_count()` - Word counting functionality
  - `character_frequency()` - Character frequency analysis
  - `extract_numbers()` - Number extraction from text
  - `reverse_words()` - Word order reversal
  - `truncate_text()` - Text truncation with customizable suffix
- Text validation functions:
  - `validate_email()` - Email address validation
  - `validate_url()` - URL format validation
  - `validate_phone()` - Phone number validation (US and international)
  - `is_palindrome()` - Palindrome detection
  - `contains_only_letters()` - Alphabetic character validation
  - `contains_only_digits()` - Numeric character validation
- Text formatting functions:
  - `to_title_case()` - Title case conversion
  - `to_snake_case()` - Snake case conversion
  - `to_camel_case()` - Camel case conversion
  - `to_kebab_case()` - Kebab case conversion
  - `remove_html_tags()` - HTML tag removal
  - `capitalize_words()` - Smart word capitalization with exceptions
  - `remove_accents()` - Accent and diacritical mark removal
- Comprehensive test suite with pytest
- Complete documentation with Sphinx
- Example scripts demonstrating usage
- Proper packaging configuration for PyPI
- Type hints for better IDE support
- Error handling and input validation

### Technical Details
- Python 3.7+ compatibility
- No external dependencies for core functionality
- Following PEP 8 style guidelines
- MIT License
- Comprehensive docstrings following Google style
- 95%+ test coverage
