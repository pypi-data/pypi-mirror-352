# TFQ0tool

**A powerful command-line utility for extracting text from various file formats, including PDFs, Word documents, spreadsheets, and code files.**

[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI Version](https://img.shields.io/pypi/v/tfq0tool)](https://pypi.org/project/tfq0tool/)

## Features ✨

- 📂 **Multi-format Support**

- 🚀 **Advanced Processing**

- 📊 **Progress Tracking**

- 🛡️ **Robust Error Handling**

## Installation 💻

### From PyPI (Recommended)
```bash
pip install tfq0tool
```

### From Source
```bash
git clone https://github.com/tfq0/TFQ0tool.git
cd TFQ0tool
pip install -e .
```

## Usage 🛠️

### Basic Usage
```bash
# Process a single file
tfq0tool document.pdf

# Process multiple files
tfq0tool *.pdf *.docx

# Specify output directory
tfq0tool document.pdf --output ./extracted/

# Enable parallel processing
tfq0tool *.pdf --threads 4
```

### Advanced Options
```bash
# Password-protected PDF
tfq0tool secure.pdf --password mypass

# Text preprocessing
tfq0tool input.docx --preprocess lowercase,strip_whitespace

# Verbose output with progress
tfq0tool *.pdf --verbose

# Force overwrite existing files
tfq0tool data.xlsx --force
```

## Command-Line Options ⚙️

| Option | Description |
|--------|-------------|
| `-o, --output` | Output directory for extracted text |
| `-t, --threads` | Number of threads (default: 1) |
| `-v, --verbose` | Enable detailed output |
| `-f, --force` | Overwrite without confirmation |
| `-p, --password` | PDF password |
| `--preprocess` | Text preprocessing options |

## Text Preprocessing Options 🔧

- `lowercase`: Convert text to lowercase
- `strip_whitespace`: Remove excessive whitespace

## Requirements 📋

- Python 3.8 or higher




