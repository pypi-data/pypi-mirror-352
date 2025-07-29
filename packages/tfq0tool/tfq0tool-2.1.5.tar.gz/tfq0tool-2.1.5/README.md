# TFQ0tool

A command-line utility for extracting text from various file formats. Designed for simplicity and efficiency.

## Features

- **Format Support**:
  - PDF (with password protection)
  - Microsoft Office (DOCX, DOC, XLSX, XLS)
  - Data files (CSV, JSON, XML)
  - Text files (TXT, LOG, MD)

- **Processing Features**:
  - Parallel processing
  - Memory-efficient streaming
  - Text preprocessing (lowercase, whitespace removal)
  - Progress tracking
  - Automatic encoding detection

## Installation

```bash
pip install tfq0tool
```

## Usage

### Basic Commands

```bash
# Extract text from a file
tfq0tool extract document.pdf

# Extract to specific directory
tfq0tool extract document.pdf -o output_dir

# Process multiple files
tfq0tool extract *.pdf *.docx -o ./extracted

# Show supported formats
tfq0tool formats

# Show help
tfq0tool --help
```

### Extract Options

```bash
tfq0tool extract [OPTIONS] FILE_PATHS...

Options:
  -o, --output DIR    Output directory
  -t, --threads N     Thread count (default: auto)
  -f, --force        Overwrite existing files
  -p, --password PWD  PDF password
  --preprocess OPT    Preprocessing (lowercase,strip_whitespace)
  --progress         Show progress bar
  --verbose         Detailed output
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
tfq0tool extract document.pdf

# Multiple files with progress
tfq0tool extract *.pdf *.docx --progress -o ./output

# Process password-protected PDF
tfq0tool extract secure.pdf -p mypassword

# Extract with preprocessing
tfq0tool extract input.docx --preprocess lowercase,strip_whitespace

# Parallel processing
tfq0tool extract *.pdf -t 4 --progress
```

## License

MIT License - see LICENSE file for details.