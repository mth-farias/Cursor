#%% CELL 00 — MODULE OVERVIEW
'''
_utils.py

Overview
    Shared, policy-light mechanics used by BehaviorClassifier modules:
    _classifier, _qc_error_flag, and the future _main. Centralizes only
    generic helpers; policy (thresholds, tie-breaks, windows, filenames)
    stays in Config and in algorithm/QC modules. Style and sectioning match
    the project’s modules for consistency.

Fixed section order
    1) Binary stimulus            — detection mapping, onsets, pulse durations, cleaners
    2) Labels & runs              — prefix utilities and generic run-length iteration
    3) Motion                     — PixelChange → Motion (nullable Int)
    4) Geometry & kinematics      — norm↔mm, speed (mm/s), orientation (0°=North)
    5) Pose view selection        — choose (view_label, x, y) from confidences
    6) Alignment                  — crop_alignment arithmetic + slicing
    7) I/O primitive              — atomic CSV writer (tmp → fsync → replace)
    8) Public export              — read-only dict (BC_UTILS) of callables

Scope
    • Stateless helpers with minimal defaults pulled from Config (EXPERIMENT).
    • No windowing rules — stay in _classifier.
    • No stats like nan_fraction / fraction_equal — stay in _qc_error_flag.
    • No path/suffix builders — callers use Config.path directly.

Notes
    • Stimulus edge logic respects EXPERIMENT["STIMULI"][…]["detection"] (off,on).
    • NOISE_TOLERANCE now lives in experiment.py; defaults pulled from EXPERIMENT.
    • NumPy/Pandas–friendly surfaces; clarity over micro-optimisation.
    • Series in → Series out (index preserved) unless explicitly returning slices.
'''


#%% CELL 01 — IMPORTS
"""
Minimal, side-effect–free imports.
Order: stdlib → typing → third-party → package (Config for defaults only).
"""

# stdlib
from pathlib import Path
import sys
from types import MappingProxyType

# typing
from typing import Iterator, Sequence, Tuple, Optional, Dict

# third-party
import numpy as np
import pandas as pd

#%%% CELL 01.1 — PACKAGE IMPORTS (CONFIG SHIM)
"""
Ensure Codes/ is importable for absolute package imports in notebooks/Colab.
No effect when running as an installed package.
"""
ROOT = Path(__file__).resolve().parents[1]  # .../Codes
if str(ROOT) not in sys.path:
	sys.path.insert(0, str(ROOT))

from Config import EXPERIMENT  # read-only registries



#%% CELL 02 — BINARY STIMULUS (respect detection mapping)
"""
Purpose
    Helpers that operate on binary-like stimulus channels using the configured
    (off_value, on_value) detection mapping from Config.experiment.

Fixed subcells
    02.1 — detection-aware readers: resolve_stim_detection, onsets, pulse_durations
    02.2 — in-place cleaners:       fill_zeros, clean_ones

Notes
    • Defaults for tolerances are pulled from EXPERIMENT (NOISE_TOLERANCE).
    • Policy validation (stimulus schema, error reporting) remains in _qc_error_flag.
"""


#%%% CELL 02.1 — detection-aware readers  [REPLACE THIS CELL]
"""
Purpose
    Provide strict functions to resolve the (off, on) mapping for a stimulus channel
    and derive onset indices and pulse durations using that mapping.

Contract
    - CSV column names must exactly match the "name" field in Config.experiment.STIMULI.
    - Each STIMULI entry must include a valid detection=(off,on) tuple.
    - No inference from data, no fallback defaults, no acceptance of label keys.
    - If resolution fails, raise a descriptive ValueError.

Public surface
    - resolve_stim_detection(column_name: str) -> (off, on)
    - onsets(series, column_name=...) -> list[int]
    - pulse_durations(series, column_name=...) -> list[int]
"""

def resolve_stim_detection(*, column_name: str) -> Tuple:
    """
    Resolve (off,on) mapping for a stimulus channel by its CSV column name.

    Parameters
    ----------
    column_name : str
        Must exactly match the "name" field of one entry in EXPERIMENT["STIMULI"].

    Returns
    -------
    (off, on) : tuple

    Raises
    ------
    ValueError
        - if no STIMULI entry has .name == column_name
        - if a matching entry exists but lacks a valid detection tuple
    """
    stimuli = EXPERIMENT.get("STIMULI", {}) or {}
    for stim_label, info in stimuli.items():
        if info.get("name") == column_name:
            det = info.get("detection", None)
            if det is None or len(det) != 2:
                raise ValueError(
                    f"Stimulus column '{column_name}' (label '{stim_label}') "
                    f"is missing a valid detection=(off,on) in Config.experiment.STIMULI."
                )
            return tuple(det)

    valid = [info.get("name") for info in stimuli.values() if "name" in info]
    raise ValueError(
        f"Unknown stimulus column '{column_name}'. "
        f"Expected one of: {', '.join(valid) if valid else 'none configured'}."
    )


def onsets(series: pd.Series, *, column_name: str) -> list[int]:
    """
    Return indices where the signal transitions from 'off' to 'on'.

    Parameters
    ----------
    series : pandas.Series
        Stimulus channel values.
    column_name : str
        CSV column name (must be resolvable via Config.experiment.STIMULI).

    Returns
    -------
    List of rising edge indices.
    """
    off, on = resolve_stim_detection(column_name=column_name)
    vals = series.to_numpy()

    # treat NaN as not-on
    is_on = (vals == on)
    was_on = np.concatenate(([False], is_on[:-1]))
    was_off = np.concatenate(([True], ~is_on[:-1]))
    rising = np.where((~was_on) & is_on & was_off)[0]
    return rising.tolist()


def pulse_durations(series: pd.Series, *, column_name: str) -> list[int]:
    """
    Return lengths (in frames) of contiguous runs where the value equals 'on'.

    Parameters
    ----------
    series : pandas.Series
        Stimulus channel values.
    column_name : str
        CSV column name (must be resolvable via Config.experiment.STIMULI).

    Returns
    -------
    List of run lengths (frames) where the series is 'on'.
    """
    _, on = resolve_stim_detection(column_name=column_name)
    vals = series.to_numpy()

    durations = []
    n = len(vals)
    i = 0
    while i < n:
        if vals[i] == on:
            j = i + 1
            while j < n and vals[j] == on:
                j += 1
            durations.append(j - i)
            i = j
        else:
            i += 1
    return durations



#%%% CELL 02.2 — in-place cleaners
"""
Purpose
    Provide in-place run-length smoothing for binary stimulus channels.
    Used to fill bounded zero-holes and trim bounded one-spikes before
    onset/duration checks.

Steps
    - fill_zeros: fill strictly bounded 0-runs (≤ max_run_length).
    - clean_ones: remove strictly bounded 1-runs (≤ max_run_length).
    - Default max_run_length from EXPERIMENT["NOISE_TOLERANCE"].

Output
    - None (modifies DataFrame in place).
"""

def fill_zeros(
    df: pd.DataFrame,
    column: str,
    max_run_length: Optional[int] = None,
) -> None:
    """
    In-place hole-fill of strictly bounded zero-runs (length ≤ max_run_length).
    """
    # Setup
    if column not in df.columns:
        raise KeyError(f"Column not found: {column!r}")
    if max_run_length is None:
        max_run_length = int(EXPERIMENT["NOISE_TOLERANCE"])

    column_values = df[column].to_numpy(copy=False)
    zero_mask = (column_values == 0)
    one_mask = (column_values == 1)

    total_length = column_values.size
    if total_length == 0:
        return

    # Run-length encode zero mask
    zero_mask_int = zero_mask.astype(np.int8)
    zero_change_diff = np.diff(zero_mask_int)

    run_start_indices = np.flatnonzero(zero_change_diff == 1) + 1
    run_end_indices_exclusive = np.flatnonzero(zero_change_diff == -1) + 1

    # Handle boundaries
    if zero_mask[0]:
        run_start_indices = np.r_[0, run_start_indices]
    if zero_mask[-1]:
        run_end_indices_exclusive = np.r_[run_end_indices_exclusive, total_length]

    # Iterate runs
    for start_index, end_index in zip(run_start_indices, run_end_indices_exclusive):
        run_length = end_index - start_index
        left_neighbor_is_one = (start_index - 1) >= 0 and one_mask[start_index - 1]
        right_neighbor_is_one = end_index < total_length and one_mask[end_index]
        is_strictly_bounded = left_neighbor_is_one and right_neighbor_is_one

        if is_strictly_bounded and run_length <= max_run_length:
            column_values[start_index:end_index] = 1  # fill to 'on' value


def clean_ones(
    df: pd.DataFrame,
    column: str,
    max_run_length: Optional[int] = None,
) -> None:
    """
    In-place spike-trim of strictly bounded one-runs (length ≤ max_run_length).
    """
    # Setup
    if column not in df.columns:
        raise KeyError(f"Column not found: {column!r}")
    if max_run_length is None:
        max_run_length = int(EXPERIMENT["NOISE_TOLERANCE"])

    column_values = df[column].to_numpy(copy=False)
    one_mask = (column_values == 1)
    zero_mask = (column_values == 0)

    total_length = column_values.size
    if total_length == 0:
        return

    # Run-length encode one mask
    one_mask_int = one_mask.astype(np.int8)
    one_change_diff = np.diff(one_mask_int)

    run_start_indices = np.flatnonzero(one_change_diff == 1) + 1
    run_end_indices_exclusive = np.flatnonzero(one_change_diff == -1) + 1

    # Handle boundaries
    if one_mask[0]:
        run_start_indices = np.r_[0, run_start_indices]
    if one_mask[-1]:
        run_end_indices_exclusive = np.r_[run_end_indices_exclusive, total_length]

    # Iterate runs
    for start_index, end_index in zip(run_start_indices, run_end_indices_exclusive):
        run_length = end_index - start_index
        left_neighbor_is_zero = (start_index - 1) >= 0 and zero_mask[start_index - 1]
        right_neighbor_is_zero = end_index < total_length and zero_mask[end_index]
        is_strictly_bounded = left_neighbor_is_zero and right_neighbor_is_zero

        if is_strictly_bounded and run_length <= max_run_length:
            column_values[start_index:end_index] = 0  # trim to 'off' value



#%% CELL 03 — LABELS & RUNS (mechanics only)
"""
Purpose
    Provide generic string and sequence helpers for working with prefixed labels
    and contiguous runs of values. Used across classifier layers and resistant logic.

Steps
    - ensure_prefixed: build "Prefix_Base" string labels.
    - strip_prefix: remove known prefix from a label (pass through NaNs/others).
    - iter_label_runs: run-length encode a sequence into contiguous segments.

Output
    - String with prefix applied.
    - String with prefix removed (or unchanged input).
    - Iterator of (start_index, end_index_exclusive, value) tuples.
"""

def ensure_prefixed(prefix: str, base_label: str) -> str:
    """
    Return f"{prefix}{base_label}" without validation.
    Example: ensure_prefixed("Layer2_", "Walk") → "Layer2_Walk".
    """
    return f"{prefix}{base_label}"


def strip_prefix(prefix: str, label: str | float | None) -> str | float | None:
    """
    Remove 'prefix' from a string label when present.
    Non-strings and NaN-like tokens are passed through unchanged.
    Example: strip_prefix("Layer2_", "Layer2_Walk") → "Walk".
    """
    if not isinstance(label, str):
        return label
    if label.startswith(prefix):
        return label[len(prefix):]
    return label


def iter_label_runs(labels: Sequence[object]) -> Iterator[tuple[int, int, object]]:
    """
    Yield (start_index, end_index_exclusive, value) for each contiguous run of labels.

    Behavior
      - Works with strings, numbers, and other hashable objects.
      - NaNs are treated as distinct values and segmented like any other.
      - Returns an iterator of tuples.
    """
    if len(labels) == 0:
        return iter([])

    start_index = 0
    current_value = labels[0]

    for index in range(1, len(labels)):
        if labels[index] != current_value:
            yield (start_index, index, current_value)
            start_index = index
            current_value = labels[index]

    # Final run
    yield (start_index, len(labels), current_value)


#%% CELL 04 — MOTION
"""
Purpose
    Derive a binary Motion signal from PixelChange for downstream Layer-1 logic.

Steps
    - motion_from_pixel_change: map PixelChange > 0 → 1, == 0 → 0, NaN → <NA> (nullable Int64).

Output
    - pandas Series with dtype 'Int64' (nullable), index preserved from the input.
"""

def motion_from_pixel_change(pixel_change: pd.Series) -> pd.Series:
    """
    Convert PixelChange to a binary Motion Series with pandas' nullable Int64 dtype.

    Mapping
      • > 0  → 1
      • == 0 → 0
      • NaN  → <NA>

    Returns
      pandas.Series[Int64], index preserved from 'pixel_change'.
    """
    # Setup
    motion_series = pd.Series(index=pixel_change.index, dtype="Int64")

    # Positive changes become motion = 1
    positive_mask = pixel_change > 0
    motion_series.loc[positive_mask] = 1

    # Exact zeros become motion = 0
    zero_mask = pixel_change == 0
    motion_series.loc[zero_mask] = 0

    # Missing values remain <NA> (no assignment needed for NaNs)

    return motion_series


#%% CELL 05 — GEOMETRY & KINEMATICS
"""
Purpose
    Vectorized spatial helpers using arena geometry and experiment timebase.

Steps
    - norm_to_mm_x: normalized X → mm (width from EXPERIMENT if omitted).
    - norm_to_mm_y: normalized Y → mm with Y-flip (height from EXPERIMENT).
    - compute_speed_mm_per_s: Euclidean speed in mm/s (frame_span_sec from EXPERIMENT).
    - compute_orientation: bearing A→B in degrees (0°=North, [0,360)).

Output
    - Return type mirrors input: Series keeps index, ndarray returns ndarray.
"""

def norm_to_mm_x(x_norm: pd.Series | np.ndarray, width_mm: Optional[float] = None):
    """
    Convert normalized X (0–1) to millimetres.

    Defaults
      - width_mm = EXPERIMENT["ARENA_WIDTH_MM"]

    Returns
      - pandas Series with index preserved when input is Series
      - numpy.ndarray when input is ndarray
    """
    # Setup
    if width_mm is None:
        width_mm = EXPERIMENT["ARENA_WIDTH_MM"]

    # Conversion
    values_mm = np.asarray(x_norm) * width_mm

    # Preserve type
    if isinstance(x_norm, pd.Series):
        return pd.Series(values_mm, index=x_norm.index, name=x_norm.name)
    return values_mm


def norm_to_mm_y(y_norm: pd.Series | np.ndarray, height_mm: Optional[float] = None):
    """
    Convert normalized Y (0–1) to millimetres with Y-flip (top-positive).

    Defaults
      - height_mm = EXPERIMENT["ARENA_HEIGHT_MM"]

    Returns
      - pandas Series with index preserved when input is Series
      - numpy.ndarray when input is ndarray
    """
    # Setup
    if height_mm is None:
        height_mm = EXPERIMENT["ARENA_HEIGHT_MM"]

    # Conversion with Y-flip
    values_mm = (1.0 - np.asarray(y_norm)) * height_mm

    # Preserve type
    if isinstance(y_norm, pd.Series):
        return pd.Series(values_mm, index=y_norm.index, name=y_norm.name)
    return values_mm


def compute_speed_mm_per_s(
    x_mm: pd.Series | np.ndarray,
    y_mm: pd.Series | np.ndarray,
    frame_span_sec: Optional[float] = None,
):
    """
    Euclidean speed between consecutive frames in mm/s.

    Defaults
      - frame_span_sec = EXPERIMENT["SEC_PER_FRAME"]

    Returns
      - pandas Series with index preserved when inputs are Series
      - numpy.ndarray when inputs are ndarrays
    """
    if frame_span_sec is None:
        frame_span_sec = float(EXPERIMENT["SEC_PER_FRAME"])

    dx = np.diff(np.asarray(x_mm), prepend=np.nan)
    dy = np.diff(np.asarray(y_mm), prepend=np.nan)

    speed_mm_per_s = np.sqrt(dx**2 + dy**2) / frame_span_sec

    if isinstance(x_mm, pd.Series):
        return pd.Series(speed_mm_per_s, index=x_mm.index, name="Speed")
    return speed_mm_per_s


def compute_orientation(
    ax: pd.Series | np.ndarray,
    ay: pd.Series | np.ndarray,
    bx: pd.Series | np.ndarray,
    by: pd.Series | np.ndarray,
):
    """
    Bearing from A→B in degrees; 0°=North (positive Y), increasing clockwise, wrapped to [0,360).

    Returns
      - pandas Series with index preserved when inputs are Series
      - numpy.ndarray when inputs are ndarrays
    """
    # Delta vectors
    dx = np.asarray(bx) - np.asarray(ax)
    dy = np.asarray(by) - np.asarray(ay)

    # atan2 gives radians, convert to degrees
    radians = np.arctan2(dx, dy)  # note order: dx first to rotate 90°
    degrees = np.degrees(radians)

    # Wrap to [0,360)
    orientation_deg = np.mod(degrees, 360.0)

    # Preserve type
    if isinstance(ax, pd.Series):
        return pd.Series(orientation_deg, index=ax.index, name="Orientation_deg")
    return orientation_deg



#%% CELL 06 — POSE VIEW SELECTION
"""
Purpose
    Select a single (view_label, x, y) per frame from available pose confidences.

Steps
    - Legacy gate: if Head, Thorax, Abdomen are all present (by X availability),
      choose among Left/Right/Top/Bottom by maximum confidence (missing conf = 0.0).
      Normalize 'Bottom' → 'Top'. Return chosen (label, x, y) if coords exist.
    - Else fallback: return ('Vertical', Head_X, Head_Y) if Head exists; otherwise
      ('Vertical', Abdomen_X, Abdomen_Y) if Abdomen exists.
    - If nothing usable, return (np.nan, np.nan, np.nan).

Output
    - Tuple[object, float, float]: (view_label, x, y) using normalized view names.
"""

def determine_view(row: pd.Series) -> tuple[object, float, float]:
    """
    Legacy-compatible view selection using dot-style pose columns.

    Candidate views (for the HTA-present branch)
      - 'Left', 'Right', 'Top', 'Bottom'
      - Coordinates: '<View>.Position.X', '<View>.Position.Y'
      - Confidence:  '<View>.Confidence' (missing treated as 0.0)

    Fallback (Vertical)
      - Prefer Head coords; else Abdomen coords.

    Returns
      (view_label, x, y) with:
        • 'Bottom' normalized to 'Top' in the label
        • (np.nan, np.nan, np.nan) when nothing usable is present
    """
    # Setup: presence of Head/Thorax/Abdomen determined by X coord availability
    head_x = row.get("Head.Position.X", np.nan)
    thorax_x = row.get("Thorax.Position.X", np.nan)
    abdomen_x = row.get("Abdomen.Position.X", np.nan)

    head_present = pd.notna(head_x)
    thorax_present = pd.notna(thorax_x)
    abdomen_present = pd.notna(abdomen_x)

    # HTA present → choose the best of Left/Right/Top/Bottom by confidence
    if head_present and thorax_present and abdomen_present:
        candidate_views = ("Left", "Right", "Top", "Bottom")

        best_label: object = np.nan
        best_x: float = np.nan
        best_y: float = np.nan
        best_confidence = -np.inf

        # Evaluate candidates by max confidence (missing conf treated as 0.0)
        for view_label in candidate_views:
            x_key = f"{view_label}.Position.X"
            y_key = f"{view_label}.Position.Y"
            conf_key = f"{view_label}.Confidence"

            x_value = row.get(x_key, np.nan)
            y_value = row.get(y_key, np.nan)
            confidence_value = row.get(conf_key, 0.0)

            # Skip if coordinates are missing
            if pd.isna(x_value) or pd.isna(y_value):
                continue

            numeric_confidence = float(confidence_value) if pd.notna(confidence_value) else 0.0
            if numeric_confidence > best_confidence:
                best_confidence = numeric_confidence
                # Normalize 'Bottom' → 'Top' to fit downstream schema
                best_label = "Top" if view_label == "Bottom" else view_label
                best_x = float(x_value)
                best_y = float(y_value)

        # If a valid candidate was found, return it
        if pd.notna(best_label):
            return best_label, best_x, best_y

        # If chosen view lacked coords, fall through to Vertical fallback

    # Vertical fallback: prefer Head, else Abdomen
    head_y = row.get("Head.Position.Y", np.nan)
    if head_present and pd.notna(head_y):
        return "Vertical", float(head_x), float(head_y)

    abdomen_y = row.get("Abdomen.Position.Y", np.nan)
    if abdomen_present and pd.notna(abdomen_y):
        return "Vertical", float(abdomen_x), float(abdomen_y)

    # Nothing usable found
    return (np.nan, np.nan, np.nan)


#%% CELL 07 — ALIGNMENT
"""
Purpose
    Crop a DataFrame to the experiment-aligned window around the first stimulus onset,
    and provide a safe, deterministic tail-trim aligner for tracked vs sleap lengths.

Subsections
    - crop_alignment:     deterministic experiment window crop (view, not copy).
    - align_tracked_sleap_lengths: tail-only aligner using FrameIndex overlap.

Notes
    • align_tracked_sleap_lengths never trims heads and never writes to disk.
      It returns adjusted copies and an info dict. Callers decide if/what to persist.
    • Any mismatch inside the overlap (heads differ, mid-stream gaps, duplicates) raises.
"""


def crop_alignment(
    df: pd.DataFrame,
    baseline_frames: Optional[int] = None,
    total_frames: Optional[int] = None,
) -> pd.DataFrame:
    """
    Crop DataFrame rows to an experiment-aligned window.

    Args
      df: DataFrame containing the alignment stimulus column.
      baseline_frames: override for baseline duration in frames.
      total_frames: override for total window length in frames.

    Returns
      Cropped DataFrame (view). Empty DataFrame when no onset found.
    """
    # Resolve defaults from EXPERIMENT
    if baseline_frames is None:
        baseline_frames = EXPERIMENT["BASELINE_FRAMES"]
    if total_frames is None:
        total_frames = EXPERIMENT["TOTAL_FRAMES"]

    # Resolve alignment stim metadata
    align_stim_label = EXPERIMENT["ALIGNMENT_STIM"]
    stim_info = EXPERIMENT["STIMULI"][align_stim_label]
    stim_column = stim_info["name"]

    # Find first onset index
    detection_pair = stim_info["detection"]
    onset_indices = onsets(df[stim_column], detection=detection_pair)
    if len(onset_indices) == 0:
        return df.iloc[0:0]  # empty DataFrame view

    first_stim_idx = onset_indices[0]

    # Compute crop indices
    start_idx = first_stim_idx - baseline_frames
    end_idx_exclusive = start_idx + total_frames

    # Clamp to valid bounds to avoid negative-index wraparound
    n_rows = len(df)
    start_idx_clamped = max(0, min(start_idx, n_rows))
    end_idx_clamped = max(0, min(end_idx_exclusive, n_rows))

    # Return cropped DataFrame
    return df.iloc[start_idx_clamped:end_idx_clamped]


def align_tracked_sleap_lengths(
    tracked_df: pd.DataFrame,
    sleap_df: pd.DataFrame,
    *,
    key: str = "FrameIndex",
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, int | str]]:
    """
    Tail-only length alignment using the authoritative FrameIndex sequence.

    Policy
      • Never trim heads. Only trim the longer tail down to the shorter length.
      • If overlap keys differ at any position → raise ValueError("overlap_mismatch").
      • If key is missing or non-monotonic/duplicated → raise ValueError with reason.

    Returns
      (tracked_aligned, sleap_aligned, info)
      where info includes:
        - action: "no_action" | "tail_trim"
        - trimmed_tracked: int
        - trimmed_sleap: int
        - k_overlap: int

    This function performs no I/O and is silent.
    """
    # Basic presence
    if key not in tracked_df.columns:
        raise ValueError(f"missing_key_in_tracked:{key}")
    if key not in sleap_df.columns:
        raise ValueError(f"missing_key_in_sleap:{key}")

    # Extract sequences (as numpy for speed)
    t_keys = tracked_df[key].to_numpy()
    s_keys = sleap_df[key].to_numpy()

    n_t = t_keys.size
    n_s = s_keys.size
    k = min(n_t, n_s)

    # Guard: empty overlap is a mismatch (can't prove alignment)
    if k == 0:
        raise ValueError("empty_overlap")

    # Monotonicity & uniqueness checks in the overlap (strong guardrails)
    # We only need to validate up to k since we won't keep beyond that for the longer file.
    t_overlap = t_keys[:k]
    s_overlap = s_keys[:k]

    # Non-decreasing and no duplicates (strictly increasing recommended for frame indices)
    # If you allow equal repeats, adjust these checks accordingly.
    if (np.diff(t_overlap) <= 0).any():
        raise ValueError("non_monotonic_tracked_overlap")
    if (np.diff(s_overlap) <= 0).any():
        raise ValueError("non_monotonic_sleap_overlap")

    # Exact key equality over the overlap is required
    if not np.array_equal(t_overlap, s_overlap):
        raise ValueError("overlap_mismatch")

    # If equal lengths → no-op
    if n_t == n_s:
        info = {"action": "no_action", "trimmed_tracked": 0, "trimmed_sleap": 0, "k_overlap": int(k)}
        return tracked_df, sleap_df, info

    # Tail trim the longer one
    trim_tracked = 0
    trim_sleap = 0
    if n_t > k:
        trim_tracked = int(n_t - k)
        tracked_df = tracked_df.iloc[:k].reset_index(drop=True)
    if n_s > k:
        trim_sleap = int(n_s - k)
        sleap_df = sleap_df.iloc[:k].reset_index(drop=True)

    info = {
        "action": "tail_trim",
        "trimmed_tracked": trim_tracked,
        "trimmed_sleap": trim_sleap,
        "k_overlap": int(k),
    }
    return tracked_df, sleap_df, info



#%% CELL 08 — I/O PRIMITIVE (atomic write)
"""
Purpose
    Provide a single safe CSV writer used by QC and the orchestrator to prevent
    partial files. Writes to a sibling temp file, fsyncs, then atomically replaces
    the destination. Ensures the destination folder exists (mkdir -p).

Steps
    - Ensure parent directory exists (mkdir -p).
    - Create a temp file in the same folder as the destination.
    - df.to_csv(temp, **kwargs), then flush and os.fsync.
    - Atomically replace temp → final_path.
    - Best-effort fsync on the parent directory (POSIX).
    - Clean up temp on exceptions.

Output
    - None (writes file atomically).

Contract
    - Caller derives 'final_path' via Config.path policy.
    - This function performs no path *logic* beyond ensuring the parent dir exists.
"""

from pathlib import Path
import pandas as pd

def write_csv_atomic(df: pd.DataFrame, final_path: Path, **to_csv_kwargs) -> None:
    """
    Atomically write a CSV to 'final_path', ensuring the parent directory exists.

    Args
      df: pandas DataFrame to serialize.
      final_path: destination Path (parent directory will be created if missing).
      **to_csv_kwargs: forwarded to DataFrame.to_csv.

    Raises
      OSError / IOError on filesystem errors; temp file is removed when possible.
    """
    # Local imports (keep module import-time lean)
    import os
    import tempfile

    parent_dir = final_path.parent
    # Ensure destination folder exists (policy-light mkdir -p)
    parent_dir.mkdir(parents=True, exist_ok=True)

    temp_path: Path | None = None

    try:
        # Create a sibling temp file in the destination directory
        with tempfile.NamedTemporaryFile(
            mode="w",
            prefix=final_path.stem + ".tmp-",
            suffix=".csv",
            dir=str(parent_dir),
            delete=False,
            encoding=to_csv_kwargs.get("encoding", "utf-8"),
            newline=""
        ) as tmp:
            temp_path = Path(tmp.name)

            # Serialize DataFrame
            df.to_csv(tmp, **to_csv_kwargs)

            # Flush Python and OS buffers for the temp file
            tmp.flush()
            os.fsync(tmp.fileno())

        # Atomic replace of the temp file into place
        os.replace(str(temp_path), str(final_path))

        # Best-effort: fsync the directory entry on POSIX for durability
        try:
            if hasattr(os, "O_DIRECTORY"):
                dir_fd = os.open(str(parent_dir), os.O_DIRECTORY)
                try:
                    os.fsync(dir_fd)
                finally:
                    os.close(dir_fd)
        except Exception:
            # Non-fatal; durability best-effort only
            pass

    except Exception:
        # Best-effort cleanup of temp file if something failed
        try:
            if temp_path is not None and temp_path.exists():
                temp_path.unlink(missing_ok=True)  # Python ≥3.8
        finally:
            raise


#%% CELL 09 — PUBLIC EXPORT (read-only mapping)
"""
Purpose
    Expose a single, stable import surface as a read-only mapping of callables.

Steps
    - Build a dict with keys matching function names from the fixed sections.
    - Wrap with MappingProxyType to prevent runtime mutation.
    - Encourage importing as:
          from BehaviorClassifier._utils import BC_UTILS as U

Output
    - MappingProxyType: BC_UTILS
"""

BC_UTILS = MappingProxyType({
    # Binary stimulus
    "resolve_stim_detection": resolve_stim_detection,
    "onsets": onsets,
    "pulse_durations": pulse_durations,
    "fill_zeros": fill_zeros,
    "clean_ones": clean_ones,

    # Labels & runs
    "ensure_prefixed": ensure_prefixed,
    "strip_prefix": strip_prefix,
    "iter_label_runs": iter_label_runs,

    # Motion
    "motion_from_pixel_change": motion_from_pixel_change,

    # Geometry & kinematics
    "norm_to_mm_x": norm_to_mm_x,
    "norm_to_mm_y": norm_to_mm_y,
    "compute_speed_mm_per_s": compute_speed_mm_per_s,
    "compute_orientation": compute_orientation,

    # Pose view selection
    "determine_view": determine_view,

    # Alignment
    "crop_alignment": crop_alignment,
    "align_tracked_sleap_lengths": align_tracked_sleap_lengths,

    # I/O primitive
    "write_csv_atomic": write_csv_atomic,
    # File copy utility (atomic): copy a file from src to dst
    # Creates parent directories if needed and overwrites existing file.
    "copy_atomic": None,  # placeholder to be replaced below
})

#%% CELL 09.1 — Additional utility: copy_atomic
"""
Purpose
    Provide a simple atomic file copy operation for arbitrary files. This helper
    mirrors the behaviour of write_csv_atomic for DataFrames but for any
    filesystem entry. It ensures that the destination directory exists, copies
    the contents of the source file to a temporary file in the destination
    directory, fsyncs intermediate buffers, and atomically moves the temp
    file into place. If any error occurs during copying, no partial file will
    remain at the destination.

Implementation Notes
    - The copy is performed using Python's built-in I/O primitives rather than
      shutil.copy2 to retain control over fsync semantics.
    - Parent directories are created if they do not exist (mkdir -p).
    - The original file permissions and metadata are not preserved; only
      contents are copied. If metadata preservation becomes important,
      shutil.copystat could be incorporated in the future.

Parameters
    src: Path or str
        The source file on disk to be copied. Must exist.
    dst: Path or str
        The destination path, including filename, where the file will be
        copied. Any existing file at this location will be replaced atomically.

Raises
    Any exception encountered during I/O will be propagated after cleaning up
    any temporary files.
"""
from contextlib import contextmanager
import shutil
import os as _os

def copy_atomic(src: Path | str, dst: Path | str) -> None:
    src_path = Path(src)
    dst_path = Path(dst)

    # Ensure source exists
    if not src_path.exists():
        raise FileNotFoundError(f"Source file does not exist: {src_path}")

    # Ensure destination directory exists
    parent = dst_path.parent
    parent.mkdir(parents=True, exist_ok=True)

    temp_path: Path | None = None
    try:
        # Read source contents in binary mode
        with open(src_path, "rb") as fsrc:
            # Create a temporary file alongside the destination
            with open(
                parent / (dst_path.stem + ".tmp-" + src_path.name),
                "wb",
            ) as fdst:
                temp_path = Path(fdst.name)
                shutil.copyfileobj(fsrc, fdst)
                # Flush Python and OS buffers
                fdst.flush()
                _os.fsync(fdst.fileno())

        # Atomically replace destination with temp file
        _os.replace(temp_path, dst_path)

        # fsync the directory entry for durability
        try:
            if hasattr(_os, "O_DIRECTORY"):
                dir_fd = _os.open(str(parent), _os.O_DIRECTORY)
                try:
                    _os.fsync(dir_fd)
                finally:
                    _os.close(dir_fd)
        except Exception:
            # Non-fatal; best effort only
            pass
    except Exception:
        # Clean up temp on failure
        try:
            if temp_path is not None and temp_path.exists():
                temp_path.unlink(missing_ok=True)
        finally:
            raise

# Replace placeholder mapping entry with actual function
BC_UTILS = MappingProxyType({**BC_UTILS, "copy_atomic": copy_atomic})

