"""Utility functions for the TFQ0tool package."""

import os
import logging
import shutil
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional
import sys
from .config import config

def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration with rotation and organization."""
    level = logging.DEBUG if verbose else logging.INFO
    
    # Create formatters
    console_formatter = logging.Formatter('%(message)s')
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    
    # Setup file handler with rotation
    log_dir = Path(config.get("logging", "log_dir"))
    log_dir.mkdir(parents=True, exist_ok=True)
    
    file_handler = RotatingFileHandler(
        log_dir / 'tfq0tool.log',
        maxBytes=config.get("logging", "max_log_size"),
        backupCount=config.get("logging", "backup_count")
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

def create_output_path(
    input_path: Path,
    output_dir: Optional[Path],
    suffix: Optional[str] = None,
    force: bool = False
) -> Path:
    """Create and return the output file path with improved safety checks."""
    if suffix is None:
        suffix = config.get("output", "default_suffix")
    
    if output_dir:
        # If output_dir is specified, use it
        output_path = output_dir / f"{input_path.stem}{suffix}"
    else:
        # Otherwise, use the same directory as input file
        output_path = input_path.parent / f"{input_path.stem}{suffix}"
    
    # Ensure the output directory exists and has enough space
    output_dir = output_path.parent
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
    
    # Check available disk space
    try:
        free_space = shutil.disk_usage(str(output_dir)).free
        if free_space < config.get("output", "min_free_space"):
            raise IOError(f"Insufficient disk space. Required: {config.get('output', 'min_free_space')} bytes")
    except Exception as e:
        logging.error(f"Error checking disk space: {e}")
        raise
    
    # Sanitize filename
    output_path = output_path.parent / "".join(
        c for c in output_path.name if c.isalnum() or c in "._- "
    )
    
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
    try:
        return file_path.stat().st_size
    except OSError as e:
        logging.error(f"Error getting file size for {file_path}: {e}")
        raise

def is_binary_file(file_path: Path) -> bool:
    """Check if a file is binary with improved detection."""
    try:
        chunk_size = min(1024, get_file_size(file_path))
        with open(file_path, 'rb') as f:
            content = f.read(chunk_size)
            
        # Check for common binary file signatures
        binary_signatures = [
            b'\x00',  # Null bytes
            b'\xff\xd8\xff',  # JPEG
            b'\x89PNG',  # PNG
            b'%PDF',  # PDF
            b'PK\x03\x04'  # ZIP
        ]
        
        for sig in binary_signatures:
            if content.startswith(sig):
                return True
        
        # Check for high concentration of non-text bytes
        text_chars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7f})
        return bool(content.translate(None, text_chars))
    except Exception as e:
        logging.error(f"Error checking if file is binary: {e}")
        raise

def validate_file_type(file_path: Path) -> bool:
    """Validate if the file type is supported."""
    return file_path.suffix.lower() in config.get("supported_formats", None) 