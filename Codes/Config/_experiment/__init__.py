#%% CELL 00 — HEADER & OVERVIEW
"""
{{COMMIT_DETAILS}}
# <github.com/YourLab/Repo>
# <commit_hash>
# <DD-MM-YYYY HH:MM:SS>

Config/_experiment/__init__.py

Overview
	Internal module exports for the experiment configuration system.
	This module aggregates processed bundles from internal modules and
	exports them for the main experiment.py controller to use.

Exports
	_STIMULI  → processed stimulus registry and validation
	_PERIODS  → processed period definitions and derived structures
	_TIME     → time conversion functions and period queries
	_REPORT   → report generation functions
	configure → function to configure all bundles with user parameters

Notes
	- This is a private package (_experiment) for internal processing
	- Main user interface remains in Config/experiment.py
	- All bundles are MappingProxyType for immutability
"""

#%% CELL 01 — IMPORTS

from __future__ import annotations

# Import modules, not the variables directly
from . import stimuli
from . import periods
from . import time
from . import report

# Export the static report
_REPORT = report._REPORT

# These will be set by configure()
_STIMULI = None
_PERIODS = None
_TIME = None

#%% CELL 02 — CONFIGURATION

def configure(frame_rate, experimental_periods, stimuli_config, alignment_stim):
    """
    Configure all experiment modules with user parameters.
    This updates the module-level _STIMULI, _PERIODS, _TIME bundles.
    
    Args:
        frame_rate: Video frame rate in fps
        experimental_periods: User-defined period specifications
        stimuli_config: User-defined stimulus registry
        alignment_stim: Name of canonical alignment stimulus
    """
    global _STIMULI, _PERIODS, _TIME
    
    # Configure time functions first
    time_bundle = time.create_time_bundle(frame_rate)
    
    # Configure periods (needs time functions)
    periods_bundle = periods.create_periods_bundle(
        experimental_periods,
        time_bundle["seconds_to_frames"],
        time_bundle["frames_to_seconds"]
    )
    
    # Update time bundle with period data for query functions
    time_bundle = time.create_time_bundle(frame_rate, periods_bundle)
    
    # Configure stimuli (needs time functions)
    stimuli_bundle = stimuli.create_stimuli_bundle(
        stimuli_config,
        alignment_stim,
        time_bundle["seconds_to_frames"]
    )
    
    # Update module-level variables in this module
    _TIME = time_bundle
    _PERIODS = periods_bundle
    _STIMULI = stimuli_bundle
    
    # Also update the individual module variables for consistency
    time._TIME = time_bundle
    periods._PERIODS = periods_bundle
    stimuli._STIMULI = stimuli_bundle

__all__ = ["_STIMULI", "_PERIODS", "_TIME", "_REPORT", "configure"]