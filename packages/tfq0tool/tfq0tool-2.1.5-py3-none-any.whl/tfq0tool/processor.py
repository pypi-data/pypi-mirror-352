"""File processing module with support for parallel processing and progress tracking."""

import os
import logging
import signal
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from threading import Event
import queue
from tqdm import tqdm

from .extractors import get_extractor
from .utils import (
    setup_logging,
    create_output_path,
    get_file_size,
    validate_file_type,
    is_binary_file
)
from .config import config

logger = logging.getLogger(__name__)

class ProcessingError(Exception):
    """Custom exception for processing errors."""
    pass

class FileProcessor:
    """Handles the processing of files for text extraction."""
    
    def __init__(
        self,
        file_paths: List[str],
        output_dir: Optional[str] = None,
        num_threads: Optional[int] = None,
        force: bool = False,
        preprocessing_options: Optional[Dict[str, Any]] = None
    ):
        self.file_paths = [Path(p) for p in file_paths]
        self.output_dir = Path(output_dir) if output_dir else None
        self.force = force
        self.preprocessing_options = preprocessing_options or {}
        self.stop_event = Event()
        
        # Configure threading
        self.num_threads = self._configure_threads(num_threads)
        
        # Validate inputs
        self._validate_inputs()
        
        # Setup result tracking
        self.results_queue = queue.Queue()
        self.failed_files = []
    
    def _configure_threads(self, num_threads: Optional[int]) -> int:
        """Configure number of threads based on config and system resources."""
        if num_threads is None:
            num_threads = os.cpu_count() or 1
        
        min_threads = config.get("threading", "min_threads")
        max_threads = config.get("threading", "max_threads")
        
        return max(min_threads, min(num_threads, max_threads))
    
    def _validate_inputs(self):
        """Validate input parameters and files."""
        if not self.file_paths:
            raise ValueError("No input files provided")
        
        for file_path in self.file_paths:
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            if not validate_file_type(file_path):
                raise ValueError(f"Unsupported file type: {file_path}")
            
            file_size = get_file_size(file_path)
            max_size = config.get("processing", "max_file_size")
            if file_size > max_size:
                raise ValueError(
                    f"File too large: {file_path} ({file_size} bytes > {max_size} bytes)"
                )
    
    def _process_chunk(self, text: str, output_file: Path, mode: str = 'a') -> None:
        """Process and write a chunk of text to the output file."""
        chunk_size = config.get("processing", "chunk_size")
        
        try:
            with open(output_file, mode, encoding='utf-8') as f:
                for i in range(0, len(text), chunk_size):
                    if self.stop_event.is_set():
                        raise ProcessingError("Processing interrupted")
                    chunk = text[i:i + chunk_size]
                    f.write(chunk)
        except Exception as e:
            logger.error(f"Error writing to {output_file}: {e}")
            raise
    
    def process_file(self, file_path: Path) -> Tuple[Path, Optional[Path], Optional[str]]:
        """Process a single file and return the result."""
        logger.info(f"Processing file: {file_path}")
        
        try:
            # Get appropriate extractor
            extractor = get_extractor(str(file_path), self.preprocessing_options)
            
            # Create output path
            output_file = create_output_path(
                file_path,
                self.output_dir,
                force=self.force
            )
            
            if output_file.exists() and not self.force:
                return file_path, None, "Output file already exists"
            
            # Extract and process text in chunks
            for chunk in extractor.extract_iter(str(file_path)):
                if self.stop_event.is_set():
                    raise ProcessingError("Processing interrupted")
                self._process_chunk(chunk, output_file, 'a')
            
            return file_path, output_file, None
            
        except TimeoutError:
            error_msg = f"Processing timeout for {file_path}"
            logger.error(error_msg)
            return file_path, None, error_msg
        except ProcessingError as e:
            logger.error(f"Processing interrupted for {file_path}: {e}")
            return file_path, None, str(e)
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}", exc_info=True)
            return file_path, None, str(e)
    
    def _handle_interrupt(self, signum, frame):
        """Handle interrupt signal."""
        logger.info("\nInterrupt received, stopping gracefully...")
        self.stop_event.set()
    
    def process_all(self) -> List[Tuple[Path, Optional[Path], Optional[str]]]:
        """Process all files with progress tracking and proper resource management."""
        results = []
        
        # Setup interrupt handler
        original_handler = signal.signal(signal.SIGINT, self._handle_interrupt)
        
        try:
            with ThreadPoolExecutor(
                max_workers=self.num_threads,
                thread_name_prefix="FileProcessor"
            ) as executor:
                # Submit all tasks
                future_to_file = {
                    executor.submit(self.process_file, file_path): file_path
                    for file_path in self.file_paths
                }
                
                # Process results with progress bar
                with tqdm(
                    total=len(self.file_paths),
                    desc="Processing files",
                    unit="file"
                ) as pbar:
                    for future in as_completed(future_to_file):
                        file_path = future_to_file[future]
                        try:
                            # Get result with timeout
                            result = future.result(
                                timeout=config.get("threading", "thread_timeout")
                            )
                            results.append(result)
                            
                            # Update progress
                            if result[2] is None:  # No error
                                pbar.set_description(f"Processed {file_path.name}")
                            else:
                                pbar.set_description(f"Failed {file_path.name}")
                                self.failed_files.append(file_path)
                            
                        except TimeoutError:
                            error_msg = f"Processing timeout for {file_path}"
                            logger.error(error_msg)
                            results.append((file_path, None, error_msg))
                            self.failed_files.append(file_path)
                        except Exception as e:
                            logger.error(
                                f"Unexpected error processing {file_path}: {e}",
                                exc_info=True
                            )
                            results.append((file_path, None, str(e)))
                            self.failed_files.append(file_path)
                        finally:
                            pbar.update(1)
                            
                            # Check if processing should stop
                            if self.stop_event.is_set():
                                executor.shutdown(wait=False)
                                break
        
        finally:
            # Restore original interrupt handler
            signal.signal(signal.SIGINT, original_handler)
        
        # Report final statistics
        self._report_statistics(results)
        
        return results
    
    def _report_statistics(self, results: List[Tuple[Path, Optional[Path], Optional[str]]]):
        """Report processing statistics."""
        total = len(results)
        successful = sum(1 for _, output_path, error in results if output_path and not error)
        failed = len(self.failed_files)
        
        logger.info("\nProcessing Summary:")
        logger.info(f"  Total files: {total}")
        logger.info(f"  Successfully processed: {successful}")
        logger.info(f"  Failed: {failed}")
        
        if failed > 0:
            logger.info("\nFailed files:")
            for file_path in self.failed_files:
                logger.info(f"  - {file_path}") 