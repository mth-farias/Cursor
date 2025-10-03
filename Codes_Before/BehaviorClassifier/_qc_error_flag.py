#%% CELL 00 — MODULE OVERVIEW
'''
{{COMMIT_DETAILS}}
#<github.com/MoitaLab/Repo>
#<full_commit_hash>
#<DD-MM-YYYY HH:MM:SS>

_qc_error_flag.py


Overview:
	Centralized Quality Control (QC) for the behavior pipeline. Runs all
	pre-flight (fatal) error checks and post-classification (non-fatal) flag
	checks. QC owns REPORT persistence and saving of flagged dataframes so
	the orchestrator (_main) only publishes clean scored outputs.

Responsibilities:
	• Pre-flight “errors” (stop on first failure):
	  1) schema/readability, 2) stimulus count, 3) stimulus duration,
	  4) timeline alignment, 5) centroid NaN fraction,
	  6) pose presence (if applicable), 7) pose length match (if applicable).
	  On first failure:
	    – Append one line to the ERROR REPORT.
	    – Return False to caller.
	  If all pass: return True.

	• Post-class “flags” (log all, non-fatal):
	  – baseline exploration too low
	  – Behavior_Denoised NaN fraction too high
	  – pose view NaN fraction too high (if applicable)
	  For each triggered flag:
	    – Append one line to the FLAG REPORT.
	  Outcomes:
	    – Any flags → also save dataframe under flagged destination.
	    – Caller receives (ok, summary_codes):
	        ok=True,  summary_codes=[]                (clean)
	        ok=False, summary_codes=['FLAG_CODE']     (exactly one)
	        ok=False, summary_codes=['multiple']      (2+ flags; all logged)

REPORTs (single source of truth):
	Schema (three fixed columns; no timestamps/run IDs):
	  check_code | metrics | file_stem
	    – check_code: stable lower_snake identifier used across filenames/reports
	    – metrics: compact "k=v" blob (semicolon-separated pairs)
	    – file_stem: canonical identity from Config.path
	Persistence:
	  – ERROR REPORT: one line per file (first fatal only), append-only.
	  – FLAG REPORT: one line per triggered flag, append-only.
	  – Writers create files if missing and perform durable appends.

Public API
	BC_QC['error_check'](file_stem, df_tracked) -> bool
	  Run pre-flight. On first failure, log and return False; else True.

	BC_QC['flag_check'](file_stem, df_scored) -> tuple[bool, list[str]]
	  Run flags. Log all flags. If any flagged: save dataframe and return
	  (False, ['FLAG_CODE']) or (False, ['multiple']); else (True, []).
'''


#%% CELL 01 — IMPORTS
"""
Keep imports stable. Add BC_UTILS for shared mechanics:
  - onsets / pulse_durations: BC_UTILS["onsets"], BC_UTILS["pulse_durations"]
  - atomic CSV write: BC_UTILS["write_csv_atomic"]
"""

# stdlib
from pathlib import Path
import sys
import os

# typing
from typing import Optional, Tuple, List
from types import MappingProxyType

# third-party
import pandas as pd


#%%% CELL 01.1 — PACKAGE IMPORTS (CONFIG SHIM)
"""
Ensure Codes/ is importable for absolute package imports in notebooks/Colab.
No effect when running as an installed package.
"""
ROOT = Path(__file__).resolve().parents[1]  # .../Codes
if str(ROOT) not in sys.path:
	sys.path.insert(0, str(ROOT))

from Config import PATH, PARAM, EXPERIMENT  # read-only registries
from BehaviorClassifier import BC_UTILS  # shared, read-only mapping



#%% CELL 02 – QC CONSTANTS
"""
Purpose
Local thresholds and formatting constants used only by QC checks.
These are not shared with other modules.
"""

# stimulus duration tolerance (frames)
STIM_DURATION_JITTER_FRAMES = 2  # allowed deviation in frames

# centroid NaN tolerance (fraction of rows)
CENTROID_NAN_MAX_FRAC = 0.0001

# baseline exploration (fraction of walk frames required)
BASELINE_MIN_WALK_FRAC = 0.20

# Behavior_Denoised NaN tolerance (fraction)
BEHAVIOR_DENOISED_NAN_MAX_FRAC = 0.05

# view NaN tolerance (fraction of rows)
VIEW_NAN_MAX_FRAC = 0.05

# report formatting separators
REPORT_FIELD_SEP = " | "
METRICS_PAIR_SEP = "; "
METRICS_KV_SEP   = "="


#%% CELL 03 — CHECKPOINT REGISTRIES  [REPLACE THIS CELL]
"""
Purpose
  Define the registries for QC checkpoints.
  - Keys: stable QC tokens (lower_snake) used in reports and filenames.
  - Values: short human-facing messages for summaries/UI.

Notes
  - Membership in CHECKPOINT_ERRORS vs CHECKPOINT_FLAGS determines fatality.
  - Dict insertion order (Python ≥3.7) is canonical only for this module;
    the runner reads explicit order lists exposed via the public API.
"""

CHECKPOINT_ERRORS = {
    # schema/readability
    "error_reading_file":        "error reading file",

    # stimulus schedule
    "wrong_stimulus_count":      "wrong stim count",
    "wrong_stimulus_duration":   "wrong stimulus duration",

    # timeline coverage
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
    # Keep the code 'no_exploration' to remain compatible with existing REPORTs/artifacts.
    "no_exploration":            "low baseline exploration",
}



#%% CELL 04 — SHARED HELPERS
"""
Purpose
	Local utilities shared across QC checks. These are internal to this module
	(not exported) and intentionally minimal.
"""


#%% CELL 04.2 — METRICS FORMATTING
"""
Helpers
	_format_metrics(pairs)
		Return a compact "k=v; k=v" string using module separators.

Notes
	- Keys are sorted for deterministic output.
	- Booleans are rendered as 0/1 for compactness.
	- Floats are formatted with up to 6 significant digits.
"""

def _format_number(value) -> str:
	"""Return a compact string for numeric-like values."""
	# normalize booleans to 0/1
	if isinstance(value, bool):
		return "1" if value else "0"

	# format floats compactly while keeping readability
	if isinstance(value, float):
		# format with up to 6 significant digits, strip trailing zeros and dot
		formatted = f"{value:.6g}"
		return formatted.rstrip("0").rstrip(".") if "." in formatted else formatted

	# pass-through for ints and strings
	return str(value)


def _format_metrics(pairs: dict[str, object]) -> str:
	"""Return 'k=v; k=v' string from a dict using module separators."""
	if not pairs:
		return ""

	# sort keys for deterministic order
	items_sorted = sorted(pairs.items(), key=lambda item: item[0])

	# build "k=v" tokens
	tokens: list[str] = []
	for key, value in items_sorted:
		key_str = str(key)
		val_str = _format_number(value)
		# join key/value with the module-level KV separator
		token = f"{key_str}{METRICS_KV_SEP}{val_str}"
		tokens.append(token)

	# join tokens with the module-level pair separator
	return METRICS_PAIR_SEP.join(tokens)


#%% CELL 04.3 — WINDOW & FRACTION HELPERS
"""
Helpers
	_slice_baseline(first_stim_index)
		Return a slice covering [0, first_stim_index) for baseline computations.

	_nan_fraction(series)
		Return fraction of NaN values in a Series (0.0 if empty).

	_fraction_equal(series, target_value, start=None, end=None)
		Return fraction of entries equal to target_value within [start:end),
		excluding NaNs from the denominator. Returns 0.0 if no valid frames.
"""

def _slice_baseline(first_stim_index: int) -> slice:
	"""Return a half-open slice [0, first_stim_index) for baseline windows."""
	if first_stim_index is None or first_stim_index <= 0:
		return slice(0, 0)
	return slice(0, int(first_stim_index))


def _nan_fraction(series) -> float:
	"""Return the fraction of NaNs in a Series; 0.0 for empty input."""
	total_count = int(series.size) if series is not None else 0
	if total_count <= 0:
		return 0.0

	nan_count = int(series.isna().sum())
	return float(nan_count) / float(total_count)


def _fraction_equal(series, target_value, start: Optional[int] = None, end: Optional[int] = None) -> float:
	"""
	Return the fraction of entries equal to target_value in [start:end).
	NaN entries are excluded from the denominator. Returns 0.0 if no valid frames.
	"""
	if series is None or series.size == 0:
		return 0.0

	windowed = series.iloc[start:end] if (start is not None or end is not None) else series

	valid_mask = windowed.notna()
	valid_count = int(valid_mask.sum())
	if valid_count == 0:
		return 0.0

	match_count = int((windowed[valid_mask] == target_value).sum())
	return float(match_count) / float(valid_count)


#%%% CELL 04.4 — Is file already classified? (boolean only)
"""
Boolean probe used by the orchestrator to skip work:
  - True if a *good* scored file exists,
           OR a *flagged* scored file exists,
           OR an error-tracked copy exists (fatal QC already handled).
  - False otherwise.

Notes
  - No I/O mutation, just existence checks.
  - Path policy is centralized in Config.path.
"""

def is_file_already_classified(file_stem: str) -> bool:
    # 1) Has final good Scored?
    scored_path: Path = PATH["scored_path"](file_stem)
    if Path(scored_path).exists():
        return True

    # 2) Has a flagged Scored?
    flag_scored_path: Path = PATH["flag_scored_path"](file_stem)
    if Path(flag_scored_path).exists():
        return True

    # 3) Has an error-tracked copy? (fatal already processed)
    error_tracked_copy: Path = PATH["error_tracked_copy_path"](
        PATH["tracked_name"](file_stem)
    )
    if Path(error_tracked_copy).exists():
        return True

    return False


#%% CELL 05 — PRE-FLIGHT ERROR CHECKS (ORCHESTRATOR; NO I/O)  [REPLACE THIS CELL]
"""
Purpose
  Run fatal QC checks in canonical order (dict insertion order from
  CHECKPOINT_ERRORS). Stop on the first failure and return its code/metrics.

Contract
  _run_preflight(file_stem, df_tracked) -> tuple[bool, str, str]
    Returns:
      (ok, code, metrics)
      - ok: True if all checks passed; False on first failure.
      - code: lower_snake QC token from CHECKPOINT_ERRORS ('' if ok=True).
      - metrics: compact k=v; k=v string ('' if ok=True).
        (This is the blob that will be written as metrics_observed in the CSV.)

Notes
  - No persistence here. Report writing is handled later (Cell 07 / Cell 08).
  - Dispatch is resolved at call time so helper functions may live in later cells.
"""

def _run_preflight(file_stem: str, df_tracked) -> Tuple[bool, str, str]:
    """Run pre-flight checks in registry order; stop on first failure."""
    # map QC codes → local checker function names (exact, current names)
    check_dispatch: dict[str, str] = {
        "error_reading_file":    "_schema_ok",
        "wrong_stimulus_count":  "_check_stim_count",
        "wrong_stimulus_duration":"_check_stim_duration",
        "timeline_misaligned":   "_check_timeline_alignment",
        "centroid_nan_exceeded": "_check_centroid_nan",
        "missing_sleap_file":    "_check_sleap_presence",
        "sleap_len_mismatch":    "_check_sleap_length",
    }

    for check_code in CHECKPOINT_ERRORS.keys():
        function_name = check_dispatch.get(check_code)
        if function_name is None:
            continue

        checker = globals().get(function_name)
        if checker is None:
            continue

        # pass the right arguments per checker signature
        if check_code in ("missing_sleap_file", "sleap_len_mismatch"):
            ok, metrics = checker(df_tracked, file_stem)
        else:
            ok, metrics = checker(df_tracked)

        if not ok:
            return False, check_code, metrics

    # all wired fatal checks passed
    return True, "", ""


#%% CELL 05.1 — Schema: dtype & domain validation  [REPLACE THIS CELL]
"""
Purpose
  Validate that tracked/pose dataframes conform to PARAM: known columns,
  dtype contract, and domain contract.

Notes
  - Domain spec supports:
      • Enumerations:        domain = [v1, v2, ...]      (exact equality)
      • Numeric ranges:      domain = [min, max]         (inclusive, continuous)
      • Booleans as enums:   domain = [0,1] or [False,True]
"""

from typing import Iterable

def _dtype_matches_contract(series: pd.Series, expected: str) -> bool:
    """Return True if pandas dtype matches an expected simple contract."""
    expected = (expected or "").lower()
    if expected in ("float", "float64"):
        return pd.api.types.is_float_dtype(series)
    if expected in ("int", "int64", "int32"):
        return pd.api.types.is_integer_dtype(series)
    if expected in ("bool", "boolean"):
        return pd.api.types.is_bool_dtype(series) or set(series.dropna().unique()).issubset({0,1,False,True})
    if expected in ("str", "string", "category"):
        return pd.api.types.is_string_dtype(series) or pd.api.types.is_categorical_dtype(series)
    return True  # permissive default

def _domain_enum_violations(series: pd.Series, domain: Iterable) -> list[str]:
    allowed = set(domain)
    bad = []
    for v in pd.unique(series.dropna()):
        if v not in allowed:
            bad.append(str(v))
    return bad

def _domain_range_violations(series: pd.Series, lo: float, hi: float, eps: float = 0.0) -> list[str]:
    bad_vals = series[(series < lo - eps) | (series > hi + eps)]
    return [f"{v}" for v in pd.unique(bad_vals.dropna())]

def _schema_ok(df: pd.DataFrame) -> tuple[bool, str]:
    # unknown names → fail
    unknown_columns = [column_name for column_name in df.columns if column_name not in PARAM]
    if unknown_columns:
        metrics = _format_metrics({"unknown": ",".join(unknown_columns)})
        return False, metrics

    # dtype and domain checks for each present, PARAM-known column
    for column_name in df.columns:
        spec = PARAM[column_name]

        # dtype contract
        expected_type = str(spec.get("type", "")).lower()
        if not _dtype_matches_contract(df[column_name], expected_type):
            metrics = _format_metrics({
                "col": column_name,
                "expected": expected_type or "unspecified",
                "actual": str(df[column_name].dtype),
            })
            return False, metrics

        # domain contract (optional)
        domain = spec.get("domain", None)
        if domain:
            is_enum = False
            if len(domain) == 2:
                # Try numeric range first; if it fails, fall back to enum
                try:
                    lo = float(domain[0]); hi = float(domain[1])
                    bad = _domain_range_violations(df[column_name], lo, hi, eps=0.0)
                    if bad:
                        metrics = _format_metrics({
                            "col": column_name,
                            "min_allowed": lo,
                            "max_allowed": hi,
                            "bad": "|".join(sorted(bad)),
                        })
                        return False, metrics
                    continue
                except Exception:
                    is_enum = True
            else:
                is_enum = True

            if is_enum:
                bad = _domain_enum_violations(df[column_name], domain)
                if bad:
                    metrics = _format_metrics({
                        "col": column_name,
                        "bad": "|".join(sorted(bad)),
                        "allowed": "|".join([str(v) for v in domain]),
                    })
                    return False, metrics

    return True, ""


#%% CELL 05.2 — Error: wrong stimulus count  [REPLACE THIS CELL]
"""
Rule
  If the ALIGNMENT_STIM declares a fixed number of trials (onsets), the tracked
  file must contain exactly that many off→on transitions for the corresponding
  CSV column.

Inputs
  - EXPERIMENT["ALIGNMENT_STIM"] → label key in STIMULI
  - EXPERIMENT["STIMULI"][label]:
      • name           → CSV column name to read
      • trials         → expected onset count (int > 0), or 0/None for variable
      • detection      → (off,on) mapping used by BC_UTILS["onsets"]

Outcome
  - Pass when trials is 0/None (variable) OR observed_onsets == expected.
  - Fail otherwise with concise metrics.
"""

def _check_stim_count(df_tracked: pd.DataFrame) -> Tuple[bool, str]:
    label = EXPERIMENT["ALIGNMENT_STIM"]
    stim_info = EXPERIMENT["STIMULI"][label]
    expected = stim_info.get("trials", None)

    # Variable or unspecified trial count → pass
    if not expected or int(expected) <= 0:
        return True, ""

    column_name = stim_info["name"]
    if column_name not in df_tracked.columns:
        metrics = _format_metrics({
            "failure": "missing_column",
            "label": label,
            "name": column_name,
        })
        return False, metrics

    series = df_tracked[column_name]

    # Strict resolver uses the STIMULI registry; raises if misconfigured.
    onset_idxs = BC_UTILS["onsets"](series, column_name=column_name)
    observed = len(onset_idxs)

    if observed != int(expected):
        metrics = _format_metrics({
            "label": label,
            "name": column_name,
            "expected": int(expected),          # runner also accepts this alias
            "observed": observed,               # runner also accepts this alias
        })
        return False, metrics

    return True, ""


#%% CELL 05.3 — Error: wrong stimulus duration  [REPLACE THIS CELL]
"""
Rule
  If the ALIGNMENT_STIM declares a fixed pulse duration, every observed 'on'
  run must be within tolerance of that expected duration (in frames).

Inputs
  - EXPERIMENT["ALIGNMENT_STIM"] → label into STIMULI
  - STIMULI[label]:
      • name             → CSV column to read
      • duration_frames  → expected run length (int), or None for variable
  - EXPERIMENT["NOISE_TOLERANCE"] → tolerance in frames (int)

Outcome
  - Pass when duration is None (variable) OR all observed runs are within
    ±NOISE_TOLERANCE frames of expected.
  - Fail otherwise with concise metrics (min/max/mean observed).
"""

def _check_stim_duration(df_tracked: pd.DataFrame) -> Tuple[bool, str]:
    label = EXPERIMENT["ALIGNMENT_STIM"]
    stim_info = EXPERIMENT["STIMULI"][label]
    expected_frames = stim_info.get("duration_frames", None)

    # Variable or unspecified duration → pass
    if expected_frames is None:
        return True, ""

    column_name = stim_info["name"]
    if column_name not in df_tracked.columns:
        metrics = _format_metrics({
            "failure": "missing_column",
            "label": label,
            "name": column_name,
        })
        return False, metrics

    series = df_tracked[column_name]
    runs = BC_UTILS["pulse_durations"](series, column_name=column_name)

    # No runs observed is a count problem; let count checker handle it.
    if not runs:
        return True, ""

    tol = int(STIM_DURATION_JITTER_FRAMES)
    exp = int(expected_frames)

    # Check all runs are within [exp - tol, exp + tol]
    lo = exp - tol
    hi = exp + tol
    bad = [r for r in runs if not (lo <= int(r) <= hi)]

    if bad:
        import numpy as _np
        arr = _np.array(runs, dtype=int)
        metrics = _format_metrics({
            "label": label,
            "name": column_name,
            # IMPORTANT: rename for runner compatibility (Δ extraction)
            "expected_frames": exp,            # was "expected"
            "tolerance": tol,                  # accepted by runner
            "min_obs": int(arr.min()),         # runner accepts min_obs or min_obs_frames
            "max_obs": int(arr.max()),         # runner accepts max_obs or max_obs_frames
            "mean_obs": float(arr.mean()),
            "bad_count": int(len(bad)),
        })
        return False, metrics

    return True, ""




#%% CELL 05.4 — Error: timeline misaligned (anchor = first onset, fit-only)  [REPLACE THIS CELL]
"""
Rule (simple fit check, no tolerance, padding allowed)

1) Find the first observed onset of the ALIGNMENT_STIM → first_onset.
2) Compute experiment_start = first_onset - baseline_frames  (floored at 0).
3) Compute expected_end   = experiment_start + experiment_span.
4) Let observed_end = len(df_tracked).

Pass if:
  - first_onset >= baseline_frames      (enough headroom for Baseline), and
  - observed_end >= expected_end        (enough tail to fit Experiment).

Fail otherwise (fatal), with a concise metrics string.
"""

def _check_timeline_alignment(df_tracked: pd.DataFrame) -> Tuple[bool, str]:
    # Resolve alignment stim series (same column used elsewhere in QC)
    stim_label  = EXPERIMENT["ALIGNMENT_STIM"]
    stim_info   = EXPERIMENT["STIMULI"][stim_label]
    column_name = stim_info["name"]
    if column_name not in df_tracked.columns:
        return False, _format_metrics({"failure": "missing_column", "label": stim_label, "name": column_name})
    series = df_tracked[column_name]

    # First observed onset (strict: use configured detection)
    onset_idxs = BC_UTILS["onsets"](series, column_name=column_name)
    if not onset_idxs:
        return False, "no_onsets_detected"

    first_onset = int(onset_idxs[0])

    # Frame durations for Baseline/Experiment (provided by Config)
    periods = EXPERIMENT["EXPERIMENTAL_PERIODS"]
    try:
        baseline_frames = int(periods["Baseline"]["duration_frames"])
        experiment_span = int(periods["Experiment"]["duration_frames"])
    except Exception:
        return False, "period_durations_unavailable"

    # Expected bounds (allow padding before/after; only deficits matter)
    experiment_start = max(0, first_onset - baseline_frames)
    expected_end     = experiment_start + experiment_span
    observed_end     = int(len(df_tracked))

    # Headroom check
    if first_onset < baseline_frames:
        deficit = baseline_frames - first_onset
        metrics = _format_metrics({
            "failure":     "short_head",
            "baseline":    baseline_frames,
            "first_onset": first_onset,
            "deficit":     deficit,           # runner accepts 'deficit' or 'deficit_frames'
            "span":        experiment_span,
        })
        return False, metrics

    # Tail check
    if observed_end < expected_end:
        deficit = expected_end - observed_end
        metrics = _format_metrics({
            "failure":      "short_tail",
            "expected_end": expected_end,
            "observed_end": observed_end,
            "deficit":      deficit,          # runner accepts 'deficit' or 'deficit_frames'
        })
        return False, metrics

    return True, ""


#%% CELL 05.5 — Error: centroid NaN health  [REPLACE THIS CELL]
"""
Check that Position_X / Position_Y are sufficiently populated.

Rule
  Let nan_mask = isna(Position_X) OR isna(Position_Y).
  Let nan_fraction = mean(nan_mask).
  Fail if nan_fraction > CENTROID_NAN_MAX_FRAC (default 0.05 when unset).

Returns
  (ok: bool, metrics: str)
  metrics includes:
    - nan_fraction=<float>           # used for per-file % in the UI
    - max_run=<int>                  # longest contiguous NaN run (frames) [diagnostic]
    - nan_hotspot_start=<int>        # start frame of that run, -1 if none [diagnostic]
"""

def _check_centroid_nan(df_tracked: pd.DataFrame) -> Tuple[bool, str]:
    # Guard: columns must exist (schema checker 05.1 would normally catch this)
    if ("NormalizedCentroidX" not in df_tracked.columns) or ("NormalizedCentroidY" not in df_tracked.columns):
        return False, _format_metrics({"nan_fraction": 1.0, "max_run": 0, "nan_hotspot_start": -1})

    import numpy as _np
    x = df_tracked["NormalizedCentroidX"].to_numpy(dtype=float)
    y = df_tracked["NormalizedCentroidY"].to_numpy(dtype=float)
    nan_mask = _np.isnan(x) | _np.isnan(y)

    if nan_mask.size == 0:
        # empty file — treat as fully valid here; other checks deal with emptiness
        return True, _format_metrics({"nan_fraction": 0.0, "max_run": 0, "nan_hotspot_start": -1})

    frac = float(_np.mean(nan_mask))

    # Compute longest contiguous NaN run and its start (cheap pass)
    max_run = 0
    hotspot = -1
    curr = 0
    start = -1
    for i, v in enumerate(nan_mask):
        if v:
            if curr == 0:
                start = i
            curr += 1
            if curr > max_run:
                max_run = curr
                hotspot = start
        else:
            curr = 0

    max_allowed = float(CENTROID_NAN_MAX_FRAC)
    ok = (frac <= max_allowed)

    metrics = _format_metrics({
        "nan_fraction": frac,         # <- key your runner uses to compute % for this file
        "max_run": max_run,
        "nan_hotspot_start": hotspot,
    })
    return ok, metrics


#%% CELL 05.6 — Error: missing Sleap file  [REPLACE THIS CELL]
"""
Ensure the companion SLEAP pose file exists when POSE_SCORING is enabled.

Rule
  If EXPERIMENT['POSE_SCORING'] is truthy:
    - Resolve expected path via PATH['sleap_path'](file_stem).
    - Fail if it does not exist.

Returns
  (ok: bool, metrics: str)
  On failure, metrics include:
    - sleap_present=0
    - sleap_expected_path=<path>
    - pose_scoring=true
"""

def _check_sleap_presence(df_tracked: pd.DataFrame, file_stem: str) -> Tuple[bool, str]:
    want_pose = bool(EXPERIMENT.get("POSE_SCORING", True))
    if not want_pose:
        return True, "pose_scoring=false"

    sleap_path = PATH["sleap_path"](file_stem)
    if sleap_path.exists():
        return True, _format_metrics({"sleap_present": 1, "sleap_expected_path": str(sleap_path)})

    # Missing
    metrics = _format_metrics({
        "sleap_present": 0,
        "sleap_expected_path": str(sleap_path),
        "pose_scoring": True,
    })
    return False, metrics



#%% CELL 05.7 — Error: sleap/tracked length mismatch  [REPLACE THIS CELL]
"""
Verify tracked and pose (SLEAP) data have identical frame counts.

Preconditions
  - Presence is checked by 05.6; if the SLEAP file is missing, this check passes
    (to avoid double-reporting).

Rule
  Read pose CSV (SLEAP) directly with pandas after resolving the path.
  Compare len(df_tracked) vs len(df_pose). Fail if different.

Returns
  (ok: bool, metrics: str)
  On failure, metrics include keys recognized by the Δ extractor:
    - tracked_len=<int>
    - sleap_len=<int>
  (Optionally include ratio and a tiny trim suggestion for forensics.)
"""

def _check_sleap_length(df_tracked: pd.DataFrame, file_stem: str) -> Tuple[bool, str]:
    sleap_path = PATH["sleap_path"](file_stem)
    if not sleap_path.exists():
        # 05.6 will have emitted the presence error; avoid duplicating it here
        return True, "sleap_present=0"

    # Read the SLEAP CSV directly with pandas (avoid BC_UTILS['read_pose'] dependency)
    try:
        df_pose = pd.read_csv(sleap_path)
    except Exception as e:
        # Pose file exists but couldn't be read -> report read failure clearly
        return False, _format_metrics({
            "tracked_len": len(df_tracked),
            "sleap_len": -1,
            "reason": "pose_read_fail",
            "msg": str(e)[:120],
        })

    t_len = int(len(df_tracked))
    s_len = int(len(df_pose))

    if t_len == s_len:
        return True, ""

    # Mismatch → emit keys the Δ extractor understands
    suggest = "none"
    if abs(t_len - s_len) > 0:
        # Heuristic: if pose longer, suggest trimming left (common drift); if shorter, right.
        suggest = "left" if (s_len > t_len) else "right"

    metrics = _format_metrics({
        "tracked_len": t_len,         # key used for Δ±N
        "sleap_len": s_len,           # key used for Δ±N
        "ratio": round((s_len / t_len), 3) if t_len else 0.0,
        "trim_suggestion": suggest,   # diagnostic only
    })
    return False, metrics





#%% CELL 06 — POST-CLASS FLAGS (ORCHESTRATOR; NO I/O)  [REPLACE THIS CELL]
"""
Purpose
    Run non-fatal QC flags in registry order (dict insertion order from
    CHECKPOINT_FLAGS). Collect all triggered flags and return them.

Contract
    _run_flags(df_scored, file_stem) -> list[tuple[str, str]]
        Returns:
            [(code, metrics), ...]  # empty list means no flags
    Notes:
        - No persistence here. Writing flagged artifacts and appending to
          the report happens in the public API (flag_check).
        - Only wired checks are executed; others are skipped.

Metrics schema (stable keys)
  view_nan_exceeded:
    - missing columns → "present_cols=...; required_cols=View_X,View_Y"
    - too many NaNs  → "nan_fraction=<float>; max_run=<int>; nan_hotspot_start=<int>"

  behavior_nan_exceeded:
    - missing column → "col_missing=Behavior_Denoised; available_behavior_cols=Behavior[,Behavior_Denoised]"
    - too many NaNs  → "nan_fraction=<float>; max_run=<int>; nan_hotspot_start=<int>"

  no_exploration:
    - missing column → "col_missing=Behavior_Denoised; available_behavior_cols=Behavior[,Behavior_Denoised]"
    - low walk       → "walk_frac=<float>; walk_frames=<int>; baseline=<start>:<stop>[; nonwalk_top=Label1:count,Label2:count]"
"""

from typing import List, Tuple


# Explicit schemas (mirrors of _main.py lists)
_SCORED_COLS = [
    "FrameIndex", "VisualStim", "Stim0", "Stim1",
    "Position_X", "Position_Y", "Speed", "Motion",
    "Layer1", "Layer1_Denoised",
    "Layer2", "Layer2_Denoised",
    "Resistant", "Resistant_Denoised",
    "Behavior", "Behavior_Denoised",
]

_POSE_COLS = [
    "FrameIndex", "Orientation", "View", "View_X", "View_Y",
    "Head_X", "Head_Y", "Thorax_X", "Thorax_Y", "Abdomen_X", "Abdomen_Y",
    "LeftWing_X", "LeftWing_Y", "RightWing_X", "RightWing_Y",
]



def _run_flags(df_scored: pd.DataFrame, file_stem: str) -> List[Tuple[str, str]]:
    """Evaluate all flags in registry order and return (code, metrics) for each triggered flag."""
    triggered: List[Tuple[str, str]] = []

    for code in CHECKPOINT_FLAGS.keys():
        if code == "view_nan_exceeded":
            ok, metrics = _flag_view_nan(df_scored)
        elif code == "behavior_nan_exceeded":
            ok, metrics = _flag_behavior_nan(df_scored)
        elif code == "no_exploration":
            ok, metrics = _flag_no_exploration(df_scored)
        else:
            # Skip any flags not yet wired.
            continue

        if not ok:
            triggered.append((code, metrics))

    return triggered


# -------------------------
# Individual flags
# -------------------------

def _flag_view_nan(df_scored: pd.DataFrame,
                   x_col: str = "View_X",
                   y_col: str = "View_Y") -> Tuple[bool, str]:
    """
    Rule
      If POSE_SCORING is off → pass trivially.
      If either required column is missing → flag with 'present_cols' diagnostic.
      Else compute nan_fraction over frames: isna(View_X) OR isna(View_Y).
      Flag when nan_fraction > VIEW_NAN_MAX_FRAC.

    Metrics (see module docstring).
    """
    if not EXPERIMENT.get("POSE_SCORING", False):
        return True, "pose_scoring=false"

    have_x = x_col in df_scored.columns
    have_y = y_col in df_scored.columns
    if not (have_x and have_y):
        present = ",".join([c for c in (x_col, y_col) if c in df_scored.columns]) or "None"
        metrics = _format_metrics({
            "present_cols": present,
            "required_cols": f"{x_col},{y_col}",
        })
        return False, metrics

    import numpy as _np
    x = df_scored[x_col].to_numpy(dtype=float)
    y = df_scored[y_col].to_numpy(dtype=float)
    nan_mask = _np.isnan(x) | _np.isnan(y)
    frac = float(_np.mean(nan_mask)) if nan_mask.size else 0.0

    # longest contiguous NaN run and its start
    max_run = 0
    hotspot = -1
    curr = 0; start = -1
    for i, v in enumerate(nan_mask):
        if v:
            if curr == 0:
                start = i
            curr += 1
            if curr > max_run:
                max_run = curr
                hotspot = start
        else:
            curr = 0

    max_allowed = float(VIEW_NAN_MAX_FRAC)
    ok = (frac <= max_allowed)

    metrics = _format_metrics({
        "nan_fraction": frac,            # used for per-file % in the UI/CSV
        "max_run": max_run,
        "nan_hotspot_start": hotspot,
    })
    return ok, metrics


def _flag_behavior_nan(df_scored: pd.DataFrame,
                       col: str = "Behavior_Denoised") -> Tuple[bool, str]:
    """
    Rule
      If column missing → flag with 'col_missing' + 'available_behavior_cols'.
      Else nan_fraction over frames: isna(Behavior_Denoised).
      Flag when nan_fraction > BEHAVIOR_DENOISED_NAN_MAX_FRAC.

    Metrics (see module docstring).
    """
    if col not in df_scored.columns:
        available = ",".join([c for c in ("Behavior", "Behavior_Denoised") if c in df_scored.columns]) or "None"
        metrics = _format_metrics({
            "col_missing": col,
            "available_behavior_cols": available,
        })
        return False, metrics

    nan_mask = df_scored[col].isna().to_numpy()
    import numpy as _np
    frac = float(_np.mean(nan_mask)) if nan_mask.size else 0.0

    # longest contiguous NaN run and its start
    max_run = 0
    hotspot = -1
    curr = 0; start = -1
    for i, v in enumerate(nan_mask):
        if v:
            if curr == 0:
                start = i
            curr += 1
            if curr > max_run:
                max_run = curr
                hotspot = start
        else:
            curr = 0

    max_allowed = float(BEHAVIOR_DENOISED_NAN_MAX_FRAC)
    ok = (frac <= max_allowed)

    metrics = _format_metrics({
        "nan_fraction": frac,            # used for per-file % in the UI/CSV
        "max_run": max_run,
        "nan_hotspot_start": hotspot,
    })
    return ok, metrics


def _flag_no_exploration(df_scored: pd.DataFrame,
                         col: str = "Behavior_Denoised") -> Tuple[bool, str]:
    """
    Rule
      If Behavior_Denoised is missing → flag with 'col_missing'.
      Else compute walking fraction during the baseline window.
      Flag when walk_frac < BASELINE_MIN_WALK_FRAC.

    Baseline window
      - Find the first onset of the ALIGNMENT_STIM (strict on registry).
      - Baseline start = max(0, first_onset - Baseline.duration_frames)
      - Baseline stop  = first_onset

    Metrics (low-walk path)
      'walk_frac=<float>; walk_frames=<int>; baseline=<start>:<stop>[; nonwalk_top=Label1:count,Label2:count]'
    """
    # Branch A: missing classification column
    if col not in df_scored.columns:
        available = ",".join([c for c in ("Behavior", "Behavior_Denoised") if c in df_scored.columns]) or "None"
        metrics = _format_metrics({
            "col_missing": col,
            "available_behavior_cols": available,
        })
        return False, metrics

    # Locate first alignment onset (preflight guarantees stim exists in data)
    align_label = EXPERIMENT["ALIGNMENT_STIM"]
    stim_info   = EXPERIMENT["STIMULI"][align_label]
    column_name = stim_info["name"]
    if column_name not in df_scored.columns:
        return False, _format_metrics({"failure": "missing_column", "label": align_label, "name": column_name})

    series = df_scored[column_name]
    onset_idxs = BC_UTILS["onsets"](series, column_name=column_name)
    if not onset_idxs:
        # If somehow there are no onsets at this stage, treat as low-walk to be safe
        return False, _format_metrics({"walk_frac": 0.0, "walk_frames": 0, "baseline": "0:0"})

    first_onset = int(onset_idxs[0])

    # Derive exact baseline window (frames)
    baseline_frames = int(EXPERIMENT["EXPERIMENTAL_PERIODS"]["Baseline"]["duration_frames"])
    baseline_start  = max(0, first_onset - baseline_frames)
    baseline_stop   = first_onset

    df_base = df_scored[(df_scored["FrameIndex"] >= baseline_start) & (df_scored["FrameIndex"] < baseline_stop)]
    total = int(len(df_base))
    if total <= 0:
        # Empty baseline window → no flag (or conservative? keep as pass)
        return True, _format_metrics({"baseline": f"{baseline_start}:{baseline_stop}", "walk_frac": 0.0})

    walk_label = EXPERIMENT.get("WALK_LABEL", "Walk")
    walk_frames = int((df_base[col] == walk_label).sum())
    walk_frac = (walk_frames / total) if total else 0.0
    min_walk = float(BASELINE_MIN_WALK_FRAC)

    # Optional: most frequent non-walk labels (for quick forensics)
    nonwalk = df_base[col][df_base[col] != walk_label]
    top_counts = nonwalk.value_counts().head(2).to_dict()
    top_str = ",".join([f"{k}:{v}" for k, v in top_counts.items()])

    ok = (walk_frac >= min_walk)
    metrics = _format_metrics({
        "walk_frac": float(walk_frac),
        "walk_frames": walk_frames,
        "baseline": f"{baseline_start}:{baseline_stop}",
        **({"nonwalk_top": top_str} if top_str else {}),
    })
    return ok, metrics


# -------------------------
# Flagged artifact saver (unchanged behavior)
# -------------------------

def _save_flagged_artifact(df_combined: pd.DataFrame, file_stem: str, triggered: List[Tuple[str, str]]) -> None:
    """
    Save compact 'scored' and 'pose' CSV snapshots for inspection.
    - Uses explicit schema lists where available, dropping missing cols silently.
    - Atomic writes via BC_UTILS['write_csv_atomic'].
    """
    try:
        # --- Scored view ---
        if "_SCORED_COLS" in globals():
            scored_cols = [c for c in _SCORED_COLS if c in df_combined.columns]
        else:
            # Fallback: a reasonable minimal set
            scored_cols = [c for c in ("FrameIndex","Stim0","Stim1","Position_X","Position_Y","Speed","Behavior","Behavior_Denoised") if c in df_combined.columns]

        scored_view = df_combined[scored_cols].copy() if scored_cols else pd.DataFrame()
        scored_dest: Path = PATH["flag_scored_path"](file_stem)
        scored_dest.parent.mkdir(parents=True, exist_ok=True)
        BC_UTILS["write_csv_atomic"](scored_view, scored_dest, index=False)

        # --- Pose view (only when POSE_SCORING) ---
        if EXPERIMENT.get("POSE_SCORING"):
            if "_POSE_COLS" in globals():
                pose_cols = [c for c in _POSE_COLS if c in df_combined.columns]
            else:
                pose_cols = [c for c in ("View_X","View_Y") if c in df_combined.columns]

            pose_view = df_combined[pose_cols].copy() if pose_cols else pd.DataFrame()
            pose_dest: Path = PATH["flag_pose_path"](file_stem)
            pose_dest.parent.mkdir(parents=True, exist_ok=True)
            BC_UTILS["write_csv_atomic"](pose_view, pose_dest, index=False)

    except Exception:
        # best-effort only; never break the session on a save failure
        pass



#%% CELL 07 — Append to QC REPORTs (CSV, durable, append-only)  [REPLACE THIS CELL]
"""
CSV-only QC reports (no TXT).

Schema (fixed columns)
  kind, code, file_stem, unit, delta, metrics_observed, metrics_expected

Notes
  - 'kind' is 'error' or 'flag'
  - 'code' is the stable lower_snake token (registry key)
  - 'metrics_observed' is the compact 'k=v; k=v' blob returned by checkers
  - For now, we leave 'unit', 'delta', 'metrics_expected' empty to avoid ripples
  - Atomic writes via BC_UTILS['write_csv_atomic']
"""

from pathlib import Path
import pandas as pd

_REPORT_COLUMNS = [
    "kind",
    "code",
    "file_stem",
    "unit",
    "delta",
    "metrics_observed",
    "metrics_expected",
]

def _report_csv_append(report_path: Path, row: dict) -> None:
    report_path = Path(report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    # one-row DF with fixed schema
    payload = {k: row.get(k, "") for k in _REPORT_COLUMNS}
    df_new = pd.DataFrame([payload], columns=_REPORT_COLUMNS)

    if report_path.exists():
        try:
            df_old = pd.read_csv(report_path, dtype=str)
        except Exception:
            df_old = pd.DataFrame(columns=_REPORT_COLUMNS)
        df_out = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_out = df_new

    BC_UTILS["write_csv_atomic"](df_out, report_path, index=False)


def _append_error_report_csv(*,
                             file_stem: str,
                             code: str,
                             metrics_observed: str) -> None:
    _report_csv_append(
        report_path=Path(PATH["report_error_path"]()),
        row={
            "kind": "error",
            "code": code,
            "file_stem": file_stem,
            "unit": "",
            "delta": "",
            "metrics_observed": metrics_observed or "",
            "metrics_expected": "",
        },
    )


def _append_flag_report_csv(*,
                            file_stem: str,
                            code: str,
                            metrics_observed: str) -> None:
    _report_csv_append(
        report_path=Path(PATH["report_flag_path"]()),
        row={
            "kind": "flag",
            "code": code,
            "file_stem": file_stem,
            "unit": "",
            "delta": "",
            "metrics_observed": metrics_observed or "",
            "metrics_expected": "",
        },
    )



#%% CELL 07.1 — Error input copies (Tracked & Pose)  [REPLACE THIS CELL]
"""
On a fatal error, copy relevant inputs to the error folder for inspection.

- Always copies the 'tracked' CSV to the error bucket.
- If a SLEAP file exists, copy it as well.
- Best-effort: never raise on copy failures.
"""

def _copy_error_inputs(file_stem: str) -> None:
    try:
        tracked_src = PATH["tracked_path_from_stem"](file_stem)
        if tracked_src.exists():
            tracked_dst = PATH["error_tracked_copy_path"](tracked_src.name)
            tracked_dst.parent.mkdir(parents=True, exist_ok=True)
            BC_UTILS["copy_atomic"](tracked_src, tracked_dst)

        sleap_src = PATH["sleap_path"](file_stem)
        if sleap_src.exists():
            # Use the unified 'error_pose_copy_path' for pose copies (inputs)
            sleap_dst = PATH["error_pose_copy_path"](sleap_src.name)
            sleap_dst.parent.mkdir(parents=True, exist_ok=True)
            BC_UTILS["copy_atomic"](sleap_src, sleap_dst)
    except Exception:
        # best-effort; never break the session on copy issues
        pass



#%% CELL 08 — PUBLIC ENTRYPOINTS (error_check / flag_check / log_error)  [REPLACE THIS CELL]
"""
CSV-only QC API. No TXT writes.

Public surface
  BC_QC['error_check'](file_stem, df_tracked) -> bool
    - Runs pre-flight checks (Cell 05: _run_preflight).
    - On first failure, appends ONE 'error' CSV row and copies inputs.
    - Returns False on failure, True otherwise.

  BC_QC['flag_check'](file_stem, df_scored) -> (ok: bool, list[str])
    - Runs all flags (Cell 06: _run_flags).
    - Appends ONE 'flag' CSV row per triggered flag (no 'multiple' in CSV).
    - Saves flagged artifacts snapshot if any flags fired.
    - Returns:
        (True, [])                             when no flags
        (False, ['<single_code>'])             when exactly one flag
        (False, ['multiple'])                  when 2+ flags

  BC_QC['log_error'](file_stem, code, metrics="")
    - For early failures (before df_tracked exists).
    - Appends ONE 'error' CSV row and copies inputs.
"""

from typing import Tuple, List

def error_check(file_stem: str, df_tracked) -> bool:
    ok, code, metrics = _run_preflight(file_stem, df_tracked)
    if ok:
        return True

    # Append CSV row for the failing error. Do not copy inputs here; the
    # orchestrator is responsible for copying tracked/sleap files on error.
    _append_error_report_csv(
        file_stem=file_stem,
        code=code,
        metrics_observed=metrics or "",
    )
    return False


def flag_check(file_stem: str, df_combined) -> Tuple[bool, List[str]]:
    """
    Evaluate non-fatal flags and append report rows.

    The QC module only logs the occurrence of flags. Saving of flagged
    artifacts (scored/pose CSVs) is delegated to the orchestrator. The
    returned tuple communicates whether any flags were raised and a summary
    code. A summary of ['multiple'] indicates more than one flag fired.
    """
    triggered = _run_flags(df_combined, file_stem)

    # Append one CSV row per individual flag (no synthetic 'multiple' row)
    for code, metrics in triggered:
        _append_flag_report_csv(
            file_stem=file_stem,
            code=code,
            metrics_observed=metrics or "",
        )

    if not triggered:
        return True, []

    if len(triggered) == 1:
        return False, [triggered[0][0]]

    # 2+ flags
    return False, ["multiple"]


def log_error(file_stem: str, code: str, metrics: str = "") -> None:
    """
    Record an early error (before df_tracked exists) in the ERROR report.

    Only writes a report line. The orchestrator should handle copying any
    relevant input files (tracked and sleap) when a fatal error occurs.
    """
    _append_error_report_csv(
        file_stem=file_stem,
        code=code,
        metrics_observed=metrics or "",
    )


BC_QC = MappingProxyType({
    # Core QC entrypoints
    "is_file_already_classified": is_file_already_classified,
    "error_check": error_check,
    "flag_check": flag_check,
    "log_error": log_error,

    # Display registries (used by the runner to render labels)
    "error_labels": CHECKPOINT_ERRORS,
    "flag_labels":  CHECKPOINT_FLAGS,
})

__all__ = ("BC_QC",)




#%% CELL 09 — QC MODULE REPORT (print-only overview)
"""
Print a concise manifest of this QC module:
  - Errors (fatal, preflight) with messages and relevant thresholds
  - Flags  (non-fatal, post-class) with messages and relevant thresholds
  - Public API entrypoints exposed to callers
No file I/O. No dataset required.
"""

def _print_qc_module_report() -> None:
	# header
	print("=== QC MODULE REPORT ===\n")

	# ---- errors ----
	print("ERRORS (fatal, preflight)")
	for code, msg in CHECKPOINT_ERRORS.items():
		line = f"  {code:<24} — {msg}"
		# attach pertinent knobs inline where it helps triage
		if code == "wrong_stimulus_duration":
			line += f"   (jitter: ±{_format_number(STIM_DURATION_JITTER_FRAMES)} frames)"
		elif code == "centroid_nan_exceeded":
			line += f"   (threshold: CENTROID_NAN_MAX_FRAC = {_format_number(CENTROID_NAN_MAX_FRAC)})"
		print(line)
	print("")

	# ---- flags ----
	print("FLAGS (non-fatal, post-class)")
	for code, msg in CHECKPOINT_FLAGS.items():
		line = f"  {code:<24} — {msg}"
		if code == "no_exploration":
			line += f"\n    (threshold: BASELINE_MIN_WALK_FRAC = {_format_number(BASELINE_MIN_WALK_FRAC)})"
		elif code == "behavior_nan_exceeded":
			line += f"\n    (threshold: BEHAVIOR_DENOISED_NAN_MAX_FRAC = {_format_number(BEHAVIOR_DENOISED_NAN_MAX_FRAC)})"
		elif code == "view_nan_exceeded":
			line += f"\n    (threshold: VIEW_NAN_MAX_FRAC = {_format_number(VIEW_NAN_MAX_FRAC)})"
		print(line)
	print("")

	# ---- public surface ----
	print("PUBLIC SURFACE")
	print('  BC_QC["error_check"](file_stem, df_tracked) -> bool')
	print('  BC_QC["flag_check"](file_stem, df_scored)  -> (ok: bool, summary_codes: list[str])')

# Print automatically when running this module directly (e.g., Run in Spyder)
if __name__ == "__main__":
	_print_qc_module_report()

