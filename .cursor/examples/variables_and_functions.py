# Template Examples: Variables and Functions

"""
This file contains template examples for variables, functions, and helpers
that can be used across any module in the fly behavior pipeline.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Sequence, Mapping, Callable, Any
from types import MappingProxyType

# =============================================================================
# VARIABLE TEMPLATES
# =============================================================================

# Constants (ALL_CAPS with descriptive names)
FRAME_RATE = 60  # Video frame rate in Hz
ARENA_WIDTH_MM = 30.0  # Arena width in millimeters
ARENA_HEIGHT_MM = 30.0  # Arena height in millimeters
BEHAVIOR_THRESHOLD = 0.5  # Classification confidence threshold

# File suffixes (domain-specific comments)
TRACKED_SUFFIX = "_tracked.csv"  # Tracked movement data
SLEAP_SUFFIX = "_sleap.csv"  # SLEAP body-parts data
SCORED_SUFFIX = "_scored.csv"  # Behavior classification results
POSE_SUFFIX = "_pose.csv"  # Pose estimation data

# Configuration constants
DEFAULT_FRAME_RATE = 60  # Default video frame rate
MIN_CONFIDENCE = 0.3  # Minimum confidence for behavior classification
MAX_SPEED_MM_S = 50.0  # Maximum expected fly speed in mm/s

# =============================================================================
# FUNCTION TEMPLATES
# =============================================================================

def validate_input_data(
    data: np.ndarray, 
    expected_shape: tuple[int, ...],
    data_type: str = "coordinates"
) -> None:
    """
    Validate input data for scientific analysis.
    
    Args:
        data: Input data array to validate
        expected_shape: Expected shape of the data array
        data_type: Type of data for error messages (e.g., "coordinates", "speeds")
        
    Raises:
        TypeError: If data is not a numpy array
        ValueError: If data shape doesn't match expected shape
        ValueError: If data contains NaN or infinite values
    """
    if not isinstance(data, np.ndarray):
        raise TypeError(f"Expected numpy array for {data_type}, got {type(data)}")
    
    if data.shape != expected_shape:
        raise ValueError(
            f"Expected {data_type} shape {expected_shape}, got {data.shape}"
        )
    
    if np.any(np.isnan(data)):
        raise ValueError(f"{data_type} contains NaN values")
    
    if np.any(np.isinf(data)):
        raise ValueError(f"{data_type} contains infinite values")


def compute_derived_metric(
    input_data: np.ndarray,
    frame_rate: int = FRAME_RATE,
    smoothing_window: int = 5
) -> np.ndarray:
    """
    Compute a derived metric from input data.
    
    Args:
        input_data: Raw input data array
        frame_rate: Video frame rate in Hz
        smoothing_window: Window size for smoothing
        
    Returns:
        Computed metric array with same length as input
        
    Examples:
        >>> data = np.array([1, 2, 3, 4, 5])
        >>> result = compute_derived_metric(data, frame_rate=60)
        >>> len(result) == len(data)
        True
    """
    # Validate input
    validate_input_data(input_data, (len(input_data),), "input_data")
    
    # Compute metric (example: smoothed derivative)
    if len(input_data) < 2:
        return np.zeros_like(input_data)
    
    # Smooth the data
    smoothed = np.convolve(input_data, np.ones(smoothing_window)/smoothing_window, mode='same')
    
    # Compute derivative
    derivative = np.gradient(smoothed)
    
    return derivative


def process_time_series(
    time_series: pd.Series,
    operation: str = "smooth",
    **kwargs: Any
) -> pd.Series:
    """
    Process a time series with specified operation.
    
    Args:
        time_series: Input time series data
        operation: Operation to perform ("smooth", "filter", "normalize")
        **kwargs: Additional parameters for the operation
        
    Returns:
        Processed time series
        
    Raises:
        ValueError: If operation is not supported
    """
    if operation == "smooth":
        window = kwargs.get("window", 5)
        return time_series.rolling(window=window, center=True).mean()
    
    elif operation == "filter":
        threshold = kwargs.get("threshold", 0.1)
        return time_series[time_series.abs() > threshold]
    
    elif operation == "normalize":
        return (time_series - time_series.mean()) / time_series.std()
    
    else:
        raise ValueError(f"Unsupported operation: {operation}")


# =============================================================================
# HELPER FUNCTION TEMPLATES
# =============================================================================

def _validate_path(path: Path, must_exist: bool = True) -> Path:
    """
    Validate a file path.
    
    Args:
        path: Path to validate
        must_exist: Whether the path must exist
        
    Returns:
        Validated path
        
    Raises:
        FileNotFoundError: If path doesn't exist and must_exist is True
        ValueError: If path is not a file when expected
    """
    if must_exist and not path.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")
    
    return path


def _format_scientific_value(value: float, precision: int = 3) -> str:
    """
    Format a scientific value with appropriate precision.
    
    Args:
        value: Value to format
        precision: Number of decimal places
        
    Returns:
        Formatted string
    """
    if abs(value) < 1e-6:
        return f"{value:.{precision}e}"
    else:
        return f"{value:.{precision}f}"


def _create_output_filename(
    base_name: str,
    suffix: str,
    extension: str = ".csv"
) -> str:
    """
    Create a standardized output filename.
    
    Args:
        base_name: Base name for the file
        suffix: Suffix to add (e.g., "_tracked", "_scored")
        extension: File extension
        
    Returns:
        Formatted filename
    """
    return f"{base_name}{suffix}{extension}"


# =============================================================================
# CLASS TEMPLATES
# =============================================================================

class DataProcessor:
    """
    Template class for data processing operations.
    
    This class demonstrates the standard structure for data processing
    classes in the fly behavior pipeline.
    """
    
    def __init__(self, frame_rate: int = FRAME_RATE) -> None:
        """
        Initialize the data processor.
        
        Args:
            frame_rate: Video frame rate in Hz
        """
        self.frame_rate = frame_rate
        self._validate_frame_rate()
    
    def _validate_frame_rate(self) -> None:
        """Validate frame rate parameter."""
        if self.frame_rate <= 0:
            raise ValueError("Frame rate must be positive")
    
    def process(self, data: np.ndarray) -> np.ndarray:
        """
        Process input data.
        
        Args:
            data: Input data array
            
        Returns:
            Processed data array
        """
        validate_input_data(data, (len(data),), "input_data")
        return self._apply_processing(data)
    
    def _apply_processing(self, data: np.ndarray) -> np.ndarray:
        """Apply the actual processing logic."""
        # Override in subclasses
        return data


# =============================================================================
# PUBLIC API TEMPLATE
# =============================================================================

# Create public bundle for module exports
_PUBLIC = {
    # Constants
    "FRAME_RATE": FRAME_RATE,
    "ARENA_WIDTH_MM": ARENA_WIDTH_MM,
    "ARENA_HEIGHT_MM": ARENA_HEIGHT_MM,
    "BEHAVIOR_THRESHOLD": BEHAVIOR_THRESHOLD,
    
    # File suffixes
    "TRACKED_SUFFIX": TRACKED_SUFFIX,
    "SLEAP_SUFFIX": SLEAP_SUFFIX,
    "SCORED_SUFFIX": SCORED_SUFFIX,
    "POSE_SUFFIX": POSE_SUFFIX,
    
    # Functions
    "validate_input_data": validate_input_data,
    "compute_derived_metric": compute_derived_metric,
    "process_time_series": process_time_series,
    
    # Classes
    "DataProcessor": DataProcessor,
}

# Export immutable bundle
TEMPLATES = MappingProxyType(_PUBLIC)
__all__ = ["TEMPLATES]
