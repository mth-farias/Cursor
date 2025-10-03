#%% CELL 00 — HEADER & SCOPE
'''
{{COMMIT_DETAILS}}
#<github.com/MoitaLab/Repo>
#<full_commit_hash>
#<DD-MM-YYYY HH:MM:SS>

experiment.py

Overview:
  Experiment-level constants and deterministic derivations.
  Defines the experimental paradigm shared across runs:
    - timebase (fps)
    - period schedule (durations in sec and frames)
    - stimuli registry and alignment choice
    - arena geometry
    - filename/grouping metadata
  Establishes the seconds↔frames conversion policy
  and derives cumulative ranges for each period.

Notes:
  - Pose scoring toggle: set POSE_SCORING=True when pose.csv is present and used.

Dependencies:
  Upstream: none (pure constants + derivations)
  Downstream: all scoring/classification modules that need experiment facts
'''

#%% CELL 01 — SCHEMA TYPES
"""
Typed schemas for registry entries to catch typos at development time.
Placed before CELL 02 so STIMULI/EXPERIMENTAL_PERIODS can be typed.
"""
from typing import TypedDict
from types import MappingProxyType as _RO

class StimSpec(TypedDict, total=False):
    name: str                     # exact CSV column title (e.g., "Stim0")
    trials: int | None            # expected onsets per run, or None if variable
    duration_sec: float | None    # stimulus length in seconds, or None if variable
    detection: tuple[int, int]    # (off_value, on_value) marking onsets
    ignore: bool                  # whether this channel is ignored for alignment/QA

class PeriodSpec(TypedDict, total=False):
    duration_sec: float           # period length in seconds


#%% CELL 02 — USER INPUT
"""
Authoritative experiment-level inputs. Purely declarative (no derivations).

Includes:
- Pose scoring toggle
- Filename/grouping metadata
- Stimulus registry and alignment choice
- Period schedule (durations in seconds only)
- Timebase and arena geometry

Notes:
- POSE_SCORING: set True when pose.csv is present and used downstream.
- STIMULI keys are human-facing labels; field 'name' is the exact CSV column.
- EXPERIMENTAL_PERIODS durations are in seconds; frames/ranges are derived later.
"""


#%%% CELL 02.1 - IDENTITY & GROUPING
"""
Filename token schema and run-group metadata shared across analyses.
"""

# Whether pose tracking was recorded/used for this dataset
POSE_SCORING: bool = True

# Ordered tokens parsed from filenames
#   "<Experimenter>-<Geno>-<Schema>-<Sex>-<Age>-<FH>-<Cam>-<Timestamp>-<FlyID>.<ext>"
FILENAME_STRUCTURE: list[str] = [
    "Experimenter","Genotype","Protocol","Sex","Age",
    "Setup","Camera","Timestamp","FlyID","Extension",
]

# Token that defines experimental groups
GROUP_IDENTIFIER: str = "Protocol"

# Experimental groups (keys serve as display labels)
#   - id_value: token value in filename that defines this group
#   - color:    hex code for plotting, or None → auto palette
GROUPS: dict[str, dict] = {
    "Control": {"id_value": "20Control_3BlackOut", "color": "#645769"},
    "Loom":    {"id_value": "20Loom_3BlackOut",    "color": "#E35B29"},
}


#%%% CELL 02.2 — STIMULUS REGISTRY & ALIGNMENT
"""
Describe all stimulus channels in tracked CSVs and pick the canonical aligner.

Rules:
- Dict keys are human-facing labels (e.g., "RedLED", "GreenLED").
- Field `name` is the exact CSV column name (e.g., "Stim0", "Stim1").
- `trials`: expected onsets per run, or None if variable.
- `duration_sec`: stimulus length in seconds, or None if variable.
- `detection`: (off_value, on_value) pair used to mark onsets.
- `ignore`: whether this channel is ignored for alignment/QA.
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


#%%% CELL 02.3 — PERIOD SCHEDULE
"""
Declare per-period durations in seconds. Frames and ranges are derived later.
"""

# Periods
# - EXPERIMENTAL_PERIODS must contain at least one non-aggregate entry ('Baseline').
# - "Experiment" always exists as the aggregate, even if only one period is defined.
EXPERIMENTAL_PERIODS: dict[str, PeriodSpec] = {
    "Baseline":    {"duration_sec": 300.0},
    "Stimulation": {"duration_sec": 300.0},
    "Recovery":    {"duration_sec": 300.0},
}


#%%% CELL 02.4 — TIMEBASE & ARENA
"""
Define the sampling rate and arena geometry.
"""

# Master tolerance [frames].
NOISE_TOLERANCE: int = 2

# Video frame rate [fps]
FRAME_RATE: int = 60

# Arena width [mm]
ARENA_WIDTH_MM: float = 30.0

# Arena height [mm]
ARENA_HEIGHT_MM: float = 30.0


#%% CELL 03 — DERIVED
"""
Derived values built from base definitions.
Split into time helpers, period enrichment, and stimulus enrichment.
"""


#%%% CELL 03.1 — TIME HELPERS & DERIVED CONSTANTS
"""
Establish universal seconds↔frames conversions.
All later derivations in this module must use these helpers.

Policy:
- All seconds→frames conversions use symmetric rounding (round(sec * FRAME_RATE)).
"""

# Seconds per frame (convenience, not for math)
SEC_PER_FRAME: float = 1.0 / FRAME_RATE

# Convert seconds → frames (symmetric rounding)
def seconds_to_frames(seconds: float) -> int:
	return int(round(seconds * FRAME_RATE))

# Convert frames → seconds (raw float)
def frames_to_seconds(frames: int) -> float:
	return frames / FRAME_RATE


#%%% CELL 03.2 — PERIOD ENRICHMENT
"""
Add derived frame counts and ranges to EXPERIMENTAL_PERIODS.
"""

# Compute duration_frames for each period
for name, info in EXPERIMENTAL_PERIODS.items():
	info["duration_frames"] = seconds_to_frames(info["duration_sec"])

# Compute cumulative ranges (half-open [start,end))
cursor = 0
for name, info in EXPERIMENTAL_PERIODS.items():
	start = cursor
	end = cursor + info["duration_frames"]
	info["range_frames"] = (start, end)
	cursor = end

# Add aggregate "Experiment" entry
EXPERIMENTAL_PERIODS["Experiment"] = {
	"duration_sec": sum(i["duration_sec"] for n,i in EXPERIMENTAL_PERIODS.items() if n!="Experiment"),
	"duration_frames": sum(i["duration_frames"] for n,i in EXPERIMENTAL_PERIODS.items() if n!="Experiment"),
	"range_frames": (0, cursor),
}


#%%% CELL 03.3 — STIMULUS ENRICHMENT
"""
Attach derived frame counts to STIMULI entries.
"""

for name, info in STIMULI.items():
	if info.get("duration_sec") is not None:
		info["duration_frames"] = seconds_to_frames(info["duration_sec"])
	else:
		info["duration_frames"] = None


#%%% CELL 03.4 — PERIOD QUERY HELPERS
"""
Convenience helpers for analytics: query period membership by frame.
Requires EXPERIMENTAL_PERIODS already enriched in CELL 06.2.
"""
def period_by_frame(frame: int) -> str:
	"""Return the period name whose [start,end) contains `frame`, or 'OutOfRange'."""
	for name, info in EXPERIMENTAL_PERIODS.items():
		if name == "Experiment":
			continue
		start, end = info["range_frames"]
		if start <= frame < end:
			return name
	return "OutOfRange"

def in_period(frame: int, name: str) -> bool:
	"""Return True if `frame` lies within the named period's [start,end)."""
	start, end = EXPERIMENTAL_PERIODS[name]["range_frames"]
	return start <= frame < end


#%% CELL 04 — REPORT
"""
Human-readable summary and quick QA checks when running this file directly.
- Prints FPS, pose scoring, arena geometry.
- Lists periods with seconds, frames, and [start,end) ranges.
- Lists stimuli with CSV column names and durations.
- QA: checks contiguity/monotonicity of period ranges and aggregate totals.
"""
if __name__ == "__main__":
	print("=== experiment.py summary ===")
	print(f"FRAME_RATE: {FRAME_RATE} fps   |   SEC_PER_FRAME: {SEC_PER_FRAME:.6f}")
	print(f"POSE_SCORING: {POSE_SCORING}")
	print(f"Arena (mm): {ARENA_WIDTH_MM} x {ARENA_HEIGHT_MM}\n")

	# Periods
	print("Periods:")
	parts = [(n, i) for n, i in EXPERIMENTAL_PERIODS.items() if n != "Experiment"]
	for name, info in parts:
		ds = info['duration_sec']
		df = info['duration_frames']
		rs, re = info['range_frames']
		print(f"  {name:<12} {ds:>7.2f} s  | {df:>7d} fr  | range: [{rs}, {re})")
	exp = EXPERIMENTAL_PERIODS["Experiment"]
	print(f"  {'Experiment':<12} {exp['duration_sec']:>7.2f} s  | {exp['duration_frames']:>7d} fr  | range: {exp['range_frames']}\n")

	# QA: contiguity & aggregate totals
	ok_order = all(parts[i][1]["range_frames"][1] == parts[i+1][1]["range_frames"][0]
	               for i in range(len(parts)-1)) and all(
	               parts[i][1]["range_frames"][0] < parts[i][1]["range_frames"][1]
	               for i in range(len(parts)))
	if not ok_order:
		print("[WARN] Period ranges are not contiguous/monotonic.")

	sum_frames = sum(i["duration_frames"] for _, i in parts)
	if sum_frames != exp["duration_frames"]:
		print("[WARN] Aggregate 'Experiment' frames do not equal sum of parts "
		      f"({sum_frames} != {exp['duration_frames']}).")

	sum_secs = sum(i["duration_sec"] for _, i in parts)
	if abs(sum_secs - exp["duration_sec"]) > 1e-9:
		print("[WARN] Aggregate 'Experiment' seconds do not equal sum of parts "
		      f"({sum_secs} != {exp['duration_sec']}).")

	# Stimuli
	print("\nStimuli (label → CSV column):")
	for label, info in STIMULI.items():
		name = info['name']
		trials = info.get('trials')
		ds = info.get('duration_sec')
		df = info.get('duration_frames')
		ignore = info.get('ignore', False)
		ds_str = "var" if ds is None else f"{ds:.3f}s"
		df_str = "var" if df is None else f"{df}fr"
		tr_str = "var" if trials is None else str(trials)
		ig_str = " (ignored)" if ignore else ""
		print(f"  {label:<12} → {name:<8} | trials: {tr_str:<4} | dur: {ds_str:>7} / {df_str:>6}{ig_str}")

	print(f"\nAlignment stimulus: {ALIGNMENT_STIM}")
	print("=== end summary ===")


#%% CELL 05 — BUNDLE: EXPERIMENT (read-only view)
"""
Assemble a read-only dict that mirrors the experiment surface for easy introspection.
This is a convenience façade; canonical symbols above remain the source of truth.
"""
_EXPERIMENT_RW = {
	# identity & grouping
	"POSE_SCORING": POSE_SCORING,
	"FILENAME_STRUCTURE": FILENAME_STRUCTURE,
	"GROUP_IDENTIFIER": GROUP_IDENTIFIER,
	"GROUPS": GROUPS,

	# timebase & arena
    "NOISE_TOLERANCE": NOISE_TOLERANCE,
	"FRAME_RATE": FRAME_RATE,
	"SEC_PER_FRAME": SEC_PER_FRAME,
	"ARENA_WIDTH_MM": ARENA_WIDTH_MM,
	"ARENA_HEIGHT_MM": ARENA_HEIGHT_MM,

	# stimuli & periods
	"ALIGNMENT_STIM": ALIGNMENT_STIM,
	"STIMULI": STIMULI,
	"EXPERIMENTAL_PERIODS": EXPERIMENTAL_PERIODS,

	# helpers (function references)
	"seconds_to_frames": seconds_to_frames,
	"frames_to_seconds": frames_to_seconds,
	"period_by_frame": period_by_frame,
	"in_period": in_period,
}

EXPERIMENT = _RO(_EXPERIMENT_RW)


#%% CELL 05.1 — PUBLIC SURFACE
"""
Public surface for experiment.py.
Downstream code should import only the read-only bundle EXPERIMENT.
"""
__all__ = ["EXPERIMENT"]



