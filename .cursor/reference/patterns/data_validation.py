# Template Examples: Data Validation Patterns

"""
This file contains template examples for data validation patterns
used throughout the fly behavior pipeline. These patterns ensure
scientific data integrity and provide clear error messages.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Any, Sequence, Mapping, Union

# =============================================================================
# COORDINATE VALIDATION TEMPLATES
# =============================================================================

def validate_coordinates(
    coords: np.ndarray, 
    expected_shape: tuple[int, ...],
    coordinate_type: str = "coordinates"
) -> None:
    """
    Validate coordinate data for scientific analysis.
    
    Args:
        coords: Coordinate array to validate
        expected_shape: Expected shape of the coordinate array
        coordinate_type: Type of coordinates for error messages
        
    Raises:
        TypeError: If coords is not a numpy array
        ValueError: If shape doesn't match expected shape
        ValueError: If coordinates contain NaN or infinite values
    """
    if not isinstance(coords, np.ndarray):
        raise TypeError(f"Expected numpy array for {coordinate_type}, got {type(coords)}")
    
    if coords.shape != expected_shape:
        raise ValueError(
            f"Expected {coordinate_type} shape {expected_shape}, got {coords.shape}"
        )
    
    if np.any(np.isnan(coords)):
        raise ValueError(f"{coordinate_type} contain NaN values")
    
    if np.any(np.isinf(coords)):
        raise ValueError(f"{coordinate_type} contain infinite values")

def validate_2d_coordinates(coords: np.ndarray, min_points: int = 1) -> None:
    """
    Validate 2D coordinate data specifically.
    
    Args:
        coords: 2D coordinate array (N, 2)
        min_points: Minimum number of coordinate points required
        
    Raises:
        ValueError: If coordinates don't meet requirements
    """
    validate_coordinates(coords, (len(coords), 2), "2D coordinates")
    
    if len(coords) < min_points:
        raise ValueError(f"Need at least {min_points} coordinate points, got {len(coords)}")
    
    # Check for reasonable coordinate ranges (adjust as needed)
    if np.any(np.abs(coords) > 1000):  # Adjust threshold as needed
        raise ValueError("Coordinates appear to be outside reasonable range")

# =============================================================================
# TIME SERIES VALIDATION TEMPLATES
# =============================================================================

def validate_time_series(
    series: pd.Series,
    expected_length: int | None = None,
    required_columns: list[str] | None = None
) -> None:
    """
    Validate time series data.
    
    Args:
        series: Time series to validate
        expected_length: Expected length of the series
        required_columns: Required column names (for DataFrame)
        
    Raises:
        TypeError: If series is not a pandas Series
        ValueError: If series doesn't meet requirements
    """
    if not isinstance(series, pd.Series):
        raise TypeError(f"Expected pandas Series, got {type(series)}")
    
    if expected_length is not None and len(series) != expected_length:
        raise ValueError(f"Expected series length {expected_length}, got {len(series)}")
    
    if series.empty:
        raise ValueError("Time series cannot be empty")
    
    if series.isna().all():
        raise ValueError("Time series cannot be all NaN")

def validate_frame_data(
    frame_data: np.ndarray,
    frame_number: int,
    expected_channels: int = 1
) -> None:
    """
    Validate frame data from video.
    
    Args:
        frame_data: Frame data array
        frame_number: Frame number for error messages
        expected_channels: Expected number of channels
        
    Raises:
        ValueError: If frame data is invalid
    """
    if not isinstance(frame_data, np.ndarray):
        raise TypeError(f"Frame {frame_number} data must be numpy array")
    
    if frame_data.size == 0:
        raise ValueError(f"Frame {frame_number} data is empty")
    
    if len(frame_data.shape) == 3 and frame_data.shape[2] != expected_channels:
        raise ValueError(
            f"Frame {frame_number} has {frame_data.shape[2]} channels, "
            f"expected {expected_channels}"
        )

# =============================================================================
# CONFIGURATION VALIDATION TEMPLATES
# =============================================================================

def validate_experiment_config(config: dict[str, Any]) -> None:
    """
    Validate experiment configuration.
    
    Args:
        config: Configuration dictionary to validate
        
    Raises:
        ValueError: If configuration is invalid
    """
    required_keys = ["frame_rate", "arena_width", "arena_height"]
    
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required configuration key: {key}")
    
    # Validate frame rate
    frame_rate = config["frame_rate"]
    if not isinstance(frame_rate, int) or frame_rate <= 0:
        raise ValueError(f"Frame rate must be positive integer, got {frame_rate}")
    
    # Validate arena dimensions
    for dim in ["arena_width", "arena_height"]:
        value = config[dim]
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError(f"{dim} must be positive number, got {value}")

def validate_stimulus_config(
    stimulus_name: str,
    stimulus_config: dict[str, Any]
) -> None:
    """
    Validate stimulus configuration.
    
    Args:
        stimulus_name: Name of the stimulus
        stimulus_config: Stimulus configuration dictionary
        
    Raises:
        ValueError: If stimulus configuration is invalid
    """
    if not stimulus_config:
        raise ValueError(f"Stimulus '{stimulus_name}' configuration is empty")
    
    # Check for required detection tuple
    detection = stimulus_config.get("detection")
    if detection is None:
        raise ValueError(f"Stimulus '{stimulus_name}' missing detection configuration")
    
    if not isinstance(detection, (list, tuple)) or len(detection) != 2:
        raise ValueError(
            f"Stimulus '{stimulus_name}' detection must be (off, on) tuple, "
            f"got {detection}"
        )
    
    off_value, on_value = detection
    if not isinstance(off_value, (int, float)) or not isinstance(on_value, (int, float)):
        raise ValueError(
            f"Stimulus '{stimulus_name}' detection values must be numeric, "
            f"got {detection}"
        )

# =============================================================================
# FILE VALIDATION TEMPLATES
# =============================================================================

def validate_file_path(
    file_path: Path,
    must_exist: bool = True,
    must_be_file: bool = True,
    required_extension: str | None = None
) -> Path:
    """
    Validate file path.
    
    Args:
        file_path: Path to validate
        must_exist: Whether the file must exist
        must_be_file: Whether the path must be a file (not directory)
        required_extension: Required file extension
        
    Returns:
        Validated path
        
    Raises:
        FileNotFoundError: If file doesn't exist and must_exist is True
        ValueError: If path doesn't meet requirements
    """
    if must_exist and not file_path.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")
    
    if must_exist and must_be_file and not file_path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")
    
    if required_extension and not file_path.suffix == required_extension:
        raise ValueError(
            f"File must have extension '{required_extension}', "
            f"got '{file_path.suffix}'"
        )
    
    return file_path

def validate_csv_file(csv_path: Path, required_columns: list[str] | None = None) -> None:
    """
    Validate CSV file structure.
    
    Args:
        csv_path: Path to CSV file
        required_columns: Required column names
        
    Raises:
        ValueError: If CSV file is invalid
    """
    validate_file_path(csv_path, must_exist=True, required_extension=".csv")
    
    try:
        df = pd.read_csv(csv_path, nrows=0)  # Read only headers
    except Exception as e:
        raise ValueError(f"Cannot read CSV file {csv_path}: {e}")
    
    if required_columns:
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            raise ValueError(
                f"CSV file {csv_path} missing required columns: {missing_columns}"
            )

# =============================================================================
# DATA TYPE VALIDATION TEMPLATES
# =============================================================================

def validate_numeric_array(
    data: Any,
    expected_dtype: np.dtype | None = None,
    allow_nan: bool = False,
    allow_inf: bool = False
) -> np.ndarray:
    """
    Validate and convert data to numeric array.
    
    Args:
        data: Data to validate and convert
        expected_dtype: Expected numpy dtype
        allow_nan: Whether NaN values are allowed
        allow_inf: Whether infinite values are allowed
        
    Returns:
        Validated numeric array
        
    Raises:
        TypeError: If data cannot be converted to numeric array
        ValueError: If data doesn't meet requirements
    """
    try:
        array = np.asarray(data, dtype=expected_dtype)
    except Exception as e:
        raise TypeError(f"Cannot convert to numeric array: {e}")
    
    if not np.issubdtype(array.dtype, np.number):
        raise TypeError(f"Array must be numeric, got dtype {array.dtype}")
    
    if not allow_nan and np.any(np.isnan(array)):
        raise ValueError("Array contains NaN values")
    
    if not allow_inf and np.any(np.isinf(array)):
        raise ValueError("Array contains infinite values")
    
    return array

def validate_positive_values(
    values: np.ndarray,
    value_name: str = "values"
) -> None:
    """
    Validate that all values are positive.
    
    Args:
        values: Array of values to validate
        value_name: Name of values for error messages
        
    Raises:
        ValueError: If any values are not positive
    """
    if np.any(values <= 0):
        negative_count = np.sum(values <= 0)
        raise ValueError(
            f"{negative_count} {value_name} are not positive "
            f"(found values <= 0)"
        )

# =============================================================================
# COMPREHENSIVE VALIDATION TEMPLATE
# =============================================================================

def validate_experiment_data(
    coordinates: np.ndarray,
    frame_rate: int,
    arena_width: float,
    arena_height: float,
    stimulus_data: dict[str, Any] | None = None
) -> None:
    """
    Comprehensive validation of experiment data.
    
    Args:
        coordinates: Fly coordinate data
        frame_rate: Video frame rate
        arena_width: Arena width in mm
        arena_height: Arena height in mm
        stimulus_data: Optional stimulus data
        
    Raises:
        ValueError: If any data is invalid
    """
    # Validate coordinates
    validate_2d_coordinates(coordinates, min_points=10)
    
    # Validate frame rate
    if not isinstance(frame_rate, int) or frame_rate <= 0:
        raise ValueError(f"Frame rate must be positive integer, got {frame_rate}")
    
    # Validate arena dimensions
    for dim_name, dim_value in [("width", arena_width), ("height", arena_height)]:
        if not isinstance(dim_value, (int, float)) or dim_value <= 0:
            raise ValueError(f"Arena {dim_name} must be positive, got {dim_value}")
    
    # Validate stimulus data if provided
    if stimulus_data:
        for stim_name, stim_config in stimulus_data.items():
            validate_stimulus_config(stim_name, stim_config)
    
    # Check coordinate bounds
    x_coords, y_coords = coordinates[:, 0], coordinates[:, 1]
    
    if np.any(x_coords < 0) or np.any(x_coords > arena_width):
        raise ValueError("X coordinates outside arena bounds")
    
    if np.any(y_coords < 0) or np.any(y_coords > arena_height):
        raise ValueError("Y coordinates outside arena bounds")
