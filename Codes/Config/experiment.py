#%% CELL 00 — HEADER & OVERVIEW
"""
{{COMMIT_DETAILS}}
# <github.com/YourLab/Repo>
# <commit_hash>
# <DD-MM-YYYY HH:MM:SS>

Config/experiment.py

Overview
	Defines the behavioral experiment paradigm for Drosophila.
	Includes frame rate, seconds↔frames conversion, experimental periods,
	stimulus registry, arena geometry, grouping policies, and helper queries.
	All information is exported as a single read-only bundle (EXPERIMENT).

Architecture
	This is the main controller that orchestrates internal processing modules:
	- User constants defined here (CELL 02)
	- Processing delegated to _experiment/ modules
	- Final EXPERIMENT bundle assembled from internal results
"""

#%% CELL 01 — IMPORTS & TYPES

from __future__ import annotations

"""
Define imports and schema types for stimuli and experimental periods.
"""

# Standard library
import sys
from pathlib import Path
from types import MappingProxyType


# Third-party
import numpy as np

# Package path setup (for safe absolute imports)
ROOT = Path(__file__).resolve().parents[1]  # .../Codes
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

#%% CELL 02 — USER INPUT
"""
Authoritative experiment-level inputs. Purely declarative (no derivations).

Includes
	- Pose scoring toggle
	- Filename/grouping metadata
	- Stimulus registry and alignment choice
	- Period schedule (durations in seconds only)
	- Timebase and arena geometry
"""


#%% CELL 02.1 — IDENTITY & GROUPING
"""
Filename token schema and run-group metadata shared across analyses.
"""

# Whether pose tracking was recorded/used for this dataset
POSE_SCORING: bool = True

# Ordered tokens parsed from filenames
# "<Experimenter>-<Genotype>-<Protocol>-<Sex>-<Age>-<Setup>-<Camera>-<Timestamp>-<FlyID>.<ext>"
FILENAME_STRUCTURE: list[str] = [
	"Experimenter", "Genotype", "Protocol", "Sex", "Age",
	"Setup", "Camera", "Timestamp", "FlyID", "Extension",
    ]

# Token that defines experimental groups
GROUP_IDENTIFIER: str = "Protocol"

# Experimental groups (keys serve as display labels)
# - id_value: token value in filename that defines this group
# - color:    hex code for plotting, or None → auto palette
GROUPS: dict[str, dict] = {
	"Control": {"id_value": "20Control_3BlackOut", "color": "#645769"},
	"Loom":    {"id_value": "20Loom_3BlackOut",    "color": "#E35B29"},
    }


#%% CELL 02.2 — STIMULUS REGISTRY & ALIGNMENT
"""
Describe stimulus channels in tracked CSVs and pick the canonical aligner.

Rules
	- Dict keys are human-facing labels (e.g., "RedLED", "GreenLED").
	- Field 'name' is the exact CSV column name (e.g., "Stim0", "Stim1").
	- 'trials': expected onsets per run.
		* None → variable/unspecified number of trials
		* 0    → explicitly zero expected trials (distinct from variable)
	- 'duration_sec': stimulus length in seconds, or None if variable.
	- 'detection': (off_value, on_value) pair used to mark onsets.
	- 'ignore': whether this channel is ignored for alignment/QC.
"""

# Name in STIMULI chosen as the canonical alignment stimulus
ALIGNMENT_STIM: str = "VisualStim"

# Stimulus registry
STIMULI: dict[str, dict] = {
	"VisualStim": {
		"name": "VisualStim",
		"trials": 23,
		"duration_sec": 0.5,
		"detection": (0, 1),
		"ignore": False,
        },
	"RedLED": {
		"name": "Stim0",
		"trials": 0,
		"duration_sec": 0.5,
		"detection": (0, 1),
		"ignore": False,
        },
	"GreenLED": {
		"name": "Stim1",
		"trials": 0,
		"duration_sec": 0.5,
		"detection": (0, 1),
		"ignore": False,
        },
    }


#%% CELL 02.3 — PERIOD SCHEDULE
"""
Declare per-period durations in seconds. Frames and ranges are derived later.
"""

# Periods
# - EXPERIMENTAL_PERIODS must contain at least one non-aggregate entry ('Baseline').
# - "Experiment" always derived as the aggregate, even if only one period is defined.
EXPERIMENTAL_PERIODS: dict[str, dict] = {
	"Baseline":    {"duration_sec": 300.0},
	"Stimulation": {"duration_sec": 300.0},
	"Recovery":    {"duration_sec": 300.0},
    }


#%% CELL 02.4 — TIMEBASE & ARENA
"""
Define the sampling rate, master tolerance, and arena geometry.
"""

# Master tolerance [frames]
NOISE_TOLERANCE: int = 2

# Video frame rate [fps]
FRAME_RATE: int = 60

# Arena geometry [mm]
ARENA_WIDTH_MM: float = 30.0
ARENA_HEIGHT_MM: float = 30.0


#%% CELL 03 — PROCESSING & ASSEMBLY
"""
Import internal processing modules and create the final EXPERIMENT bundle.
Delegates all computation to specialized modules while maintaining the
exact same functionality as the original monolithic implementation.
"""

# Import internal processing modules
from ._experiment.stimuli import create_stimuli_bundle
from ._experiment.periods import create_periods_bundle
from ._experiment.time import create_time_bundle
from ._experiment.report import _REPORT

# Create time conversion functions first (needed by other modules)
time_bundle = create_time_bundle(FRAME_RATE)  # Just time functions initially

# Create period bundle (needs time conversion functions)
periods_bundle = create_periods_bundle(
    EXPERIMENTAL_PERIODS,
    time_bundle["seconds_to_frames"],
    time_bundle["frames_to_seconds"]
)

# Update time bundle with period data for query functions
time_bundle = create_time_bundle(FRAME_RATE, periods_bundle)

# Create stimulus bundle (needs time conversion functions)
stimuli_bundle = create_stimuli_bundle(
    STIMULI,
    ALIGNMENT_STIM,
    time_bundle["seconds_to_frames"]
)


#%% CELL 04 — PUBLIC API
"""
Immutable public bundle: EXPERIMENT.
Contains both user-declared inputs and derived structures.
"""

_PUBLIC = {
	# Identity & grouping
	"POSE_SCORING": POSE_SCORING,
	"FILENAME_STRUCTURE": FILENAME_STRUCTURE,
	"GROUP_IDENTIFIER": GROUP_IDENTIFIER,
	"GROUPS": GROUPS,

	# Stimuli (user inputs + derived)
	"STIMULI": STIMULI,
	"ALIGNMENT_STIM": ALIGNMENT_STIM,
	**stimuli_bundle,

	# Periods (user inputs + derived)
	"EXPERIMENTAL_PERIODS": EXPERIMENTAL_PERIODS,
	**periods_bundle,

	# Timebase & arena (user inputs + derived)
	"NOISE_TOLERANCE": NOISE_TOLERANCE,
	"FRAME_RATE": FRAME_RATE,
	"ARENA_WIDTH_MM": ARENA_WIDTH_MM,
	"ARENA_HEIGHT_MM": ARENA_HEIGHT_MM,

	# Time functions and constants
	**time_bundle,
}

EXPERIMENT = MappingProxyType(_PUBLIC)
__all__ = ["EXPERIMENT"]


#%% CELL 05 — REPORT
"""
Human-readable summary of the EXPERIMENT bundle.
Prints key sections for quick inspection.
"""

if __name__ == "__main__":
	_REPORT["render_experiment_report"](EXPERIMENT)
