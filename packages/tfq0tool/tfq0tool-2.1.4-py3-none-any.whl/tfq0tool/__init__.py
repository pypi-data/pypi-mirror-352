"""
TFQ0tool - A powerful text extraction utility for multiple file formats.

This package provides tools for extracting text from various file formats including
PDFs, Word documents, Excel files, and more, with support for parallel processing
and advanced text processing features.
"""

from .tfq0tool import main
version="2.1.4"
__author__ = "Talal"
__description__ = "A powerful command-line utility for extracting text from various file formats, including PDFs, Word documents, spreadsheets, and code files."
__all__ = ["TextExtractor", "FileProcessor", "utils"]