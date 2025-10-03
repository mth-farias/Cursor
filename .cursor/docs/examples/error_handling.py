# Template Examples: Error Handling Patterns

"""
This file contains template examples for error handling patterns
used throughout the fly behavior pipeline. These patterns ensure
robust scientific workflows and clear error messages.
"""

from __future__ import annotations

import logging
import traceback
from pathlib import Path
from typing import Any, Callable, Optional, Union
import numpy as np
import pandas as pd

# =============================================================================
# LOGGING SETUP TEMPLATES
# =============================================================================

def setup_logging(
    log_level: str = "INFO",
    log_file: Path | None = None,
    module_name: str = "fly_behavior"
) -> logging.Logger:
    """
    Set up logging for a module.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
        module_name: Name of the module for logger
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(module_name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# =============================================================================
# BASIC ERROR HANDLING TEMPLATES
# =============================================================================

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, handling division by zero.
    
    Args:
        numerator: Numerator value
        denominator: Denominator value
        default: Default value if division by zero
        
    Returns:
        Result of division or default value
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ValueError) as e:
        raise ValueError(f"Cannot divide {numerator} by {denominator}: {e}")

def safe_array_operation(
    operation: Callable[[np.ndarray], np.ndarray],
    data: np.ndarray,
    default: np.ndarray | None = None
) -> np.ndarray:
    """
    Safely perform array operation with error handling.
    
    Args:
        operation: Function to apply to array
        data: Input array
        default: Default array if operation fails
        
    Returns:
        Result of operation or default array
    """
    try:
        return operation(data)
    except Exception as e:
        if default is not None:
            return default
        raise ValueError(f"Array operation failed: {e}")

# =============================================================================
# FILE OPERATION ERROR HANDLING
# =============================================================================

def safe_file_read(
    file_path: Path,
    read_function: Callable[[Path], Any],
    default: Any = None,
    logger: logging.Logger | None = None
) -> Any:
    """
    Safely read a file with error handling.
    
    Args:
        file_path: Path to file to read
        read_function: Function to read the file
        default: Default value if read fails
        logger: Optional logger for error messages
        
    Returns:
        File contents or default value
    """
    try:
        if not file_path.exists():
            raise FileNotFoundError(f"File does not exist: {file_path}")
        
        return read_function(file_path)
    
    except FileNotFoundError as e:
        if logger:
            logger.error(f"File not found: {e}")
        if default is not None:
            return default
        raise
    
    except PermissionError as e:
        if logger:
            logger.error(f"Permission denied: {e}")
        if default is not None:
            return default
        raise
    
    except Exception as e:
        if logger:
            logger.error(f"Unexpected error reading {file_path}: {e}")
        if default is not None:
            return default
        raise

def safe_file_write(
    file_path: Path,
    data: Any,
    write_function: Callable[[Path, Any], None],
    backup: bool = True,
    logger: logging.Logger | None = None
) -> bool:
    """
    Safely write data to file with backup.
    
    Args:
        file_path: Path to write to
        data: Data to write
        write_function: Function to write the data
        backup: Whether to create backup of existing file
        logger: Optional logger for messages
        
    Returns:
        True if write successful, False otherwise
    """
    try:
        # Create backup if file exists and backup is requested
        if backup and file_path.exists():
            backup_path = file_path.with_suffix(file_path.suffix + '.backup')
            file_path.rename(backup_path)
            if logger:
                logger.info(f"Created backup: {backup_path}")
        
        # Write the file
        write_function(file_path, data)
        
        if logger:
            logger.info(f"Successfully wrote: {file_path}")
        return True
    
    except PermissionError as e:
        if logger:
            logger.error(f"Permission denied writing {file_path}: {e}")
        return False
    
    except Exception as e:
        if logger:
            logger.error(f"Error writing {file_path}: {e}")
        return False

# =============================================================================
# DATA PROCESSING ERROR HANDLING
# =============================================================================

def process_with_validation(
    data: np.ndarray,
    processor: Callable[[np.ndarray], np.ndarray],
    validator: Callable[[np.ndarray], None] | None = None,
    logger: logging.Logger | None = None
) -> np.ndarray:
    """
    Process data with validation and error handling.
    
    Args:
        data: Input data array
        processor: Function to process the data
        validator: Optional function to validate input data
        logger: Optional logger for messages
        
    Returns:
        Processed data array
        
    Raises:
        ValueError: If data validation fails
        RuntimeError: If processing fails
    """
    try:
        # Validate input data
        if validator:
            validator(data)
        
        # Process the data
        result = processor(data)
        
        if logger:
            logger.info(f"Successfully processed data shape: {result.shape}")
        
        return result
    
    except ValueError as e:
        if logger:
            logger.error(f"Data validation failed: {e}")
        raise
    
    except Exception as e:
        if logger:
            logger.error(f"Data processing failed: {e}")
        raise RuntimeError(f"Processing failed: {e}")

def batch_process_with_recovery(
    data_list: list[np.ndarray],
    processor: Callable[[np.ndarray], np.ndarray],
    logger: logging.Logger | None = None
) -> list[np.ndarray]:
    """
    Process a batch of data with error recovery.
    
    Args:
        data_list: List of data arrays to process
        processor: Function to process each array
        logger: Optional logger for messages
        
    Returns:
        List of successfully processed arrays
    """
    results = []
    failed_count = 0
    
    for i, data in enumerate(data_list):
        try:
            result = processor(data)
            results.append(result)
            
            if logger:
                logger.debug(f"Successfully processed item {i+1}/{len(data_list)}")
        
        except Exception as e:
            failed_count += 1
            if logger:
                logger.warning(f"Failed to process item {i+1}: {e}")
            continue
    
    if logger:
        logger.info(f"Batch processing complete: {len(results)}/{len(data_list)} successful")
        if failed_count > 0:
            logger.warning(f"{failed_count} items failed processing")
    
    return results

# =============================================================================
# SCIENTIFIC ERROR HANDLING TEMPLATES
# =============================================================================

def handle_data_corruption(
    file_path: Path,
    expected_columns: list[str],
    logger: logging.Logger | None = None
) -> pd.DataFrame | None:
    """
    Handle corrupted data files gracefully.
    
    Args:
        file_path: Path to potentially corrupted file
        expected_columns: Expected column names
        logger: Optional logger for messages
        
    Returns:
        DataFrame if file can be read, None if corrupted
    """
    try:
        # Try to read the file
        df = pd.read_csv(file_path)
        
        # Check for expected columns
        missing_columns = set(expected_columns) - set(df.columns)
        if missing_columns:
            if logger:
                logger.error(f"Missing columns in {file_path}: {missing_columns}")
            return None
        
        # Check for completely empty data
        if df.empty:
            if logger:
                logger.warning(f"Empty data file: {file_path}")
            return None
        
        # Check for all-NaN data
        if df.isna().all().all():
            if logger:
                logger.warning(f"All-NaN data file: {file_path}")
            return None
        
        return df
    
    except Exception as e:
        if logger:
            logger.error(f"Cannot read corrupted file {file_path}: {e}")
        return None

def handle_missing_files(
    required_files: list[Path],
    optional_files: list[Path] | None = None,
    logger: logging.Logger | None = None
) -> tuple[list[Path], list[Path]]:
    """
    Handle missing files and categorize them.
    
    Args:
        required_files: List of required file paths
        optional_files: List of optional file paths
        logger: Optional logger for messages
        
    Returns:
        Tuple of (existing_files, missing_files)
    """
    existing_files = []
    missing_files = []
    
    # Check required files
    for file_path in required_files:
        if file_path.exists():
            existing_files.append(file_path)
        else:
            missing_files.append(file_path)
            if logger:
                logger.error(f"Required file missing: {file_path}")
    
    # Check optional files
    if optional_files:
        for file_path in optional_files:
            if file_path.exists():
                existing_files.append(file_path)
            else:
                if logger:
                    logger.warning(f"Optional file missing: {file_path}")
    
    return existing_files, missing_files

# =============================================================================
# ERROR RECOVERY TEMPLATES
# =============================================================================

def retry_operation(
    operation: Callable[[], Any],
    max_attempts: int = 3,
    delay: float = 1.0,
    logger: logging.Logger | None = None
) -> Any:
    """
    Retry an operation with exponential backoff.
    
    Args:
        operation: Function to retry
        max_attempts: Maximum number of attempts
        delay: Initial delay between attempts
        logger: Optional logger for messages
        
    Returns:
        Result of successful operation
        
    Raises:
        Exception: If all attempts fail
    """
    import time
    
    last_exception = None
    
    for attempt in range(max_attempts):
        try:
            return operation()
        
        except Exception as e:
            last_exception = e
            if logger:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
            
            if attempt < max_attempts - 1:
                time.sleep(delay * (2 ** attempt))  # Exponential backoff
    
    if logger:
        logger.error(f"All {max_attempts} attempts failed")
    
    raise last_exception

def create_checkpoint(
    data: Any,
    checkpoint_path: Path,
    logger: logging.Logger | None = None
) -> bool:
    """
    Create a checkpoint to save intermediate results.
    
    Args:
        data: Data to save
        checkpoint_path: Path to save checkpoint
        logger: Optional logger for messages
        
    Returns:
        True if checkpoint created successfully
    """
    try:
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        
        if isinstance(data, np.ndarray):
            np.save(checkpoint_path, data)
        elif isinstance(data, pd.DataFrame):
            data.to_csv(checkpoint_path, index=False)
        else:
            import pickle
            with open(checkpoint_path, 'wb') as f:
                pickle.dump(data, f)
        
        if logger:
            logger.info(f"Checkpoint created: {checkpoint_path}")
        
        return True
    
    except Exception as e:
        if logger:
            logger.error(f"Failed to create checkpoint {checkpoint_path}: {e}")
        return False

# =============================================================================
# COMPREHENSIVE ERROR HANDLING TEMPLATE
# =============================================================================

def robust_data_processing(
    input_path: Path,
    output_path: Path,
    processor: Callable[[pd.DataFrame], pd.DataFrame],
    validator: Callable[[pd.DataFrame], None] | None = None,
    logger: logging.Logger | None = None
) -> bool:
    """
    Robust data processing with comprehensive error handling.
    
    Args:
        input_path: Path to input data file
        output_path: Path to output data file
        processor: Function to process the data
        validator: Optional function to validate data
        logger: Optional logger for messages
        
    Returns:
        True if processing successful, False otherwise
    """
    try:
        # Read input data with error handling
        df = safe_file_read(
            input_path,
            lambda p: pd.read_csv(p),
            logger=logger
        )
        
        if df is None:
            return False
        
        # Validate data if validator provided
        if validator:
            try:
                validator(df)
            except ValueError as e:
                if logger:
                    logger.error(f"Data validation failed: {e}")
                return False
        
        # Process data with error handling
        try:
            processed_df = processor(df)
        except Exception as e:
            if logger:
                logger.error(f"Data processing failed: {e}")
            return False
        
        # Write output with error handling
        success = safe_file_write(
            output_path,
            processed_df,
            lambda p, d: d.to_csv(p, index=False),
            backup=True,
            logger=logger
        )
        
        return success
    
    except Exception as e:
        if logger:
            logger.error(f"Unexpected error in robust processing: {e}")
        return False
