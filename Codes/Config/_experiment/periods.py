#%% CELL 00 — HEADER & OVERVIEW
"""
{{COMMIT_DETAILS}}
# <github.com/YourLab/Repo>
# <commit_hash>
# <DD-MM-YYYY HH:MM:SS>

Config/_experiment/periods.py

Overview
	Period validation and enrichment for the experiment configuration.
	Takes user-defined experimental periods, validates durations, computes
	frame counts, and builds deterministic ordering arrays for O(1) lookups.

Processing
	- Validates period durations are positive and finite
	- Computes frame durations and cumulative timing
	- Creates contiguous period boundaries (half-open intervals)
	- Builds derived structures for fast period queries

Exports
	_PERIODS → MappingProxyType bundle with all period-related structures
"""

#%% CELL 01 — IMPORTS

from __future__ import annotations

from types import MappingProxyType
from typing import TypedDict, Callable
import numpy as np

# SCHEMA TYPES

class PeriodSpec(TypedDict, total=False):
    """Schema for an experimental period (declarative input)."""
    duration_sec: float                 # duration in seconds (must be > 0)

#%% CELL 02 — PERIOD VALIDATION & ENRICHMENT

def process_periods(
    experimental_periods: dict[str, PeriodSpec],
    seconds_to_frames_func: Callable,
    frames_to_seconds_func: Callable
) -> dict:
    """
    Validate period durations, compute frame counts, and build deterministic
    ordering arrays for O(1) lookups.
    
    Args:
        experimental_periods: User-defined period specifications
        seconds_to_frames_func: Function to convert seconds to frames
        frames_to_seconds_func: Function to convert frames to seconds
        
    Returns:
        dict: Complete period bundle with all derived structures
        
    Raises:
        ValueError: If validation fails or periods are invalid
    """
    # VALIDATE INPUT
    if not isinstance(experimental_periods, dict) or not experimental_periods:
        raise ValueError("EXPERIMENTAL_PERIODS must be a non-empty dict.")
    
    # Derive per-period info
    _period_order: list[str] = []        # insertion order of period names
    _period_dur_sec: list[float] = []    # durations in seconds
    _period_dur_frames: list[int] = []   # durations in frames
    
    for pname, spec in experimental_periods.items():
        dur_sec = spec.get("duration_sec")
        if not isinstance(dur_sec, (int, float)):
            raise ValueError(f"Period '{pname}' missing numeric 'duration_sec'.")
        if not np.isfinite(dur_sec) or dur_sec <= 0:
            raise ValueError(f"Period '{pname}' has invalid duration_sec={dur_sec!r}.")
        
        _period_order.append(pname)
        _period_dur_sec.append(float(dur_sec))
        _period_dur_frames.append(int(seconds_to_frames_func(dur_sec)))
    
    # Frozen structures for downstream use
    period_order: tuple[str, ...] = tuple(_period_order)
    period_dur_sec: np.ndarray = np.asarray(_period_dur_sec, dtype=float)
    period_dur_frames: np.ndarray = np.asarray(_period_dur_frames, dtype=int)
    
    # Starts and ends in frames (half-open intervals)
    period_starts: np.ndarray = np.concatenate([
        np.array([0], dtype=int), 
        np.cumsum(period_dur_frames[:-1])
    ])
    period_ends_exclusive: np.ndarray = period_starts + period_dur_frames
    
    # Aggregate totals
    experiment_total_frames: int = int(period_ends_exclusive[-1])
    experiment_total_seconds: float = float(frames_to_seconds_func(experiment_total_frames))
    
    # Derived per-period dict
    periods_derived: dict[str, dict] = {
        name: {
            "duration_sec": float(period_dur_sec[i]),
            "duration_frames": int(period_dur_frames[i]),
            "start_frame": int(period_starts[i]),
            "end_frame_exclusive": int(period_ends_exclusive[i]),
        }
        for i, name in enumerate(period_order)
    }
    
    # VALIDATION CHECKS
    
    # Contiguity: next start == previous end
    if not np.all(period_starts[1:] == period_ends_exclusive[:-1]):
        raise ValueError("Periods are not contiguous (gaps or overlaps detected).")
    
    # Durations must be positive and strictly increasing
    if not (np.all(period_dur_frames > 0) and np.all(np.diff(period_ends_exclusive) > 0)):
        raise ValueError("Invalid period durations or ordering.")
    
    return {
        "PERIOD_ORDER": period_order,
        "PERIOD_DUR_SEC": period_dur_sec,
        "PERIOD_DUR_FRAMES": period_dur_frames,
        "PERIOD_STARTS": period_starts,
        "PERIOD_ENDS_EXCLUSIVE": period_ends_exclusive,
        "EXPERIMENT_TOTAL_FRAMES": experiment_total_frames,
        "EXPERIMENT_TOTAL_SECONDS": experiment_total_seconds,
        "PERIODS_DERIVED": periods_derived,
    }

#%% CELL 03 — PUBLIC API

def create_periods_bundle(
    experimental_periods: dict[str, PeriodSpec],
    seconds_to_frames_func: Callable,
    frames_to_seconds_func: Callable
) -> MappingProxyType:
    """Create immutable periods bundle for export."""
    period_data = process_periods(experimental_periods, seconds_to_frames_func, frames_to_seconds_func)
    return MappingProxyType(period_data)

# This will be set by the main experiment.py controller
_PERIODS: MappingProxyType = None
