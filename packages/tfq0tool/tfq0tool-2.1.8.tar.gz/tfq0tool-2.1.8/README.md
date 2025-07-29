# TFQ0tool

[![PyPI version](https://img.shields.io/pypi/v/tfq0tool.svg)](https://pypi.org/project/tfq0tool/)
[![License](https://img.shields.io/pypi/l/tfq0tool.svg)](https://github.com/tfq0/TFQ0tool/blob/main/LICENSE)
[![Python Versions](https://img.shields.io/pypi/pyversions/tfq0tool.svg)](https://pypi.org/project/tfq0tool/)
[![Downloads](https://img.shields.io/pypi/dm/tfq0tool.svg)](https://pypi.org/project/tfq0tool/)

A powerful command-line utility for extracting text from various file formats with advanced processing capabilities.

## Features

- **Format Support**:
  - PDF (with password protection and OCR support)
  - Microsoft Office (DOCX, DOC, XLSX, XLS)
  - Data files (CSV, JSON, XML)
  - Text files (TXT, LOG, MD)
  - Image files (via OCR)

- **Processing Features**:
  - Parallel processing with configurable threads
  - Memory-efficient streaming extraction
  - Advanced text preprocessing options
  - OCR support for images and scanned documents
  - Multiple output formats (TXT, JSON, CSV, MD)
  - Progress tracking and detailed logging
  - Automatic encoding detection
  - Language-specific processing

## Installation

```bash
pip install tfq0tool
```

## Usage

### Basic Commands

```bash
# Extract text from a file
tfq0tool extract document.pdf

# Show supported formats with details
tfq0tool formats --details

# Extract with OCR
tfq0tool extract scanned.pdf --ocr --ocr-lang eng

# Process multiple files recursively
tfq0tool extract ./docs/ -r --exclude "*.tmp"

# Show help
tfq0tool --help
```

### Extract Command Options

```bash
tfq0tool extract [OPTIONS] FILE_PATHS...

Input Options:
  FILE_PATHS          Files to process (supports glob patterns)
  -r, --recursive     Process directories recursively
  --exclude PATTERN   Exclude files matching pattern

Output Options:
  -o, --output DIR    Output directory
  --format FORMAT     Output format (txt|json|csv|md)
  --encoding ENC      Output encoding (default: utf-8)

Processing Options:
  -t, --threads N     Thread count (default: auto)
  -f, --force         Overwrite existing files
  -p, --password PWD  Password for encrypted PDFs

Text Processing Options:
  --preprocess OPT    Preprocessing options:
                      lowercase,strip_whitespace,
                      remove_numbers,remove_punctuation
  --language LANG     Language for processing (e.g., 'en')
  --ocr              Enable OCR for images/scanned docs
  --ocr-lang LANG    OCR language (default: eng)

Display Options:
  --verbose          Enable detailed output
  --progress         Show progress bar
  --silent          Suppress non-error output
```

### Configuration

View or modify settings:

```bash
# Show current config
tfq0tool config --show

# Reset to defaults
tfq0tool config --reset

# Change settings
tfq0tool config --set processing.chunk_size 2097152
tfq0tool config --set threading.max_threads 8
```

## Examples

```bash
# Basic text extraction
tfq0tool extract document.pdf -o ./output --format txt

# Process directory recursively with exclusions
tfq0tool extract ./docs -r --exclude "*.tmp" --progress

# Extract from scanned PDF with OCR
tfq0tool extract scan.pdf --ocr --ocr-lang eng

# Multiple files with advanced preprocessing
tfq0tool extract *.txt --preprocess lowercase,strip_whitespace,remove_numbers

# Parallel processing with custom output format
tfq0tool extract *.pdf -t 4 --format json --progress

# Extract with specific language and encoding
tfq0tool extract *.docx --language fr --encoding utf-8

# Password-protected PDF with OCR
tfq0tool extract secure.pdf -p mypassword --ocr
```

## Format Details

Use `tfq0tool formats --details` to see detailed information about supported formats, including:
- Supported features for each format
- Format-specific limitations
- Processing capabilities
- Best practices for extraction

