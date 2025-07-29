"""Main entry point for the TFQ0tool package."""

import argparse
import sys
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
import json

from .processor import FileProcessor
from .utils import setup_logging
from .config import config, DEFAULT_CONFIG

logger = logging.getLogger(__name__)

def create_parser() -> argparse.ArgumentParser:
    """Create and return the argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        description="""
TFQ0tool: A powerful text extraction utility for multiple file formats.

This tool provides advanced text extraction capabilities with features including:
- Support for multiple document formats (PDF, DOCX, XLSX, etc.)
- OCR support for images and scanned documents
- Parallel processing for improved performance
- Advanced text preprocessing options
- Multiple output formats
- Configurable processing options
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic text extraction
  tfq0tool extract document.pdf -o ./output

  # Process with OCR
  tfq0tool extract scan.pdf --ocr --ocr-lang eng

  # Batch processing with preprocessing
  tfq0tool extract *.txt --preprocess lowercase,strip_whitespace

For more examples and detailed documentation, visit:
https://github.com/tfq0/TFQ0tool
"""
    )
    
    # Add version information
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'%(prog)s {config.get("version")}',
        help="Show program's version number and exit"
    )
    
    # Create subcommands
    subparsers = parser.add_subparsers(
        dest='command',
        title='Available Commands',
        description='Choose a command to execute:',
        help='Command to execute',
        metavar='COMMAND'
    )
    
    # Extract command
    extract_parser = subparsers.add_parser(
        'extract',
        help='Extract text from files',
        description="""
Extract text from various file formats with customizable options.

This command supports:
- Multiple input formats (PDF, DOCX, XLSX, etc.)
- OCR for images and scanned documents
- Parallel processing
- Text preprocessing
- Multiple output formats
- Progress tracking
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic extraction
  tfq0tool extract document.pdf

  # Multiple files with OCR
  tfq0tool extract *.pdf --ocr --progress

  # Advanced preprocessing
  tfq0tool extract docs/*.txt --preprocess lowercase,strip_whitespace --format json
"""
    )
    _add_extract_arguments(extract_parser)
    
    # Config command
    config_parser = subparsers.add_parser(
        'config',
        help='Manage configuration settings',
        description="""
View or modify TFQ0tool configuration settings.

The configuration system allows you to:
- View current settings
- Reset to default values
- Modify individual settings
- Configure processing parameters
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show current settings
  tfq0tool config --show

  # Reset to defaults
  tfq0tool config --reset

  # Modify settings
  tfq0tool config --set processing.chunk_size 2097152
"""
    )
    _add_config_arguments(config_parser)
    
    # List formats command
    formats_parser = subparsers.add_parser(
        'formats',
        help='List supported file formats',
        description="""
Display detailed information about supported file formats.

This command shows:
- Supported file formats by category
- Format-specific features
- Processing capabilities
- Known limitations
- Best practices
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show basic format list
  tfq0tool formats

  # Show detailed information
  tfq0tool formats --details
"""
    )
    formats_parser.add_argument(
        '--details',
        action='store_true',
        help='Show detailed information about each format including features and limitations'
    )
    
    return parser

def _add_extract_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments for the extract command."""
    input_group = parser.add_argument_group(
        'Input Options',
        'Options for specifying input files and processing scope:'
    )
    input_group.add_argument(
        "file_paths",
        nargs='+',
        help="""Path(s) to the file(s) for text extraction.
Supports glob patterns (e.g., *.pdf) and multiple files/patterns.
When used with --recursive, processes matching files in subdirectories."""
    )
    input_group.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="""Recursively process directories.
When enabled, searches for matching files in all subdirectories."""
    )
    input_group.add_argument(
        "--exclude",
        type=str,
        help="""Glob pattern for files to exclude.
Example: --exclude "*.tmp" excludes all .tmp files.
Can be used with --recursive to filter subdirectories."""
    )
    
    output_group = parser.add_argument_group(
        'Output Options',
        'Options for controlling output format and location:'
    )
    output_group.add_argument(
        "-o", "--output",
        type=str,
        help="""Output directory for extracted text files.
If not specified, creates files in the same directory as input.
Directory will be created if it doesn't exist."""
    )
    output_group.add_argument(
        "--format",
        choices=['txt', 'json', 'csv', 'md'],
        default='txt',
        help="""Output format for extracted text:
- txt: Plain text (default)
- json: Structured JSON with metadata
- csv: Comma-separated values
- md: Markdown with formatting"""
    )
    output_group.add_argument(
        "--encoding",
        type=str,
        default='utf-8',
        help="""Output file encoding (default: utf-8).
Common options: utf-8, ascii, latin1, utf-16.
Uses system default if not specified."""
    )
    
    process_group = parser.add_argument_group(
        'Processing Options',
        'Options for controlling how files are processed:'
    )
    process_group.add_argument(
        "-t", "--threads",
        type=int,
        help=f"""Number of threads for parallel processing.
Default: Automatic based on CPU cores
Minimum: {config.get('threading', 'min_threads')}
Maximum: {config.get('threading', 'max_threads')}"""
    )
    process_group.add_argument(
        "-f", "--force",
        action="store_true",
        help="""Overwrite existing output files without prompting.
By default, existing files are not overwritten."""
    )
    process_group.add_argument(
        "-p", "--password",
        type=str,
        help="""Password for encrypted PDF files.
Required only for password-protected PDFs.
Can be combined with --ocr for protected scanned PDFs."""
    )
    
    preprocess_group = parser.add_argument_group(
        'Text Processing Options',
        'Options for text preprocessing and OCR:'
    )
    preprocess_group.add_argument(
        "--preprocess",
        type=str,
        help="""Text preprocessing options (comma-separated):
- lowercase: Convert text to lowercase
- strip_whitespace: Remove excess whitespace
- remove_numbers: Remove all numeric characters
- remove_punctuation: Remove punctuation marks
Example: --preprocess lowercase,strip_whitespace"""
    )
    preprocess_group.add_argument(
        "--language",
        type=str,
        help="""Specify language for language-specific processing.
Uses ISO 639-1 codes (e.g., 'en' for English, 'fr' for French).
Affects preprocessing and OCR if enabled."""
    )
    preprocess_group.add_argument(
        "--ocr",
        action="store_true",
        help="""Enable OCR for images and scanned PDFs.
Requires Tesseract OCR to be installed.
Can significantly increase processing time."""
    )
    preprocess_group.add_argument(
        "--ocr-lang",
        type=str,
        default='eng',
        help="""Language for OCR (default: eng).
Uses Tesseract language codes.
Multiple languages can be specified (e.g., 'eng+fra')."""
    )
    
    display_group = parser.add_argument_group(
        'Display Options',
        'Options for controlling output and logging:'
    )
    display_group.add_argument(
        "--verbose",
        action="store_true",
        help="""Enable detailed output.
Shows additional processing information and debug messages."""
    )
    display_group.add_argument(
        "--progress",
        action="store_true",
        help="""Show progress bar during processing.
Displays completion percentage and estimated time remaining."""
    )
    display_group.add_argument(
        "--silent",
        action="store_true",
        help="""Suppress all non-error output.
Only error messages will be displayed.
Overrides --verbose if both are specified."""
    )

def _add_config_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments for the config command."""
    group = parser.add_mutually_exclusive_group(required=True)
    
    group.add_argument(
        "--show",
        action="store_true",
        help="Show current configuration"
    )
    
    group.add_argument(
        "--reset",
        action="store_true",
        help="Reset configuration to default values"
    )
    
    group.add_argument(
        "--set",
        nargs=2,
        metavar=("KEY", "VALUE"),
        help="Set a configuration value (format: section.key value)"
    )

def show_supported_formats(show_details: bool = False) -> None:
    """Display information about supported file formats."""
    formats = {
        "Document Formats": {
            ".pdf": {
                "description": "Adobe PDF documents",
                "features": ["Password protection", "OCR support", "Metadata extraction"],
                "limitations": ["Some PDFs may require OCR", "Complex layouts may affect extraction"]
            },
            ".docx": {
                "description": "Microsoft Word documents",
                "features": ["Style preservation", "Table extraction", "Image text extraction"],
                "limitations": ["Complex formatting may be simplified"]
            },
            ".doc": {
                "description": "Legacy Microsoft Word documents",
                "features": ["Basic text extraction"],
                "limitations": ["Limited formatting support"]
            },
            ".rtf": {
                "description": "Rich Text Format documents",
                "features": ["Basic text extraction", "Simple formatting"],
                "limitations": ["Advanced formatting may be lost"]
            }
        },
        "Spreadsheet Formats": {
            ".xlsx": {
                "description": "Microsoft Excel workbooks",
                "features": ["Multi-sheet support", "Formula preservation", "Cell formatting"],
                "limitations": ["Complex formulas may be simplified"]
            },
            ".xls": {
                "description": "Legacy Microsoft Excel workbooks",
                "features": ["Basic cell extraction"],
                "limitations": ["Limited formatting support"]
            },
            ".csv": {
                "description": "Comma-separated values files",
                "features": ["Delimiter detection", "Encoding detection"],
                "limitations": ["No formatting support"]
            }
        },
        "Data Formats": {
            ".json": {
                "description": "JSON data files",
                "features": ["Structure preservation", "Unicode support"],
                "limitations": ["None"]
            },
            ".xml": {
                "description": "XML documents",
                "features": ["Structure preservation", "Namespace support"],
                "limitations": ["Complex schemas may affect extraction"]
            }
        },
        "Text Formats": {
            ".txt": {
                "description": "Plain text files",
                "features": ["Encoding detection", "Line ending normalization"],
                "limitations": ["No formatting support"]
            },
            ".log": {
                "description": "Log files",
                "features": ["Pattern recognition", "Timestamp parsing"],
                "limitations": ["Format-specific parsing may be required"]
            },
            ".md": {
                "description": "Markdown documents",
                "features": ["Markup preservation", "Link extraction"],
                "limitations": ["Complex formatting may be simplified"]
            }
        }
    }
    
    print("\nSupported File Formats:")
    print("=====================")
    
    for category, format_dict in formats.items():
        print(f"\n{category}:")
        for ext, info in format_dict.items():
            if show_details:
                print(f"\n  {ext}")
                print(f"    Description: {info['description']}")
                print(f"    Features: {', '.join(info['features'])}")
                print(f"    Limitations: {', '.join(info['limitations'])}")
            else:
                print(f"  {ext:<6} - {info['description']}")
    
    if not show_details:
        print("\nUse --details for more information about each format")
    
    print("\nGeneral Features:")
    print("  - Automatic encoding detection")
    print("  - Parallel processing support")
    print("  - Memory-efficient streaming extraction")
    print("  - Text preprocessing options")
    print("  - Progress tracking")
    print("  - OCR support for images and scanned documents")

def handle_config_command(args: argparse.Namespace) -> int:
    """Handle the config subcommand."""
    try:
        if args.show:
            # Show current configuration
            print("\nCurrent Configuration:")
            print(json.dumps(config.settings, indent=2))
            return 0
            
        elif args.reset:
            # Reset to default configuration
            config.settings = DEFAULT_CONFIG.copy()
            config._save_default_config()
            print("Configuration reset to default values.")
            return 0
            
        elif args.set:
            # Set a configuration value
            key_path, value = args.set
            section, key = key_path.split('.')
            
            # Convert value to appropriate type
            if value.lower() in ('true', 'false'):
                value = value.lower() == 'true'
            elif value.isdigit():
                value = int(value)
            elif value.replace('.', '').isdigit():
                value = float(value)
            
            config.update(section, key, value)
            print(f"Updated configuration: {section}.{key} = {value}")
            return 0
            
    except Exception as e:
        logger.error(f"Error handling config command: {e}")
        return 1

def main() -> int:
    """Main entry point."""
    try:
        parser = create_parser()
        args = parser.parse_args()
        
        if not args.command:
            parser.print_help()
            return 0
        
        # Setup logging
        setup_logging(args.verbose if hasattr(args, 'verbose') else False)
        
        # Handle commands
        if args.command == 'formats':
            show_supported_formats(args.details)
            return 0
            
        elif args.command == 'config':
            return handle_config_command(args)
            
        elif args.command == 'extract':
            # Parse preprocessing options
            preprocessing_options = {}
            if args.preprocess:
                for option in args.preprocess.split(','):
                    option = option.strip().lower()
                    if option in ('lowercase', 'strip_whitespace', 'remove_numbers', 'remove_punctuation'):
                        preprocessing_options[option] = True
                    else:
                        logger.warning(f"Unknown preprocessing option: {option}")
            
            # Add password to preprocessing options if provided
            if args.password:
                preprocessing_options['password'] = args.password
            
            # Create processor
            processor = FileProcessor(
                file_paths=args.file_paths,
                output_dir=args.output,
                num_threads=args.threads,
                force=args.force,
                preprocessing_options=preprocessing_options
            )
            
            # Process files
            results = processor.process_all()
            
            return 0 if not processor.failed_files else 1
        
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        return 130
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())