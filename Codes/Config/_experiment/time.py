#%% CELL 00 — HEADER & OVERVIEW
"""
{{COMMIT_DETAILS}}
# <github.com/YourLab/Repo>
# <commit_hash>
# <DD-MM-YYYY HH:MM:SS>

Config/_experiment/time.py

Overview
	Time conversion and query utilities for the experiment configuration.
	Provides seconds↔frames conversions and fast period query functions.
	Handles both scalar and vectorized operations with NumPy arrays.

Functions
	- seconds_to_frames: Convert seconds to frame indices (scalar/array)
	- frames_to_seconds: Convert frame indices to seconds (scalar/array)
	- period_by_frame: Get period name for single frame
	- period_by_frames: Vectorized period lookup for frame arrays
	- in_period: Check if frame is within named period

Exports
	_TIME → MappingProxyType bundle with all time functions and constants
"""

#%% CELL 01 — IMPORTS

from __future__ import annotations

from types import MappingProxyType
import numpy as np

#%% CELL 02 — TIME CONVERSION FUNCTIONS

def create_time_functions(frame_rate: int) -> dict:
    """
    Create time conversion functions for given frame rate.
    
    Args:
        frame_rate: Video frame rate in fps
        
    Returns:
        dict: Time conversion functions and constants
    """
    if frame_rate <= 0:
        raise ValueError("FRAME_RATE must be > 0.")
    
    sec_per_frame: float = 1.0 / float(frame_rate)
    
    def seconds_to_frames(seconds) -> int | np.ndarray:
        """
        Convert seconds to frame index counts using FRAME_RATE.
        
        Args:
            seconds: Scalar float/int or NumPy array-like of seconds.
        
        Returns:
            int or np.ndarray: Frame counts as integers.
        
        Raises:
            ValueError: If FRAME_RATE <= 0.
        
        Notes:
            - Uses np.rint ("banker's rounding") to keep .5 boundaries stable across
              NumPy/Python and avoid jitter that can shift frames by ±1 at x.5.
        """
        arr = np.asarray(seconds)
        frames = np.rint(arr * frame_rate).astype(int)  # round to nearest int
        
        # Preserve scalar return when input was scalar
        return int(frames) if np.isscalar(seconds) else frames
    
    def frames_to_seconds(frames) -> float | np.ndarray:
        """
        Convert frame indices/counts to seconds using FRAME_RATE.
        
        Args:
            frames: Scalar int or NumPy array-like of frames.
        
        Returns:
            float or np.ndarray: Seconds as float(s).
        
        Raises:
            ValueError: If FRAME_RATE <= 0.
        """
        arr = np.asarray(frames, dtype=float)
        seconds = arr * sec_per_frame  # multiply by reciprocal
        
        return float(seconds) if np.isscalar(frames) else seconds
    
    return {
        "SEC_PER_FRAME": sec_per_frame,
        "seconds_to_frames": seconds_to_frames,
        "frames_to_seconds": frames_to_seconds,
    }

#%% CELL 03 — PERIOD QUERY FUNCTIONS

def create_period_query_functions(period_data: dict) -> dict:
    """
    Create period query functions using period data.
    
    Args:
        period_data: Period structures from periods module
        
    Returns:
        dict: Period query functions
    """
    period_order = period_data["PERIOD_ORDER"]
    period_ends_exclusive = period_data["PERIOD_ENDS_EXCLUSIVE"]
    periods_derived = period_data["PERIODS_DERIVED"]
    experiment_total_frames = period_data["EXPERIMENT_TOTAL_FRAMES"]
    
    def period_by_frame(frame: int) -> str:
        """
        Return the period name that contains `frame`, or "OutOfRange" if out of bounds.
        
        Args:
            frame: Zero-based frame index.
        
        Returns:
            str: Period name if frame ∈ [0, EXPERIMENT_TOTAL_FRAMES), else "OutOfRange".
        
        Notes:
            - Membership uses half-open intervals: [start, end_exclusive).
              A frame equal to a period's end_exclusive belongs to the next period.
        """
        if not isinstance(frame, (int, np.integer)):
            raise TypeError("frame must be an integer.")
        if frame < 0 or frame >= experiment_total_frames:
            return "OutOfRange"
        
        # Find the first end_exclusive strictly greater than frame.
        idx = int(np.searchsorted(period_ends_exclusive, frame, side="right"))
        return period_order[idx]
    
    def period_by_frames(frames: np.ndarray) -> np.ndarray:
        """
        Vectorized period lookup.
        
        Args:
            frames: 1D array-like of zero-based frame indices.
        
        Returns:
            np.ndarray[str]: Period names; "OutOfRange" where applicable.
        
        Notes:
            - Membership uses half-open intervals: [start, end_exclusive).
        """
        arr = np.asarray(frames, dtype=int)
        
        # Map to indices via first end_exclusive strictly greater than frame.
        idx = np.searchsorted(period_ends_exclusive, arr, side="right")
        
        # Build output with "OutOfRange" default, then fill valid positions.
        names = np.array(period_order, dtype=object)
        out = np.full(arr.shape, "OutOfRange", dtype=object)
        in_range = (arr >= 0) & (arr < experiment_total_frames)
        out[in_range] = names[idx[in_range]]
        return out
    
    def in_period(name: str, frame: int) -> bool:
        """
        Check whether a frame lies inside the named period.
        
        Args:
            name: Period name (must exist).
            frame: Zero-based frame index.
        
        Returns:
            bool: True iff frame ∈ [start, end_exclusive) of `name`.
        
        Raises:
            KeyError: If `name` is not a valid period.
        
        Notes:
            - Membership uses half-open intervals: [start, end_exclusive).
        """
        if name not in periods_derived:
            raise KeyError(f"Unknown period name: {name!r}")
        if frame < 0 or frame >= experiment_total_frames:
            return False
        
        info = periods_derived[name]
        return (frame >= info["start_frame"]) and (frame < info["end_frame_exclusive"])
    
    return {
        "period_by_frame": period_by_frame,
        "period_by_frames": period_by_frames,
        "in_period": in_period,
    }

#%% CELL 04 — PUBLIC API

def create_time_bundle(frame_rate: int, period_data: dict = None) -> MappingProxyType:
    """Create immutable time bundle for export."""
    time_functions = create_time_functions(frame_rate)
    
    # Only create query functions if period data is available
    if period_data:
        query_functions = create_period_query_functions(period_data)
        _bundle = {**time_functions, **query_functions}
    else:
        _bundle = time_functions
    
    return MappingProxyType(_bundle)

# This will be set by the main experiment.py controller
_TIME: MappingProxyType = None
