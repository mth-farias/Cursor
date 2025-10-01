#%% CELL 00 — HEADER & OVERVIEW
"""
{{COMMIT_DETAILS}}
# <github.com/YourLab/Repo>
# <commit_hash>
# <DD-MM-YYYY HH:MM:SS>

BehaviorClassifier/_qc_error_flag.py

Overview
	QC module for the BehaviorClassifier pipeline.
	Performs:
	- Pre-flight fatal checks (schema, stimulus count/duration, timeline alignment, pose presence/length).
	- Post-scoring quality checks (NaN fractions, baseline exploration, pose view health).
	- Appends normalized rows to ERROR/FLAG reports and saves minimal artifacts for triage.

Public API
	Exports a single read-only bundle: BC_QC (MappingProxyType):
	- "run_pre_flight": execute all fatal input checks and log errors
	- "run_post_scoring_flags": execute all non-fatal flag checks and log flags
	- "append_error": append a row to the ERROR report
	- "append_flag": append a row to the FLAG report
	- "save_artifacts": persist tracked/pose/scored views for flagged/error cases
	- "is_file_already_classified": check if a session has been processed before

Usage
	from BehaviorClassifier import BC_QC
	BC_QC["run_pre_flight"](df_tracked, df_pose, expected_stim_count, expected_stim_frames, required_pose, session_id, error_report_path)
	BC_QC["run_post_scoring_flags"](df_scored, df_pose, baseline_mask_walk, session_id, flag_report_path)
"""


#%% CELL 01 — IMPORTS

from __future__ import annotations

"""Consolidated imports: stdlib → typing → third-party (no local imports here)."""

# Standard library
from pathlib import Path
from types import MappingProxyType
import sys

# Typing
from typing import Optional

# Third-party
import pandas as pd


#%% CELL 01.1 — PACKAGE IMPORTS (CONFIG SHIM)
"""
Make the repo root importable in notebooks/Colab so absolute package imports work.
No effect when installed as a package. Idempotent and policy-light.
"""
ROOT = Path(__file__).resolve().parents[1]  # repo root containing Config/ and BehaviorClassifier/
if (p := str(ROOT)) not in sys.path:
	sys.path.insert(0, p)

# Local packages (read-only registries and grouped utils)
from Config import PATH, PARAM, EXPERIMENT
from BehaviorClassifier import BC_UTILS


#%% CELL 02 — CONSTANTS / POLICIES
"""
Purpose
	Local QC thresholds and formatting constants used only by this module.
	These are not shared elsewhere and mirror the original behavior exactly.
"""

# Stimulus duration tolerance (frames)
STIM_DURATION_JITTER_FRAMES = 2

# Centroid NaN tolerance (fraction of rows)
CENTROID_NAN_MAX_FRAC = 0.0001

# Baseline exploration (fraction of walk frames required)
BASELINE_MIN_WALK_FRAC = 0.20

# Behavior_Denoised NaN tolerance (fraction)
BEHAVIOR_DENOISED_NAN_MAX_FRAC = 0.01

# View NaN tolerance (fraction of rows)
VIEW_NAN_MAX_FRAC = 0.01

# Report formatting separators
# NOTE: legacy report separators removed; metrics strings are built inline.
REPORT_FIELD_SEP = " | "  # unused, kept for backward compatibility


#%% CELL 03 — CHECKPOINT REGISTRIES
"""
Purpose
	Define registries for QC checkpoints.
	- Keys: stable lower_snake tokens used in reports/filenames.
	- Values: short human-facing messages for summaries/UI.

Notes
	- Membership in CHECKPOINT_ERRORS vs CHECKPOINT_FLAGS determines fatality.
	- Dict insertion order is canonical only within this module.
"""

CHECKPOINT_ERRORS = {
	# schema/readability
	"error_reading_file":        "error reading file",

	# stimulus schedule
	"wrong_stimulus_count":      "wrong stimulus count",
	"wrong_stimulus_duration":   "wrong stimulus duration",

	# timeline alignment
	"timeline_misaligned":       "timeline misaligned",

	# centroid health
	"centroid_nan_exceeded":     "many centroid NaNs",

	# SLEAP integration
	"missing_sleap_file":        "missing sleap file",
	"sleap_len_mismatch":        "tracked/sleap length mismatch",
}

CHECKPOINT_FLAGS = {
	# SLEAP view quality
	"view_nan_exceeded":         "many sleap view NaNs",

	# behavior annotation quality
	"behavior_nan_exceeded":     "many Behavior NaNs",

	# baseline exploration (legacy internal code = 'no_exploration')
	"no_exploration":            "low baseline exploration",
}


#%% CELL 04 — HELPERS / CORE LOGIC
"""
Pure helpers implementing QC computations.
- Stateless; no I/O; no printing.
- Vectorized where possible; policy-light (thresholds live in CELL 02).

Sub-cells
	04.1 — Stimulus checks
	04.2 — Tracked data health
	04.3 — SLEAP / pose checks
	04.4 — Behavior output checks (post-scoring)
"""


#%% CELL 04.1 — Stimulus checks
"""
Helpers for stimulus segmentation tolerance.
Note:
	We call BC_UTILS["stimulus"]["onsets"] and ["pulse_durations"] directly at call-sites.
	No local wrappers here to avoid duplication.
"""

def _durations_within_tolerance(
	durations: list[int],
	expected_frames: int,
	jitter_frames: int,
) -> bool:
	"""
	Check if all pulse durations are within ±jitter of an expected length.

	Args:
		durations: Pulse lengths in frames.
		expected_frames: Expected pulse length (frames).
		jitter_frames: Allowed absolute deviation (frames).

	Returns:
		bool: True if every duration is within tolerance; False otherwise.

	Notes:
		Pure comparison; no side effects. Decision thresholds live in CELL 02.
	"""
	if expected_frames < 0 or jitter_frames < 0:
		raise ValueError("expected_frames and jitter_frames must be >= 0")
	lo = expected_frames - jitter_frames
	hi = expected_frames + jitter_frames
	return all(lo <= d <= hi for d in durations)


#%% CELL 04.2 — Tracked data health
"""
Helpers for tracked-table integrity.
Pure computations only; callers pass concrete columns from PARAM (SSOT).
"""

def _nan_fraction_any(df: pd.DataFrame, columns: list[str]) -> float:
	"""
	Fraction of rows with at least one NaN across the specified columns.

	Args:
		df: Tracked dataframe.
		columns: Column names to inspect for NaNs (e.g., ['position_x','position_y']).

	Returns:
		float: Proportion in [0, 1] of rows that contain any NaN across the columns.

	Notes:
		Vectorized over the given columns; no side effects.
		Raises early on empty input to avoid silent success.
	"""
	if not columns:
		raise ValueError("columns must be a non-empty list of column names")
	return float(df[columns].isna().any(axis=1).mean())


#%% CELL 04.3 — SLEAP / pose checks
"""
Helpers for pose-table integrity.
Pure computations only; no I/O, no printing.
"""

def _lengths_match(n_tracked: int, n_pose: int) -> bool:
	"""
	Check if tracked and pose tables have identical row counts.

	Args:
		n_tracked: Number of rows in the tracked table.
		n_pose: Number of rows in the pose table.

	Returns:
		bool: True if lengths match exactly; False otherwise.

	Notes:
		Pure comparison; decision logic (error vs. continue) is handled by callers.
	"""
	if n_tracked < 0 or n_pose < 0:
		raise ValueError("lengths must be non-negative")
	return n_tracked == n_pose


#%% CELL 04.4 — Behavior output checks (post-scoring)
"""
Helpers for post-scoring integrity.
Pure computations only; reuse _nan_fraction_any from CELL 04.2.

Notes
	- Behavior NaN health: _nan_fraction_any(df_scored, ["Behavior_Denoised"])
	  Compare against BEHAVIOR_DENOISED_NAN_MAX_FRAC (CELL 02).
	- Baseline exploration: use _fraction_true(mask) on a boolean mask
	  representing 'walk' within the baseline window; compare against
	  BASELINE_MIN_WALK_FRAC (CELL 02).
"""

def _fraction_true(mask: pd.Series) -> float:
	"""
	Proportion of True values in a boolean Series.

	Args:
		mask: Boolean Series aligned to the rows of interest (e.g., baseline window).

	Returns:
		float: Proportion in [0, 1] of True entries.

	Notes:
		No side effects. NaNs are ignored by treating them as False via .fillna(False).
	"""
	if mask.dtype != bool and mask.dtype != "boolean":
		# Be permissive with nullable boolean; coerce via astype(bool) if needed upstream.
		pass
	return float(mask.fillna(False).mean())


#%% CELL 05 — PRE-FLIGHT: already classified? (orchestration probe)
"""
Boolean probe used by the orchestrator to skip work.
Returns True if the session/file has already been handled by the pipeline:
    - A *good* scored file exists, OR
    - A *flagged* scored file exists, OR
    - An error-tracked copy exists (fatal QC already handled).

Notes
    - No I/O mutation, just existence checks.
    - Path policy is centralized in Config.path (PATH[...] helpers).
"""

def is_file_already_classified(file_stem: str) -> bool:
	"""Return True if this session has been previously processed.

	Args:
		file_stem: Base filename (without extension) identifying the session.

	Returns:
		bool: True when any scored, flagged, or error-tracked artifact exists.
	"""
	# 1) Has final good Scored?
	scored_path: Path = PATH["scored_path"](file_stem)
	if scored_path.exists():
		return True

	# 2) Has a flagged Scored?
	flag_scored_path: Path = PATH["flag_scored_path"](file_stem)
	if flag_scored_path.exists():
		return True

	# 3) Has an error-tracked copy? (fatal already processed)
	error_tracked_copy: Path = PATH["error_tracked_copy_path"](
		PATH["tracked_name"](file_stem)
	)
	if error_tracked_copy.exists():
		return True

	return False


#%% CELL 06 — ERROR CHECKS (pre-flight, fatal)
"""
Pre-flight fatal checks.
Pure helpers returning (ok: bool, metrics: str). No I/O, no printing.

Sub-cells
	06.1 — Schema validation
	06.2 — Timeline alignment
	06.3 — Stimulus schedule
	06.4 — Centroid NaN health
	06.5 — Pose presence & length
"""

#%% CELL 06.1 — Schema validation
"""
Validate dataframe schema against PARAM registry:
- Unknown columns
- Declared dtypes
- Optional domain constraints
"""

def _dtype_matches_contract(series: pd.Series, expected: str) -> bool:
	"""
	Return True if the Series dtype matches an expected simple contract.

	Args:
		series: Input pandas Series.
		expected: Expected type string (e.g. 'float', 'int', 'bool', 'str').

	Returns:
		bool: True if dtype is compatible; False otherwise.
	"""
	expected = (expected or "").lower()
	if expected in ("float", "float64"):
		return pd.api.types.is_float_dtype(series)
	if expected in ("int", "int64", "int32"):
		return pd.api.types.is_integer_dtype(series)
	if expected in ("bool", "boolean"):
		# Accept pandas boolean and numeric {0,1}
		return pd.api.types.is_bool_dtype(series) or set(series.dropna().unique()).issubset({0, 1, False, True})
	if expected in ("str", "string", "category"):
		return pd.api.types.is_string_dtype(series) or pd.api.types.is_categorical_dtype(series)
	return True  # permissive default


def _check_schema(df: pd.DataFrame) -> tuple[bool, str]:
	"""
	Validate that a dataframe conforms to the PARAM registry.

	Args:
		df: DataFrame to validate.

	Returns:
		(ok, metrics):
			ok: True if schema is valid; False otherwise.
			metrics: Compact 'k=v; ...' string describing the first violation (empty if ok).
	"""
	unknown = [c for c in df.columns if c not in PARAM]
	if unknown:
		return False, f"unknown={','.join(unknown)}"

	for col in df.columns:
		spec = PARAM[col]
		expected = str(spec.get("type", "")).lower()
		if expected and not _dtype_matches_contract(df[col], expected):
			return False, f"col={col}; expected={expected}; actual={df[col].dtype}"

		domain = spec.get("domain", None)
		if domain:
			try:
				if len(domain) == 2:
					lo = float(domain[0]); hi = float(domain[1])
					bad_vals = df[col][(df[col] < lo) | (df[col] > hi)].dropna().unique()
					if len(bad_vals) > 0:
						return False, f"col={col}; min={lo}; max={hi}; bad={'|'.join([str(v) for v in bad_vals])}"
					continue
			except Exception:
				pass
			allowed = set(domain)
			bad_vals = [str(v) for v in pd.unique(df[col].dropna()) if v not in allowed]
			if bad_vals:
				return False, f"col={col}; bad={'|'.join(bad_vals)}; allowed={'|'.join([str(v) for v in allowed])}"

	return True, ""


#%% CELL 06.2 — Timeline alignment
"""
Ensure tracked table has enough headroom and tail to cover
Baseline and Experiment periods defined in EXPERIMENT.
"""

def _check_timeline_alignment(df_tracked: pd.DataFrame) -> tuple[bool, str]:
	"""
	Ensure tracked table spans baseline and experiment periods.

	Args:
		df_tracked: Tracked dataframe.

	Returns:
		(ok, metrics): ok True if alignment valid; metrics string otherwise.
	"""
	stim_label = EXPERIMENT["ALIGNMENT_STIM"]
	stim_info = EXPERIMENT["STIMULI"][stim_label]
	column_name = stim_info["name"]
	if column_name not in df_tracked.columns:
		return False, f"failure=missing_column; label={stim_label}; name={column_name}"
	series = df_tracked[column_name]

	onset_idx = BC_UTILS["stimulus"]["onsets"](series)
	if not onset_idx:
		return False, "failure=no_onsets_detected"
	first_onset = int(onset_idx[0])

	periods = EXPERIMENT.get("EXPERIMENTAL_PERIODS", {})
	try:
		baseline_frames = int(periods["Baseline"]["duration_frames"])
		experiment_span = int(periods["Experiment"]["duration_frames"])
	except Exception:
		return False, "failure=period_durations_unavailable"

	experiment_start = max(0, first_onset - baseline_frames)
	expected_end = experiment_start + experiment_span
	observed_end = int(len(df_tracked))

	if first_onset < baseline_frames:
		deficit = baseline_frames - first_onset
		return False, f"failure=short_head; baseline={baseline_frames}; onset={first_onset}; deficit={deficit}"

	if observed_end < expected_end:
		deficit = expected_end - observed_end
		return False, f"failure=short_tail; expected_end={expected_end}; observed_end={observed_end}; deficit={deficit}"

	return True, ""


#%% CELL 06.3 — Stimulus schedule
"""
Check number and duration of stimuli against expected values.
"""

def _check_stim_count(stim_onsets, expected_count: int) -> tuple[bool, str]:
	"""
	Verify onset count equals expected trial count.
	"""
	observed = int(len(stim_onsets))
	if observed == int(expected_count):
		return True, ""
	return False, f"obs={observed}; exp={int(expected_count)}"


def _check_stim_duration_tolerance(
	pulse_durations_map: dict[int, int],
	expected_frames: int,
	jitter_frames: int,
) -> tuple[bool, str]:
	"""
	Verify each pulse duration is within ±jitter frames of expected length.
	"""
	if expected_frames < 0 or jitter_frames < 0:
		raise ValueError("expected_frames and jitter_frames must be >= 0")
	lo = expected_frames - jitter_frames
	hi = expected_frames + jitter_frames
	outliers = {k: v for k, v in pulse_durations_map.items() if not (lo <= v <= hi)}
	if not outliers:
		return True, ""
	pairs = "; ".join(f"{k}={v}" for k, v in sorted(outliers.items()))
	return False, f"expected={expected_frames}±{jitter_frames}; outliers=[{pairs}]"


#%% CELL 06.4 — Centroid NaN health
"""
Check NaN fraction and contiguous runs for centroid positions.
"""

def _check_centroid_nan(
	df_tracked: pd.DataFrame,
	x_col: str,
	y_col: str,
	max_frac: float,
) -> tuple[bool, str]:
	"""
	Flag if centroid (x,y) NaN fraction exceeds threshold.
	"""
	if x_col not in df_tracked.columns or y_col not in df_tracked.columns:
		return False, "nan_fraction=1.0; max_run=0; hotspot=-1"

	mask = df_tracked[[x_col, y_col]].isna().any(axis=1).to_numpy()
	if mask.size == 0:
		return True, ""
	import numpy as _np
	frac = float(_np.mean(mask))
	max_run, hotspot, curr, start = 0, -1, 0, -1
	for i, v in enumerate(mask):
		if v:
			if curr == 0:
				start = i
			curr += 1
			if curr > max_run:
				max_run, hotspot = curr, start
		else:
			curr = 0
	if frac <= float(max_frac):
		return True, ""
	return False, f"nan_fraction={frac}; max_run={max_run}; hotspot={hotspot}"


#%% CELL 06.5 — Pose presence & length
"""
Check pose dataframe presence and alignment with tracked length.
"""

def _check_pose_presence(pose_df: Optional[pd.DataFrame], required: bool) -> tuple[bool, str]:
	"""
	Verify that a pose table is present when required.
	"""
	if not required:
		return True, ""
	if pose_df is None:
		return False, "pose=missing; required=True"
	return True, ""


def _check_pose_length_match(n_tracked: int, n_pose: int) -> tuple[bool, str]:
	"""
	Verify pose and tracked tables have identical lengths.
	"""
	if int(n_tracked) == int(n_pose):
		return True, ""
	return False, f"tracked={int(n_tracked)}; pose={int(n_pose)}"



#%% CELL 07 — FLAG CHECKS (post-scoring, non-fatal)
"""
Post-scoring flag checks.
Helpers return (ok: bool, metrics: str). No I/O, no printing.

Sub-cells
	07.1 — Behavior NaN health
	07.2 — Baseline exploration
	07.3 — Pose view health
"""


#%% CELL 07.1 — Behavior NaN health
"""
Check that Behavior_Denoised does not exceed NaN tolerance.
Uses _nan_fraction_any from CELL 04.2.
"""

def _check_behavior_nans(
	df_scored: pd.DataFrame,
	behavior_col: str,
	max_frac: float,
) -> tuple[bool, str]:
	"""
	Verify that NaN fraction in a behavior column does not exceed the threshold.

	Args:
		df_scored: Scored dataframe.
		behavior_col: Column name for the denoised behavior label.
		max_frac: Maximum tolerated NaN fraction in [0, 1].

	Returns:
		(ok, metrics):
			ok: True when NaN fraction ≤ max_frac.
			metrics: Empty on success; on failure, "frac=...; max=...".
	"""
	frac = _nan_fraction_any(df_scored, [behavior_col])
	ok = (frac <= float(max_frac))
	if ok:
		return True, ""
	return False, f"frac={frac:.6f}; max={float(max_frac):.6f}"


#%% CELL 07.2 — Baseline exploration
"""
Check that locomotion (e.g., walk) during baseline meets minimum fraction.
Uses _fraction_true from CELL 04.4.
"""

def _check_baseline_exploration(
	mask_walk: pd.Series,
	min_frac: float,
) -> tuple[bool, str]:
	"""
	Verify that walk fraction during baseline meets the minimum requirement.

	Args:
		mask_walk: Boolean Series (True if 'walk', False otherwise) for the baseline window.
		min_frac: Minimum required walk fraction in [0, 1].

	Returns:
		(ok, metrics):
			ok: True when walk fraction ≥ min_frac.
			metrics: Empty on success; on failure, "frac=...; min=...".
	"""
	frac = _fraction_true(mask_walk)
	ok = (frac >= float(min_frac))
	if ok:
		return True, ""
	return False, f"frac={frac:.6f}; min={float(min_frac):.6f}"


#%% CELL 07.3 — Pose view health
"""
Check that each pose view has NaN fraction within tolerance.
Reuses _nan_fraction_any from CELL 04.2.
"""

def _check_pose_views(
	df_pose: pd.DataFrame,
	view_cols: list[str],
	max_frac: float,
) -> tuple[bool, str]:
	"""
	Verify that each pose view column has NaN fraction within tolerance.

	Args:
		df_pose: Pose dataframe.
		view_cols: Column names for per-view pose data.
		max_frac: Maximum tolerated NaN fraction in [0, 1].

	Returns:
		(ok, metrics):
			ok: True when all views have NaN fraction ≤ max_frac.
			metrics: Empty on success; on failure, "max=...; bad=[col=frac; ...]".
	"""
	if not view_cols:
		raise ValueError("view_cols must be a non-empty list of column names")
	bad: list[str] = []
	for col in view_cols:
		frac = _nan_fraction_any(df_pose, [col])
		if frac > float(max_frac):
			bad.append(f"{col}={frac:.6f}")
	ok = (len(bad) == 0)
	if ok:
		return True, ""
	return False, f"max={float(max_frac):.6f}; bad=[{'; '.join(bad)}]"


#%% CELL 08 — I/O (atomic appends & artifacts)
"""
Atomic writers for QC reports and optional artifact capture.
- Policy-light: callers pass concrete Paths resolved via PATH[...] (SSOT).
- No printing. Atomic write/copy only.
"""

def _now_iso() -> str:
	"""
	Return the current timestamp in ISO 8601 format (seconds resolution).

	Returns:
		str: ISO timestamp (e.g., '2025-09-29T21:03:00').
	"""
	return pd.Timestamp.now().isoformat(timespec="seconds")


def _append_row_atomic(
	report_path: Path,
	row: dict,
	columns: list[str],
) -> None:
	"""
	Append a single row into a CSV with a stable column order.

	Args:
		report_path: Destination CSV path (resolved by caller via PATH[...]).
		row: Mapping of column → value for the new entry.
		columns: Canonical column order for the CSV.

	Notes:
		Uses BC_UTILS["io"]["write_csv_atomic"] to ensure durability.
	"""
	if report_path.exists():
		# Load existing and enforce canonical columns
		df = pd.read_csv(report_path)
		for c in columns:
			if c not in df.columns:
				# Add missing column with NaN
				df[c] = pd.NA
		# Reorder
		df = df[columns]
		df_new = pd.DataFrame([row], columns=columns)
		df_out = pd.concat([df, df_new], ignore_index=True)
	else:
		# First row defines schema
		df_out = pd.DataFrame([row], columns=columns)
	# Atomic write
	BC_UTILS["io"]["write_csv_atomic"](df_out, report_path, index=False)


def append_error(
	report_path: Path,
	session_id: str,
	code: str,
	message: str,
	details: str = "",
	timestamp: Optional[str] = None,
) -> None:
	"""
	Append one normalized ERROR row.

	Args:
		report_path: Path to ERROR report CSV.
		session_id: Stable session/file identifier.
		code: Error code (see CHECKPOINT_ERRORS).
		message: Short, human-facing description.
		details: Compact metrics string (optional).
		timestamp: Override timestamp; defaults to now() if None.
	"""
	cols = ["session_id", "code", "message", "details", "timestamp"]
	row = {
		"session_id": session_id,
		"code": code,
		"message": message,
		"details": details,
		"timestamp": _now_iso() if timestamp is None else timestamp,
	}
	_append_row_atomic(report_path, row, cols)


def append_flag(
	report_path: Path,
	session_id: str,
	code: str,
	message: str,
	severity: str = "warn",
	details: str = "",
	timestamp: Optional[str] = None,
) -> None:
	"""
	Append one normalized FLAG row.

	Args:
		report_path: Path to FLAG report CSV.
		session_id: Stable session/file identifier.
		code: Flag code (see CHECKPOINT_FLAGS).
		message: Short, human-facing description.
		severity: Text label (e.g., 'info', 'warn', 'high').
		details: Compact metrics string (optional).
		timestamp: Override timestamp; defaults to now() if None.
	"""
	cols = ["session_id", "code", "message", "severity", "details", "timestamp"]
	row = {
		"session_id": session_id,
		"code": code,
		"message": message,
		"severity": severity,
		"details": details,
		"timestamp": _now_iso() if timestamp is None else timestamp,
	}
	_append_row_atomic(report_path, row, cols)


def save_artifacts(
	tracked_src: Optional[Path],
	pose_src: Optional[Path],
	scored_src: Optional[Path],
	tracked_dst: Optional[Path],
	pose_dst: Optional[Path],
	scored_dst: Optional[Path],
) -> None:
	"""
	Best-effort snapshot copies for triage (no mutations if paths are None).

	Args:
		tracked_src: Source tracked CSV path (or None).
		pose_src: Source pose CSV path (or None).
		scored_src: Source scored CSV path (or None).
		tracked_dst: Destination tracked snapshot path (or None).
		pose_dst: Destination pose snapshot path (or None).
		scored_dst: Destination scored snapshot path (or None).

	Notes:
		Uses BC_UTILS["io"]["copy_atomic"] for file copies.
		Guarded by best-effort semantics to never break the session.
	"""
	def _copy_opt(src: Optional[Path], dst: Optional[Path]) -> None:
		if src is None or dst is None:
			return
		try:
			BC_UTILS["io"]["copy_atomic"](src, dst)
		except Exception:
			# best-effort; never break session
			pass

	_copy_opt(tracked_src, tracked_dst)
	_copy_opt(pose_src, pose_dst)
	_copy_opt(scored_src, scored_dst)


#%% CELL 09 — PUBLIC API
"""
Public bundle for QC checks and orchestrators.
- Exposes one immutable MappingProxyType: BC_QC.
- Callers import via: from BehaviorClassifier import BC_QC
"""

def run_pre_flight(
	df_tracked: pd.DataFrame,
	df_pose: Optional[pd.DataFrame],
	expected_stim_count: int,
	expected_stim_frames: int,
	required_pose: bool,
	session_id: str,
	error_report_path: Path,
) -> None:
	"""
	Run all fatal pre-flight checks and append any ERROR rows.

	Args:
		df_tracked: Tracked dataframe.
		df_pose: Pose dataframe or None.
		expected_stim_count: Expected number of stimuli (trials).
		expected_stim_frames: Expected duration of each stimulus (frames).
		required_pose: Whether pose is required (e.g., EXPERIMENT['POSE_SCORING']).
		session_id: Session identifier (used in report rows).
		error_report_path: Path to ERROR report CSV.
	"""
	# 1) Schema validation on tracked and pose
	ok, metrics = _check_schema(df_tracked)
	if not ok:
		append_error(error_report_path, session_id, "error_reading_file",
			CHECKPOINT_ERRORS["error_reading_file"], metrics)
		# abort further checks once a fatal error is logged
		return
	if df_pose is not None:
		ok_pose, metrics_pose = _check_schema(df_pose)
		if not ok_pose:
			append_error(error_report_path, session_id, "error_reading_file",
				CHECKPOINT_ERRORS["error_reading_file"], metrics_pose)
			return

	# 2) Timeline alignment
	ok, metrics = _check_timeline_alignment(df_tracked)
	if not ok:
		append_error(error_report_path, session_id, "timeline_misaligned",
			CHECKPOINT_ERRORS["timeline_misaligned"], metrics)
		return

	# 3) Stimulus count and duration
	# Determine alignment stim series and call BC_UTILS stimulus helpers
	stim_label = EXPERIMENT["ALIGNMENT_STIM"]
	stim_info = EXPERIMENT["STIMULI"][stim_label]
	column_name = stim_info["name"]
	series = df_tracked[column_name]
	onsets = BC_UTILS["stimulus"]["onsets"](series)
	# Count check
	ok, metrics = _check_stim_count(onsets, expected_stim_count)
	if not ok:
		append_error(error_report_path, session_id, "wrong_stimulus_count",
			CHECKPOINT_ERRORS["wrong_stimulus_count"], metrics)
		return
	# Duration check
	durations_map = BC_UTILS["stimulus"]["pulse_durations"](series)
	ok, metrics = _check_stim_duration_tolerance(
		durations_map,
		expected_stim_frames,
		STIM_DURATION_JITTER_FRAMES,
	)
	if not ok:
		append_error(error_report_path, session_id, "wrong_stimulus_duration",
			CHECKPOINT_ERRORS["wrong_stimulus_duration"], metrics)
		return

	# 4) Centroid NaN health
	ok, metrics = _check_centroid_nan(
		df_tracked,
		"NormalizedCentroidX",
		"NormalizedCentroidY",
		CENTROID_NAN_MAX_FRAC,
	)
	if not ok:
		append_error(error_report_path, session_id, "centroid_nan_exceeded",
			CHECKPOINT_ERRORS["centroid_nan_exceeded"], metrics)
		return

	# 5) Pose presence and length
	ok, metrics = _check_pose_presence(df_pose, required_pose)
	if not ok:
		append_error(error_report_path, session_id, "missing_sleap_file",
			CHECKPOINT_ERRORS["missing_sleap_file"], metrics)
		return
	if df_pose is not None:
		ok, metrics = _check_pose_length_match(len(df_tracked), len(df_pose))
		if not ok:
			append_error(error_report_path, session_id, "sleap_len_mismatch",
				CHECKPOINT_ERRORS["sleap_len_mismatch"], metrics)
			return


def run_post_scoring_flags(
	df_scored: pd.DataFrame,
	df_pose: Optional[pd.DataFrame],
	baseline_mask_walk: pd.Series,
	session_id: str,
	flag_report_path: Path,
) -> None:
	"""
	Run all non-fatal post-scoring flag checks and append any FLAG rows.

	Args:
		df_scored: Scored dataframe.
		df_pose: Pose dataframe or None.
		baseline_mask_walk: Boolean Series mask for baseline walk frames.
		session_id: Session identifier (used in report rows).
		flag_report_path: Path to FLAG report CSV.
	"""
	# 1) Behavior NaN health
	ok, metrics = _check_behavior_nans(
		df_scored,
		"Behavior_Denoised",
		BEHAVIOR_DENOISED_NAN_MAX_FRAC,
	)
	if not ok:
		append_flag(flag_report_path, session_id, "behavior_nan_exceeded",
			CHECKPOINT_FLAGS["behavior_nan_exceeded"], "warn", metrics)

	# 2) Baseline exploration
	ok, metrics = _check_baseline_exploration(baseline_mask_walk, BASELINE_MIN_WALK_FRAC)
	if not ok:
		append_flag(flag_report_path, session_id, "no_exploration",
			CHECKPOINT_FLAGS["no_exploration"], "warn", metrics)

	# 3) Pose view health
	if df_pose is not None:
		# Identify view columns (prefixed 'view_' or 'View' in old schema)
		view_cols = [c for c in df_pose.columns if c.lower().startswith("view")]
		if view_cols:
			ok, metrics = _check_pose_views(df_pose, view_cols, VIEW_NAN_MAX_FRAC)
			if not ok:
				append_flag(flag_report_path, session_id, "view_nan_exceeded",
					CHECKPOINT_FLAGS["view_nan_exceeded"], "warn", metrics)


# Immutable public bundle
_PUBLIC = {
	"is_file_already_classified": is_file_already_classified,
	"run_pre_flight": run_pre_flight,
	"run_post_scoring_flags": run_post_scoring_flags,
	"append_error": append_error,
	"append_flag": append_flag,
	"save_artifacts": save_artifacts,
}

BC_QC = MappingProxyType(_PUBLIC)

__all__ = ["BC_QC"]
