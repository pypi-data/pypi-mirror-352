"""Main entry point for the TFQ0tool package."""

import argparse
import sys
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

from .processor import FileProcessor
from .utils import setup_logging

logger = logging.getLogger(__name__)

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="TFQ0tool: A powerful text extraction utility for multiple file formats.",
        epilog="""
Examples:
  tfq0tool sample.pdf
  tfq0tool document.docx --output ./extracted
  tfq0tool *.pdf *.docx --threads 4 --verbose
  tfq0tool file.pdf --password mypass
  tfq0tool input.docx --preprocess lowercase,strip_whitespace
""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "file_paths",
        nargs='+',
        help="Path(s) to the file(s) for text extraction"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output directory for extracted text files"
    )
    
    parser.add_argument(
        "-t", "--threads",
        type=int,
        default=1,
        help="Number of threads for parallel processing (default: 1)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Overwrite files without prompting"
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
    
    return parser.parse_args()

def parse_preprocessing_options(preprocess_str: Optional[str]) -> Dict[str, Any]:
    """Parse preprocessing options from command line argument."""
    if not preprocess_str:
        return {}
    
    options = {}
    for option in preprocess_str.split(','):
        option = option.strip().lower()
        if option == 'lowercase':
            options['lowercase'] = True
        elif option == 'strip_whitespace':
            options['strip_whitespace'] = True
        else:
            logger.warning(f"Unknown preprocessing option: {option}")
    
    return options

def expand_file_paths(paths: List[str]) -> List[str]:
    """Expand glob patterns in file paths."""
    expanded = []
    for path in paths:
        p = Path(path)
        if '*' in path:
            expanded.extend(str(f) for f in p.parent.glob(p.name))
        else:
            expanded.append(path)
    return expanded

def main() -> int:
    """Main entry point."""
    try:
        args = parse_args()
        
        # Setup logging
        setup_logging(args.verbose)
        
        # Expand file paths (handle glob patterns)
        file_paths = expand_file_paths(args.file_paths)
        if not file_paths:
            logger.error("No files found matching the specified patterns")
            return 1
        
        # Parse preprocessing options
        preprocessing_options = parse_preprocessing_options(args.preprocess)
        
        # Create processor
        processor = FileProcessor(
            file_paths=file_paths,
            output_dir=args.output,
            num_threads=args.threads,
            force=args.force,
            preprocessing_options=preprocessing_options
        )
        
        # Process files
        results = processor.process_all()
        
        # Report results
        success_count = sum(1 for _, output_path, error in results if output_path and not error)
        error_count = sum(1 for _, _, error in results if error)
        
        logger.info(f"\nProcessing complete:")
        logger.info(f"  Successful: {success_count}")
        logger.info(f"  Failed: {error_count}")
        
        if args.verbose:
            logger.debug("\nDetailed results:")
            for input_path, output_path, error in results:
                if error:
                    logger.debug(f"  ❌ {input_path}: {error}")
                else:
                    logger.debug(f"  ✅ {input_path} -> {output_path}")
        
        return 0 if error_count == 0 else 1
        
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        return 130
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())