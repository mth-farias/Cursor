#%% CELL 00 — HEADER & OVERVIEW
"""
{{COMMIT_DETAILS}}
# <github.com/YourLab/Repo>
# <commit_hash>
# <DD-MM-YYYY HH:MM:SS>

Config/_experiment/stimuli.py

Overview
	Stimulus validation and enrichment for the experiment configuration.
	Takes user-defined stimulus registry and alignment settings, validates
	all specifications, and produces derived structures with frame durations.

Processing
	- Validates stimulus registry format and detection mappings
	- Ensures alignment stimulus exists and is not ignored
	- Computes frame durations from second durations
	- Preserves trials=0 vs None semantics (explicit zero vs variable)

Exports
	_STIMULI → MappingProxyType bundle with STIMULI_DERIVED and validation
"""

#%% CELL 01 — IMPORTS

from __future__ import annotations

from types import MappingProxyType
from typing import TypedDict, Optional, Tuple, Callable
import numpy as np

# SCHEMA TYPES

class StimSpec(TypedDict, total=False):
    """Schema for a stimulus specification in the tracked CSV."""
    name: str                           # exact CSV column name
    trials: Optional[int]               # expected onsets; None=variable, 0=explicitly zero
    duration_sec: Optional[float]       # stimulus duration in seconds; None if variable
    detection: Tuple[int, int]          # (off_value, on_value) detector pair
    ignore: bool                        # whether to ignore this channel for alignment/QA

#%% CELL 02 — STIMULUS VALIDATION & ENRICHMENT

def process_stimuli(
    stimuli: dict[str, StimSpec],
    alignment_stim: str,
    seconds_to_frames_func: Callable
) -> dict:
    """
    Validate stimulus registry and compute derived fields.
    
    Args:
        stimuli: User-defined stimulus registry
        alignment_stim: Name of canonical alignment stimulus
        seconds_to_frames_func: Function to convert seconds to frames
        
    Returns:
        dict: STIMULI_DERIVED with validated and enriched stimulus specs
        
    Raises:
        ValueError: If validation fails or alignment stimulus issues
    """
    # Alignment stimulus must exist
    if alignment_stim not in stimuli:
        raise ValueError(f"ALIGNMENT_STIM '{alignment_stim}' not present in STIMULI.")
    
    _seen_names: set[str] = set()
    stimuli_derived: dict[str, dict] = {}
    
    for label, spec in stimuli.items():
        # CSV column name
        name = spec.get("name")
        if not isinstance(name, str) or not name:
            raise ValueError(f"Stimulus '{label}' missing non-empty 'name'.")
        if name in _seen_names:
            raise ValueError(f"Duplicate stimulus CSV column name: {name!r}.")
        _seen_names.add(name)
        
        # Detection pair
        detection = spec.get("detection")
        if not (isinstance(detection, tuple) and len(detection) == 2):
            raise ValueError(f"Stimulus '{label}' must define 'detection' as (off, on).")
        off_val, on_val = detection
        if off_val == on_val:
            raise ValueError(f"Stimulus '{label}' has identical off/on detection values.")
        
        # Trials (0 is allowed and means literally zero; None means variable)
        trials = spec.get("trials", None)
        if trials is not None and (not isinstance(trials, int) or trials < 0):
            raise ValueError(f"Stimulus '{label}' has invalid 'trials'={trials!r}.")
        
        # Duration (optional, must be positive if provided)
        dur_sec = spec.get("duration_sec", None)
        if dur_sec is not None:
            if (not isinstance(dur_sec, (int, float))) or (not np.isfinite(dur_sec)) or (dur_sec <= 0):
                raise ValueError(f"Stimulus '{label}' has invalid 'duration_sec'={dur_sec!r}.")
            dur_frames = int(seconds_to_frames_func(float(dur_sec)))
        else:
            dur_frames = None
        
        # Ignore flag
        ignore = bool(spec.get("ignore", False))
        
        # Final derived entry (preserves trials==0 vs None semantics)
        stimuli_derived[label] = {
            "name": name,
            "trials": trials,
            "duration_sec": None if dur_frames is None else float(dur_sec),
            "duration_frames": dur_frames,
            "detection": (off_val, on_val),
            "ignore": ignore,
        }
    
    # Alignment stimulus must not be ignored
    if stimuli_derived.get(alignment_stim, {}).get("ignore", False):
        raise ValueError(f"ALIGNMENT_STIM '{alignment_stim}' is marked 'ignore=True'.")
    
    return stimuli_derived

#%% CELL 03 — PUBLIC API

def create_stimuli_bundle(
    stimuli: dict[str, StimSpec],
    alignment_stim: str,
    seconds_to_frames_func: Callable
) -> MappingProxyType:
    """Create immutable stimulus bundle for export."""
    stimuli_derived = process_stimuli(stimuli, alignment_stim, seconds_to_frames_func)
    
    _bundle = {
        "STIMULI_DERIVED": stimuli_derived,
    }
    
    return MappingProxyType(_bundle)

# This will be set by the main experiment.py controller
_STIMULI: MappingProxyType = None
