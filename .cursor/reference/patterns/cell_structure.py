# Template Examples: Cell Structure

"""
This file contains template examples for the cell-based structure
used in the fly behavior pipeline. Each cell has a specific purpose
and follows a consistent pattern.
"""

#%% CELL 00 — HEADER & OVERVIEW
"""
{{COMMIT_DETAILS}}
# <github.com/YourLab/Repo>
# <commit-hash>
# <DD-MM-YYYY HH:MM:SS>

ModuleName/example_module.py

Overview
	Brief description of module purpose and functionality.
	This module demonstrates the cell-based structure used throughout
	the fly behavior pipeline.

API
	This module exports TEMPLATES bundle containing:
	- Constants: FRAME_RATE, ARENA_WIDTH_MM, etc.
	- Functions: validate_data, process_data, etc.
	- Classes: DataProcessor, etc.

Canonical layout
------------------------------------------------------------------------------------
	ModuleName/
	├── example_module.py          ← this file
	├── _helpers.py               # Private helper functions
	└── _validation.py            # Data validation functions
"""

#%% CELL 01 — IMPORTS

from __future__ import annotations

"""
Import minimal, stable dependencies used throughout this module.
Order: stdlib → typing → third-party → local types.
"""

# Standard library
import os
import sys
from pathlib import Path
from types import MappingProxyType

# Typing
from typing import Iterator, Sequence, Mapping, Any, Callable

# Third-party
import numpy as np
import pandas as pd

# Package path setup (for safe absolute imports)
ROOT = Path(__file__).resolve().parents[1]  # .../Codes
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Local imports
from Config import EXPERIMENT
from BehaviorClassifier import BC_CLASSIFIER

#%% CELL 02 — CONSTANTS & VALIDATION

"""
Define module-level constants and validation functions.
All constants must be ALL_CAPS with descriptive comments.
"""

# FILE SUFFIXES
TRACKED_SUFFIX = "_tracked.csv"  # Tracked movement data
SLEAP_SUFFIX = "_sleap.csv"      # SLEAP body-parts data
SCORED_SUFFIX = "_scored.csv"    # Behavior classification results
POSE_SUFFIX = "_pose.csv"        # Pose estimation data

# PROCESSING PARAMETERS
DEFAULT_FRAME_RATE = 60  # Default video frame rate in Hz
MIN_CONFIDENCE = 0.3     # Minimum confidence for classification
MAX_SPEED_MM_S = 50.0    # Maximum expected fly speed in mm/s

# VALIDATION FUNCTIONS
def validate_frame_rate(frame_rate: int) -> None:
    """Validate frame rate parameter."""
    if not isinstance(frame_rate, int):
        raise TypeError(f"Frame rate must be integer, got {type(frame_rate)}")
    if frame_rate <= 0:
        raise ValueError(f"Frame rate must be positive, got {frame_rate}")

def validate_confidence(confidence: float) -> None:
    """Validate confidence parameter."""
    if not isinstance(confidence, (int, float)):
        raise TypeError(f"Confidence must be numeric, got {type(confidence)}")
    if not 0 <= confidence <= 1:
        raise ValueError(f"Confidence must be between 0 and 1, got {confidence}")

#%% CELL 03 — HELPER FUNCTIONS

"""
Private helper functions used within this module.
All helpers must be stateless and policy-light.
"""

def _validate_input_data(
    data: np.ndarray, 
    expected_shape: tuple[int, ...],
    data_type: str = "data"
) -> None:
    """Validate input data for scientific analysis."""
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

def _format_scientific_value(value: float, precision: int = 3) -> str:
    """Format a scientific value with appropriate precision."""
    if abs(value) < 1e-6:
        return f"{value:.{precision}e}"
    else:
        return f"{value:.{precision}f}"

def _create_output_filename(
    base_name: str,
    suffix: str,
    extension: str = ".csv"
) -> str:
    """Create a standardized output filename."""
    return f"{base_name}{suffix}{extension}"

#%% CELL 04 — CORE LOGIC

"""
Main functionality of the module.
This is where the core processing logic lives.
"""

def process_movement_data(
    coordinates: np.ndarray,
    frame_rate: int = DEFAULT_FRAME_RATE,
    smoothing_window: int = 5
) -> dict[str, np.ndarray]:
    """
    Process movement data to extract behavioral metrics.
    
    Args:
        coordinates: Array of (x, y) coordinates over time
        frame_rate: Video frame rate in Hz
        smoothing_window: Window size for smoothing
        
    Returns:
        Dictionary containing processed metrics
        
    Raises:
        ValueError: If coordinates are invalid
        TypeError: If parameters are wrong type
    """
    # Validate inputs
    validate_frame_rate(frame_rate)
    _validate_input_data(coordinates, (len(coordinates), 2), "coordinates")
    
    # Process coordinates
    x_coords = coordinates[:, 0]
    y_coords = coordinates[:, 1]
    
    # Compute speed
    speed = _compute_speed(x_coords, y_coords, frame_rate)
    
    # Compute acceleration
    acceleration = _compute_acceleration(speed, frame_rate)
    
    # Smooth the data
    smoothed_speed = _smooth_data(speed, smoothing_window)
    
    return {
        "speed": speed,
        "acceleration": acceleration,
        "smoothed_speed": smoothed_speed,
        "x_coords": x_coords,
        "y_coords": y_coords
    }

def _compute_speed(x_coords: np.ndarray, y_coords: np.ndarray, frame_rate: int) -> np.ndarray:
    """Compute speed from coordinates."""
    if len(x_coords) < 2:
        return np.zeros_like(x_coords)
    
    # Compute displacement
    dx = np.diff(x_coords, prepend=x_coords[0])
    dy = np.diff(y_coords, prepend=y_coords[0])
    
    # Compute speed in mm/s
    speed = np.sqrt(dx**2 + dy**2) * frame_rate
    return speed

def _compute_acceleration(speed: np.ndarray, frame_rate: int) -> np.ndarray:
    """Compute acceleration from speed."""
    if len(speed) < 2:
        return np.zeros_like(speed)
    
    acceleration = np.diff(speed, prepend=speed[0]) * frame_rate
    return acceleration

def _smooth_data(data: np.ndarray, window: int) -> np.ndarray:
    """Smooth data using moving average."""
    if len(data) < window:
        return data
    
    return np.convolve(data, np.ones(window)/window, mode='same')

#%% CELL 05 — PUBLIC API

"""
Export the public interface for this module.
Exactly one immutable bundle per module.
"""

# Create public bundle
_PUBLIC = {
    # Constants
    "TRACKED_SUFFIX": TRACKED_SUFFIX,
    "SLEAP_SUFFIX": SLEAP_SUFFIX,
    "SCORED_SUFFIX": SCORED_SUFFIX,
    "POSE_SUFFIX": POSE_SUFFIX,
    "DEFAULT_FRAME_RATE": DEFAULT_FRAME_RATE,
    "MIN_CONFIDENCE": MIN_CONFIDENCE,
    "MAX_SPEED_MM_S": MAX_SPEED_MM_S,
    
    # Functions
    "process_movement_data": process_movement_data,
    "validate_frame_rate": validate_frame_rate,
    "validate_confidence": validate_confidence,
}

# Export immutable bundle
TEMPLATES = MappingProxyType(_PUBLIC)
__all__ = ["TEMPLATES"]

#%% CELL 06 — REPORT

"""
Optional diagnostic output for this module.
Only consumes the exported bundle, no computation.
"""

if __name__ == "__main__":
    print("=== TEMPLATES Module Report ===")
    print(f"Constants: {len([k for k in TEMPLATES if k.isupper()])}")
    print(f"Functions: {len([k for k in TEMPLATES if callable(TEMPLATES[k])])}")
    print(f"Total exports: {len(TEMPLATES)}")
    
    print("\nAvailable constants:")
    for key in sorted(TEMPLATES):
        if key.isupper():
            print(f"  {key}: {TEMPLATES[key]}")
    
    print("\nAvailable functions:")
    for key in sorted(TEMPLATES):
        if callable(TEMPLATES[key]):
            print(f"  {key}: {TEMPLATES[key].__name__}")
