Welcome to textutils documentation!
====================================

TextUtils is a comprehensive Python library for text processing utilities including validation, formatting, and manipulation functions.

Features
--------

* **Text Validation**: Email, URL, phone number validation
* **Text Formatting**: Case conversion, text cleaning, normalization  
* **Text Analysis**: Word count, character analysis, readability metrics
* **String Manipulation**: Advanced string operations and transformations

Quick Start
-----------

Installation::

    pip install textutils

Basic usage::

    from textutils import validate_email, clean_text, word_count

    # Email validation
    is_valid = validate_email("user@example.com")
    print(is_valid)  # True

    # Text cleaning
    cleaned = clean_text("  Hello,   World!  \n")
    print(cleaned)  # "Hello, World!"

    # Word counting
    count = word_count("The quick brown fox jumps")
    print(count)  # 5

Contents
--------

.. toctree::
   :maxdepth: 2

   api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
