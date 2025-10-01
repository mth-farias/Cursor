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
"""


#%% CELL 01 — IMPORTS & TYPES

from __future__ import annotations

"""
Define imports and schema types for stimuli and experimental periods.
"""

# Standard library
from types import MappingProxyType

# Typing
from typing import TypedDict, Optional, Tuple

# Third-party
import numpy as np


# SCHEMA TYPES

class StimSpec(TypedDict, total=False):
	"""Schema for a stimulus specification in the tracked CSV."""
	name: str                           # exact CSV column name
	trials: Optional[int]               # expected onsets; None=variable, 0=explicitly zero
	duration_sec: Optional[float]       # stimulus duration in seconds; None if variable
	detection: Tuple[int, int]          # (off_value, on_value) detector pair
	ignore: bool                        # whether to ignore this channel for alignment/QA


class PeriodSpec(TypedDict, total=False):
	"""Schema for an experimental period (declarative input)."""
	duration_sec: float                 # duration in seconds (must be > 0)


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
STIMULI: dict[str, StimSpec] = {
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
EXPERIMENTAL_PERIODS: dict[str, PeriodSpec] = {
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


#%% CELL 03 — DERIVED & VALIDATION
"""
Derived helpers and validated, deterministic structures:
	- Timebase helpers (scalar and vectorized)
	- Period enrichment with explicit ordering
	- Stimulus enrichment (frame durations) and validations
	- Fast period query helpers (scalar and vectorized)
"""


#%% CELL 03.1 — TIME HELPERS
"""
Seconds↔frames conversions. Accept scalars or NumPy arrays.
Rounding uses np.rint for stability (banker's rounding).

Conventions
	- Frame indexing is zero-based.
	- Period intervals are half-open: [start, end_exclusive).
"""

SEC_PER_FRAME: float = 1.0 / float(FRAME_RATE)  # seconds per frame


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
		- Uses np.rint (“banker’s rounding”) to keep .5 boundaries stable across
		  NumPy/Python and avoid jitter that can shift frames by ±1 at x.5.
	"""
	if FRAME_RATE <= 0:
		raise ValueError("FRAME_RATE must be > 0.")

	arr = np.asarray(seconds)
	frames = np.rint(arr * FRAME_RATE).astype(int)  # round to nearest int

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
	if FRAME_RATE <= 0:
		raise ValueError("FRAME_RATE must be > 0.")

	arr = np.asarray(frames, dtype=float)
	seconds = arr * SEC_PER_FRAME  # multiply by reciprocal

	return float(seconds) if np.isscalar(frames) else seconds


#%% CELL 03.2 — PERIOD ENRICHMENT & ORDERING
"""
Validate period durations, compute frame counts, and build deterministic
ordering arrays for O(1) lookups.
"""

# VALIDATE INPUT
if not isinstance(EXPERIMENTAL_PERIODS, dict) or not EXPERIMENTAL_PERIODS:
	raise ValueError("EXPERIMENTAL_PERIODS must be a non-empty dict.")

# Derive per-period info
_PERIOD_ORDER: list[str] = []        # insertion order of period names
_PERIOD_DUR_SEC: list[float] = []    # durations in seconds
_PERIOD_DUR_FRAMES: list[int] = []   # durations in frames

for pname, spec in EXPERIMENTAL_PERIODS.items():
	dur_sec = spec.get("duration_sec")
	if not isinstance(dur_sec, (int, float)):
		raise ValueError(f"Period '{pname}' missing numeric 'duration_sec'.")
	if not np.isfinite(dur_sec) or dur_sec <= 0:
		raise ValueError(f"Period '{pname}' has invalid duration_sec={dur_sec!r}.")

	_PERIOD_ORDER.append(pname)
	_PERIOD_DUR_SEC.append(float(dur_sec))
	_PERIOD_DUR_FRAMES.append(int(seconds_to_frames(dur_sec)))

# Frozen structures for downstream use
PERIOD_ORDER: tuple[str, ...] = tuple(_PERIOD_ORDER)
PERIOD_DUR_SEC: np.ndarray = np.asarray(_PERIOD_DUR_SEC, dtype=float)
PERIOD_DUR_FRAMES: np.ndarray = np.asarray(_PERIOD_DUR_FRAMES, dtype=int)

# Starts and ends in frames (half-open intervals)
PERIOD_STARTS: np.ndarray = np.concatenate(
	([np.array([0], dtype=int), np.cumsum(PERIOD_DUR_FRAMES[:-1], dtype=int)])
    )
PERIOD_ENDS_EXCLUSIVE: np.ndarray = PERIOD_STARTS + PERIOD_DUR_FRAMES

# Aggregate totals
EXPERIMENT_TOTAL_FRAMES: int = int(PERIOD_ENDS_EXCLUSIVE[-1])
EXPERIMENT_TOTAL_SECONDS: float = float(frames_to_seconds(EXPERIMENT_TOTAL_FRAMES))

# Derived per-period dict
PERIODS_DERIVED: dict[str, dict] = {
	name: {
		"duration_sec": float(PERIOD_DUR_SEC[i]),
		"duration_frames": int(PERIOD_DUR_FRAMES[i]),
		"start_frame": int(PERIOD_STARTS[i]),
		"end_frame_exclusive": int(PERIOD_ENDS_EXCLUSIVE[i]),
        }
	for i, name in enumerate(PERIOD_ORDER)
    }

# VALIDATION CHECKS

# Contiguity: next start == previous end
if not np.all(PERIOD_STARTS[1:] == PERIOD_ENDS_EXCLUSIVE[:-1]):
	raise ValueError("Periods are not contiguous (gaps or overlaps detected).")

# Durations must be positive and strictly increasing
if not (np.all(PERIOD_DUR_FRAMES > 0) and np.all(np.diff(PERIOD_ENDS_EXCLUSIVE) > 0)):
	raise ValueError("Invalid period durations or ordering.")


#%% CELL 03.3 — STIMULUS ENRICHMENT & VALIDATION
"""
Validate the stimulus registry and compute derived fields.

Key points
	- `trials` semantics:
		* `None` → variable/unspecified number of trials.
		* `0`    → explicitly zero expected trials (distinct from variable).
	- Strict validation, no silent fallbacks.
	- Derived: duration in frames when `duration_sec` is provided (> 0).

Produces
	- STIMULI_DERIVED: dict[str, dict]
	  {
	    name: str,                 # CSV column header (unique across stimuli)
	    trials: int | None,        # preserves 0 vs None semantics
	    duration_sec: float | None,
	    duration_frames: int | None,
	    detection: (off, on),      # tuple with distinct values
	    ignore: bool
	  }
"""

# Alignment stimulus must exist
if ALIGNMENT_STIM not in STIMULI:
	raise ValueError(f"ALIGNMENT_STIM '{ALIGNMENT_STIM}' not present in STIMULI.")

_seen_names: set[str] = set()
STIMULI_DERIVED: dict[str, dict] = {}

for label, spec in STIMULI.items():
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
		dur_frames = int(seconds_to_frames(float(dur_sec)))
	else:
		dur_frames = None

	# Ignore flag
	ignore = bool(spec.get("ignore", False))

	# Final derived entry (preserves trials==0 vs None semantics)
	STIMULI_DERIVED[label] = {
		"name": name,
		"trials": trials,
		"duration_sec": None if dur_frames is None else float(dur_sec),
		"duration_frames": dur_frames,
		"detection": (off_val, on_val),
		"ignore": ignore,
        }

# Alignment stimulus must not be ignored
if STIMULI_DERIVED.get(ALIGNMENT_STIM, {}).get("ignore", False):
	raise ValueError(f"ALIGNMENT_STIM '{ALIGNMENT_STIM}' is marked 'ignore=True'.")


#%% CELL 03.4 — PERIOD QUERY HELPERS
"""
Utilities to map frames to period names quickly (scalar and vectorized).

Depends on earlier derived variables:
	- PERIOD_ORDER: tuple[str, ...]  (canonical period ordering)
	- PERIOD_ENDS_EXCLUSIVE: np.ndarray[int] (exclusive end frame per period)
	- PERIODS_DERIVED: dict[str, dict] (start/end info per period)
	- EXPERIMENT_TOTAL_FRAMES: int (total frames in session)

Conventions
	- Frame indexing is zero-based.
	- Period membership uses half-open intervals: [start, end_exclusive).
	- Frames outside [0, EXPERIMENT_TOTAL_FRAMES) are "OutOfRange".
"""

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
	if frame < 0 or frame >= EXPERIMENT_TOTAL_FRAMES:
		return "OutOfRange"

	# Find the first end_exclusive strictly greater than frame.
	idx = int(np.searchsorted(PERIOD_ENDS_EXCLUSIVE, frame, side="right"))
	return PERIOD_ORDER[idx]


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
	idx = np.searchsorted(PERIOD_ENDS_EXCLUSIVE, arr, side="right")

	# Build output with "OutOfRange" default, then fill valid positions.
	names = np.array(PERIOD_ORDER, dtype=object)
	out = np.full(arr.shape, "OutOfRange", dtype=object)
	in_range = (arr >= 0) & (arr < EXPERIMENT_TOTAL_FRAMES)
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
	if name not in PERIODS_DERIVED:
		raise KeyError(f"Unknown period name: {name!r}")
	if frame < 0 or frame >= EXPERIMENT_TOTAL_FRAMES:
		return False

	info = PERIODS_DERIVED[name]
	return (frame >= info["start_frame"]) and (frame < info["end_frame_exclusive"])



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

	# Stimuli
	"STIMULI": STIMULI,
	"ALIGNMENT_STIM": ALIGNMENT_STIM,
	"STIMULI_DERIVED": STIMULI_DERIVED,

	# Periods
	"EXPERIMENTAL_PERIODS": EXPERIMENTAL_PERIODS,
	"PERIOD_ORDER": PERIOD_ORDER,
	"PERIOD_DUR_SEC": PERIOD_DUR_SEC,
	"PERIOD_DUR_FRAMES": PERIOD_DUR_FRAMES,
	"PERIOD_STARTS": PERIOD_STARTS,
	"PERIOD_ENDS_EXCLUSIVE": PERIOD_ENDS_EXCLUSIVE,
	"PERIODS_DERIVED": PERIODS_DERIVED,
	"EXPERIMENT_TOTAL_FRAMES": EXPERIMENT_TOTAL_FRAMES,
	"EXPERIMENT_TOTAL_SECONDS": EXPERIMENT_TOTAL_SECONDS,

	# Timebase & arena
	"NOISE_TOLERANCE": NOISE_TOLERANCE,
	"FRAME_RATE": FRAME_RATE,
	"SEC_PER_FRAME": SEC_PER_FRAME,
	"ARENA_WIDTH_MM": ARENA_WIDTH_MM,
	"ARENA_HEIGHT_MM": ARENA_HEIGHT_MM,

	# Helpers
	"seconds_to_frames": seconds_to_frames,
	"frames_to_seconds": frames_to_seconds,
	"period_by_frame": period_by_frame,
	"period_by_frames": period_by_frames,
	"in_period": in_period,
}

EXPERIMENT = MappingProxyType(_PUBLIC)
__all__ = ["EXPERIMENT"]


#%% CELL 05 — REPORT
"""
Human-readable summary of the EXPERIMENT bundle.
Prints key sections for quick inspection.
"""

if __name__ == "__main__":
	print("=== EXPERIMENT SUMMARY ===\n")

	print("Noise tolerance:", EXPERIMENT["NOISE_TOLERANCE"], "frames")
	print("Frame rate:", EXPERIMENT["FRAME_RATE"], "fps")
	print(
		"Arena:",
		EXPERIMENT["ARENA_WIDTH_MM"],
		"x",
		EXPERIMENT["ARENA_HEIGHT_MM"],
		"mm",
	)

	print("\n-- Periods --")
	for name in EXPERIMENT["PERIOD_ORDER"]:
		spec = EXPERIMENT["PERIODS_DERIVED"][name]
		start_f = spec["start_frame"]
		end_f = spec["end_frame_exclusive"] - 1  # inclusive display
		print(
			f"{name:12s} "
			f"{spec['duration_sec']:.1f} s "
			f"({spec['duration_frames']} frames), "
			f"frames {start_f}–{end_f}"
		)

	print(
		"\nTotal experiment:",
		EXPERIMENT["EXPERIMENT_TOTAL_SECONDS"],
		"s",
		f"({EXPERIMENT['EXPERIMENT_TOTAL_FRAMES']} frames)",
	)

	print("\n-- Stimuli --")
	for label, spec in EXPERIMENT["STIMULI_DERIVED"].items():
		dur_sec = spec["duration_sec"]
		dur_str = f"{dur_sec:.2f} s" if dur_sec is not None else "variable"
		print(
			f"{label:12s} "
			f"trials={spec['trials']} "
			f"dur={dur_str} "
			f"ignore={spec['ignore']}"
		)
