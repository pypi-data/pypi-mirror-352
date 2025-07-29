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
        description="TFQ0tool: A powerful text extraction utility for multiple file formats.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Add version information
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'%(prog)s {config.get("version")}'
    )
    
    # Create subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Extract command
    extract_parser = subparsers.add_parser(
        'extract',
        help='Extract text from files',
        description='Extract text from various file formats with customizable options.'
    )
    _add_extract_arguments(extract_parser)
    
    # Config command
    config_parser = subparsers.add_parser(
        'config',
        help='Manage configuration settings',
        description='View or modify TFQ0tool configuration settings.'
    )
    _add_config_arguments(config_parser)
    
    # List formats command
    formats_parser = subparsers.add_parser(
        'formats',
        help='List supported file formats',
        description='Display all supported file formats and their features.'
    )
    
    return parser

def _add_extract_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments for the extract command."""
    parser.add_argument(
        "file_paths",
        nargs='+',
        help="Path(s) to the file(s) for text extraction. Supports glob patterns (e.g., *.pdf)"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output directory for extracted text files"
    )
    
    parser.add_argument(
        "-t", "--threads",
        type=int,
        help=f"Number of threads for parallel processing (default: auto, min: {config.get('threading', 'min_threads')}, max: {config.get('threading', 'max_threads')})"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Overwrite existing output files without prompting"
    )
    
    parser.add_argument(
        "-p", "--password",
        type=str,
        help="Password for encrypted PDF files"
    )
    
    parser.add_argument(
        "--preprocess",
        type=str,
        help="Text preprocessing options (comma-separated): lowercase,strip_whitespace"
    )
    
    parser.add_argument(
        "--progress",
        action="store_true",
        help="Show progress bar during processing"
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

def show_supported_formats() -> None:
    """Display information about supported file formats."""
    formats = {
        "Document Formats": {
            ".pdf": "Adobe PDF documents (with optional password protection)",
            ".docx": "Microsoft Word documents",
            ".doc": "Legacy Microsoft Word documents",
            ".rtf": "Rich Text Format documents"
        },
        "Spreadsheet Formats": {
            ".xlsx": "Microsoft Excel workbooks",
            ".xls": "Legacy Microsoft Excel workbooks",
            ".csv": "Comma-separated values files"
        },
        "Data Formats": {
            ".json": "JSON data files",
            ".xml": "XML documents"
        },
        "Text Formats": {
            ".txt": "Plain text files (with encoding detection)",
            ".log": "Log files",
            ".md": "Markdown documents"
        }
    }
    
    print("\nSupported File Formats:")
    print("=====================")
    
    for category, format_dict in formats.items():
        print(f"\n{category}:")
        for ext, desc in format_dict.items():
            print(f"  {ext:<6} - {desc}")
    
    print("\nFeatures:")
    print("  - Automatic encoding detection")
    print("  - Parallel processing support")
    print("  - Memory-efficient streaming extraction")
    print("  - Text preprocessing options")
    print("  - Progress tracking")

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
            show_supported_formats()
            return 0
            
        elif args.command == 'config':
            return handle_config_command(args)
            
        elif args.command == 'extract':
            # Parse preprocessing options
            preprocessing_options = {}
            if args.preprocess:
                for option in args.preprocess.split(','):
                    option = option.strip().lower()
                    if option in ('lowercase', 'strip_whitespace'):
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