"""File processing module with support for parallel processing and progress tracking."""

import os
import logging
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

from .extractors import get_extractor
from .utils import setup_logging, create_output_path

logger = logging.getLogger(__name__)

class FileProcessor:
    """Handles the processing of files for text extraction."""
    
    def __init__(
        self,
        file_paths: List[str],
        output_dir: Optional[str] = None,
        num_threads: int = 1,
        force: bool = False,
        preprocessing_options: Optional[Dict[str, Any]] = None,
        chunk_size: int = 1024 * 1024  # 1MB chunks for large files
    ):
        self.file_paths = [Path(p) for p in file_paths]
        self.output_dir = Path(output_dir) if output_dir else None
        self.num_threads = num_threads
        self.force = force
        self.preprocessing_options = preprocessing_options
        self.chunk_size = chunk_size
        
        # Validate inputs
        self._validate_inputs()
    
    def _validate_inputs(self):
        """Validate input parameters."""
        # Check if files exist
        for file_path in self.file_paths:
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
        
        # Check output directory
        if self.output_dir:
            if not self.output_dir.exists():
                self.output_dir.mkdir(parents=True)
            elif not self.output_dir.is_dir():
                raise NotADirectoryError(f"Output path exists but is not a directory: {self.output_dir}")
    
    def process_file(self, file_path: Path) -> Tuple[Path, Optional[Path], Optional[str]]:
        """Process a single file and return the result."""
        try:
            # Get appropriate extractor
            extractor = get_extractor(str(file_path), self.preprocessing_options)
            
            # Create output path
            output_file = create_output_path(
                file_path,
                self.output_dir,
                suffix="_extracted.txt",
                force=self.force
            )
            
            if output_file.exists() and not self.force:
                logger.warning(f"Output file already exists: {output_file}")
                return file_path, None, "Output file already exists"
            
            # Extract text
            extracted_text = extractor.extract(str(file_path))
            
            # Write output in chunks to handle large files
            with open(output_file, 'w', encoding='utf-8') as f:
                for i in range(0, len(extracted_text), self.chunk_size):
                    chunk = extracted_text[i:i + self.chunk_size]
                    f.write(chunk)
            
            return file_path, output_file, None
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}", exc_info=True)
            return file_path, None, str(e)
    
    def process_all(self) -> List[Tuple[Path, Optional[Path], Optional[str]]]:
        """Process all files with progress tracking."""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(self.process_file, file_path): file_path
                for file_path in self.file_paths
            }
            
            # Process results with progress bar
            with tqdm(total=len(self.file_paths), desc="Processing files") as pbar:
                for future in as_completed(future_to_file):
                    file_path = future_to_file[future]
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        logger.error(f"Unexpected error processing {file_path}: {e}", exc_info=True)
                        results.append((file_path, None, str(e)))
                    finally:
                        pbar.update(1)
        
        return results 