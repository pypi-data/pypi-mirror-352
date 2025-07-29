"""Utility functions for the TFQ0tool package."""

import os
import logging
from pathlib import Path
from typing import Optional
import sys

def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    
    # Create formatters
    console_formatter = logging.Formatter('%(message)s')
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    
    # Setup file handler
    log_dir = Path.home() / '.tfq0tool' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_dir / 'tfq0tool.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

def create_output_path(
    input_path: Path,
    output_dir: Optional[Path],
    suffix: str = "_extracted.txt",
    force: bool = False
) -> Path:
    """Create and return the output file path."""
    if output_dir:
        # If output_dir is specified, use it
        output_path = output_dir / f"{input_path.stem}{suffix}"
    else:
        # Otherwise, use the same directory as input file
        output_path = input_path.parent / f"{input_path.stem}{suffix}"
    
    # Ensure unique filename if not forcing overwrite
    if not force:
        counter = 1
        original_stem = output_path.stem
        while output_path.exists():
            output_path = output_path.parent / f"{original_stem}_{counter}{output_path.suffix}"
            counter += 1
    
    return output_path

def get_file_size(file_path: Path) -> int:
    """Get file size in bytes."""
    return file_path.stat().st_size

def is_binary_file(file_path: Path) -> bool:
    """Check if a file is binary."""
    try:
        with open(file_path, 'tr') as f:
            f.read(1024)
        return False
    except UnicodeDecodeError:
        return True 