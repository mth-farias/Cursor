#%% CELL 00 — MODULE OVERVIEW
"""
Centralize behavior classification (algorithms only). Semantics and function
names are preserved from _functions.py. Provides a single import surface with
no I/O or side effects.

Scope
- Pure, deterministic kernels (NumPy-first).
- Strict label vocabulary with explicit prefixes (no inference).
- Seconds→frames performed via EXPERIMENT['seconds_to_frames'] at call-time.

Out of scope
- File I/O, CSV writes, or path logic.
- Feature construction (speed/orientation/view).
- Error/flag decisions and progress display.
"""


#%% CELL 01 — IMPORTS
"""
Minimal dependencies for classification kernels and helpers.
Stdlib → typing → third-party. Optional JIT is guarded.
"""
# typing
from typing import Sequence
from types import MappingProxyType

# third-party
import numpy as np
import pandas as pd


#%%% CELL 01.1 — PACKAGE IMPORTS (CONFIG SHIM)
"""
Always ensure Codes/ is on sys.path so absolute imports resolve.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]  # .../Codes
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Config import EXPERIMENT  # authoritative timebase bundle
from BehaviorClassifier import BC_UTILS  # shared mechanics (onsets, labels, etc.)


#%%% CELL 01.2 — OPTIONAL JIT
"""
Provide a no-op decorator when numba is unavailable. No logs, no side effects.
"""
try:  # pragma: no cover
    from numba import njit as _jit  # type: ignore
except Exception:  # pragma: no cover
    def _jit(*_a, **_k):
        def wrap(f): return f
        return wrap


#%% CELL 02 — KNOBS AND CONSTANTS (USER INPUT)
"""
Classification rules and vocabulary. These are the knobs a user can adjust.
Values are expressed in seconds or mm/s where applicable. Frame counts are
derived later via EXPERIMENT['seconds_to_frames'].
"""

#%%% CELL 02.1 — Classification rules
"""
Thresholds, smoothing windows, denoise rules, resistant coverage, and noisy
label policy. Adjust these to change how behaviors are classified.
"""

# NOISE TOLERANCE
NOISE_TOLERANCE = int(EXPERIMENT["NOISE_TOLERANCE"])
# Master tolerance (frames).


# BEHAVIOR THRESHOLDS
HIGH_SPEED = 75
# Jump detection threshold [mm/s]. Speed ≥ HIGH_SPEED → Jump.

LOW_SPEED = 4
# Walk vs. Stationary threshold [mm/s].
# LOW_SPEED ≤ Speed < HIGH_SPEED → Walk.
# Speed < LOW_SPEED → Stationary.


# LAYER1 DENOISE
LAYER1_DENOISE_MICROBOUT_MAX_FRAMES = NOISE_TOLERANCE
# Maximum bout length (frames) of Walk/Stationary/Freeze to delete.
# Jump bouts are never deleted.


# LAYER2 PARAMETERS
LAYER2_AVG_WINDOW_SEC = 0.1
# Centered averaging window (seconds) for Layer2 and Layer2_Denoised.
# Effective frame length = window_size_in_frames + 1 (odd).

LAYER2_DENOISE_MIN_VALID_FRACTION = 0.5
# Minimum fraction of valid (non-NaN) frames required inside the Layer2_Denoise window.
# Strictly > 0.5 valid → label; else → NaN.

TIEBREAK_LAYER2 = ("Walk", "Stationary", "Freeze")
# Tie resolution order for Layer2 and Layer2_Denoised.
# Applied when multiple non-Jump classes have equal counts.


# RESISTANT PARAMETERS
RESISTANT_STIM_COLUMNS = ("VisualStim", "Stim0", "Stim1")
# Stimulus binary columns used to build resistant coverage windows.
# Windows from different channels that touch or overlap are merged.

STARTLE_PRE_STIM_SEC  = 1.0
# Seconds before a stimulus onset that must be covered by a resistant bout.

STARTLE_POST_STIM_SEC = 1.0
# Seconds after a stimulus onset that must be covered by a resistant bout.


# BEHAVIOR DENOISED PARAMETERS
MAX_NAN_BOUT_CLEAN_SEC = 1.0
# Max NaN-bout length (in seconds) eligible for filling in Behavior_Denoised.
# If set to a number (e.g., 1), we will consider replacing *internal* NaN runs
# of length ≤ that many seconds, *only when* they are strictly bounded by the same
# valid Behavior label on both sides and all other guards pass.
# If set to None, this NaN-bout cleanup is completely disabled.

MIN_BOUND_BOUT_SEC = None
# Optional guard on flank quality. When numeric, both the left and right bouts
# that bound the NaN run must be at least this long (in seconds, converted to
# frames). Set to None to disable this test entirely.

SKIP_RESPONSE_WINDOW = True
# When True, NaN runs that intersect the post-stimulus *response window*
# are never filled. The response window is the union, across all channels in
# RESISTANT_STIM_COLUMNS, of per-onset intervals [onset, onset + STARTLE_POST_STIM_SEC].
# This avoids gluing across stimulus-locked dynamics in Behavior_Denoised.

# SPEED DENOISE PARAMETERS
#
# These knobs control the smoothing of the raw Speed signal to produce a
# refined 'Speed_Denoised' track used for Layer1_Denoised classification.
#
# SPEED_DENOISE_AVG_WINDOW_SEC defines the half-width of the centered window in
# seconds (effective window length = seconds_to_frames(SPEED_DENOISE_AVG_WINDOW_SEC) + 1,
# which enforces an odd number of frames). A value of 0.5 seconds results
# in smoother trajectories over approximately half a second on either side of
# each frame.
#
# SPEED_DENOISE_SKIP_RESPONSE_WINDOW mirrors the behavior of SKIP_RESPONSE_WINDOW in the
# Behavior denoiser: when True, frames that lie inside the post-stimulus
# response window (onset to onset + STARTLE_POST_STIM_SEC) are treated as
# guards. Any smoothing window containing one of these frames preserves the
# centre's raw speed, and the guarded frames themselves are never averaged.
# This helps avoid suppressing rapid behavioral responses immediately following
# stimuli.

SPEED_DENOISE_AVG_WINDOW_SEC = 0.5
SPEED_DENOISE_SKIP_RESPONSE_WINDOW = True


# NOISY LABEL POLICY
NOISY_LABEL = None
# Replacement label applied at export time for noisy/unassigned frames.
# Set to None to keep NaNs in the scored file.



#%%% CELL 02.2 — Vocabulary and prefixes
"""
Base behaviors, resistant suffix set, label prefixes, and the allowed Behavior
output domain. These define the label space for both Behavior and
Behavior_Denoised columns.
"""

BASE_BEHAVIORS   = ("Jump", "Walk", "Stationary", "Freeze")
# Core set of behaviors assigned during Layer1 classification.

RESISTANT_SUFFIX = ("Walk", "Stationary", "Freeze")
# Only these behaviors are eligible for resistant classification
# (must fully cover the [pre, post] window).

LAYER1_PREFIX    = "Layer1_"
# Prefix for Layer1 labels.

LAYER2_PREFIX    = "Layer2_"
# Prefix for Layer2 labels.

RESISTANT_PREFIX = "Resistant_"
# Prefix for resistant labels.

BEHAVIOR_OUTPUT  = ("Jump", "Walk", "Stationary", "Freeze", "Resistant_Freeze")
# Allowed labels for both 'Behavior' and 'Behavior_Denoised' columns.


#%% CELL 03 — HELPERS
"""
Internal helpers shared by classifiers. No I/O, no logging, no side effects.
"""


#%%% CELL 03.1 — Codebook (strict, private)
"""
Fixed mappings for label codes. Used when a compact numeric representation
is needed. Unknowns raise; NaNs map to _NAN_CODE.
"""
_LABEL_TO_CODE = {"Walk": 0, "Stationary": 1, "Freeze": 2, "Jump": 3}
_CODE_TO_LABEL = {value: key for key, value in _LABEL_TO_CODE.items()}
_NAN_CODE = -1


#%%% CELL 03.2 — _encode_labels and _decode_labels
"""
Strict conversion between string labels and integer codes.

Why strict?
- Catches typos and prefix drift early (raises instead of guessing).
- Keeps downstream vectorized ops deterministic.
"""
def _encode_labels(labels: np.ndarray, *, prefix: str) -> np.ndarray:
    """
    Map prefixed labels to integer codes.
    'Layer2_Walk' → 0, 'Layer2_Jump' → 3, NaN → -1.
    """
    codes = np.full(len(labels), _NAN_CODE, dtype=np.int16)
    for index, value in enumerate(labels):
        if isinstance(value, str):
            base = BC_UTILS["strip_prefix"](prefix, value)
            code = _LABEL_TO_CODE.get(base)
            if code is None:
                raise ValueError(f"Unknown label '{value}' (prefix='{prefix}')")
            codes[index] = code
        elif pd.isna(value):
            codes[index] = _NAN_CODE
        else:
            raise ValueError(f"Non-string label at index {index}: {type(value)}")
    return codes

def _decode_labels(codes: np.ndarray, *, prefix: str) -> np.ndarray:
    """
    Map integer codes back to prefixed labels.
    0 → 'Layer2_Walk', 3 → 'Layer2_Jump', -1 → NaN.
    """
    labels = np.empty(len(codes), dtype=object)
    labels[:] = np.nan
    for index, code in enumerate(codes):
        if code == _NAN_CODE:
            continue
        base = _CODE_TO_LABEL.get(int(code))
        if base is None:
            raise ValueError(f"Unknown code '{code}' at index {index}")
        labels[index] = BC_UTILS["ensure_prefixed"](prefix, base)
    return labels


#%%% CELL 03.3 — _resolve_tiebreak
"""
Resolve ties among Walk, Stationary, and Freeze using TIEBREAK_LAYER2.
Deterministic ordering (default: Walk > Stationary > Freeze).
"""
def _resolve_tiebreak(class_counts: dict[str, int]) -> str:
	best_label = None
	best_value = -1
	for label in TIEBREAK_LAYER2:
		value = class_counts.get(label, 0)
		if value > best_value:
			best_label = label
			best_value = value
	return best_label or TIEBREAK_LAYER2[0]


#%%% CELL 03.5 — Speed smoothing for Layer1_Denoised (centered; ignore NaNs; no smoothing if any ≥ HIGH_SPEED)
"""
Centered moving-average smoothing for speed (mm/s) used by Layer1_Denoised.

Windowing matches Layer2 semantics:
  • window_length = EXPERIMENT['seconds_to_frames'](LAYER2_AVG_WINDOW_SEC) + 1  (odd; centered)
  • For each index i, consider [i-half_window, i+half_window].

Rules:
  • If the window contains ANY sample with speed ≥ HIGH_SPEED, do NOT smooth:
        DSpeed[i] = raw Speed[i]   (preserve center value as-is)
    (This includes the case where ALL samples are ≥ HIGH_SPEED.)
  • Otherwise, compute the mean of VALID samples in the window:
        VALID = non-NaN and < HIGH_SPEED
    – If the count of VALID samples is 0 (e.g., window is all NaNs), set DSpeed[i] = NaN.
  • NaNs never contribute to the average.

Outputs a new column 'DSpeed' for classification in Layer1_Denoised.
"""

def _smooth_speed_centered_array_with_high_guard(speed_mm_per_s: np.ndarray) -> np.ndarray:
    frame_count = len(speed_mm_per_s)

    # Derive centered odd window from the Layer2 knob (keeps semantics identical to Layer2)
    window_size_frames = EXPERIMENT["seconds_to_frames"](LAYER2_AVG_WINDOW_SEC)  # integer number of frames
    window_length = int(window_size_frames) + 1  # enforce odd length
    half_window = window_length // 2

    out = np.empty(frame_count, dtype=float)
    out[:] = np.nan

    # Prepare arrays and masks
    speed = speed_mm_per_s.astype(float, copy=False)
    is_nan = pd.isna(speed)
    is_high = (~is_nan) & (speed >= HIGH_SPEED)   # Jump-level or higher

    # Valid for averaging: not NaN and strictly below HIGH_SPEED
    valid = (~is_nan) & (~is_high)

    # Cumulative sums for O(1) window queries over valid values
    s = np.where(valid, speed, 0.0).astype(float, copy=False)
    csum = np.cumsum(s)
    ccount = np.cumsum(valid.astype(int))

    # Cumulative counts of high-speed samples to detect "any high in window"
    chigh = np.cumsum(is_high.astype(int))

    def win_stats(lo: int, hi: int):
        # inclusive lo..hi, returns (sum_valid, count_valid, count_high)
        if lo < 0: lo = 0
        if hi >= frame_count: hi = frame_count - 1
        if lo > hi:
            return 0.0, 0, 0
        sum_valid = csum[hi] - (csum[lo - 1] if lo > 0 else 0.0)
        cnt_valid = ccount[hi] - (ccount[lo - 1] if lo > 0 else 0)
        cnt_high  = chigh[hi] - (chigh[lo - 1] if lo > 0 else 0)
        return sum_valid, cnt_valid, cnt_high

    for i in range(frame_count):
        lo = i - half_window
        hi = i + half_window
        sum_valid, cnt_valid, cnt_high = win_stats(lo, hi)

        if cnt_high > 0:
            # If ANY sample in the window is ≥ HIGH_SPEED, keep the center raw value (no smoothing).
            out[i] = speed[i]
            continue

        if cnt_valid > 0:
            out[i] = sum_valid / cnt_valid
        else:
            # No valid samples and no high-speed samples -> all NaN window
            out[i] = np.nan

    return out


#%%% CELL 04.1a — Speed denoising with high-speed and response guards
"""
Internal helper used by classify_layer1_denoised to compute a smoothed speed track.

This function generalises `_smooth_speed_centered_array_with_high_guard` by also
accepting an optional per-frame guard mask (e.g., frames inside a post-stimulus
response window). The smoothing window length is derived from
`SPEED_DENOISE_AVG_WINDOW_SEC` rather than `LAYER2_AVG_WINDOW_SEC` to decouple
Layer1 denoising from Layer2 smoothing. The semantics are:

    • Compute a centered window of odd length W = seconds_to_frames(SPEED_DENOISE_AVG_WINDOW_SEC) + 1.
    • Any frame is considered a guard if it meets either of the following:
        – Its raw speed is ≥ HIGH_SPEED (jump threshold).
        – It lies inside the provided `is_response` mask and
          SPEED_DENOISE_SKIP_RESPONSE_WINDOW is True.
    • Guard frames are never averaged; if ANY guard appears in the window, the
      centre frame retains its raw speed value.
    • Only frames that are non-NaN and non-guard are averaged. If no valid
      samples exist in the window (and no guards), the result is NaN.

Parameters
----------
speed_mm_per_s : np.ndarray
    Raw speed signal in mm/s.
is_response : np.ndarray | None
    Boolean array indicating frames that lie in the post-stimulus response
    window. When SPEED_DENOISE_SKIP_RESPONSE_WINDOW is False or this array is
    None, response windows are ignored.

Returns
-------
np.ndarray
    Smoothed speed track of the same length as the input.
"""
def _smooth_speed_centered_array_for_speed_denoise(
    speed_mm_per_s: np.ndarray,
    *,
    is_response: np.ndarray | None = None,
) -> np.ndarray:
    frame_count = len(speed_mm_per_s)
    # Derive window length from the dedicated speed denoise knob
    window_size_frames = EXPERIMENT["seconds_to_frames"](float(SPEED_DENOISE_AVG_WINDOW_SEC))
    window_length = int(window_size_frames) + 1  # enforce odd
    half_window = window_length // 2

    out = np.empty(frame_count, dtype=float)
    out[:] = np.nan

    # Cast to float for numeric comparisons
    speed = speed_mm_per_s.astype(float, copy=False)
    is_nan = pd.isna(speed)
    # High-speed guard (Jump-level or higher)
    is_high = (~is_nan) & (speed >= HIGH_SPEED)
    # Optional response guard
    if SPEED_DENOISE_SKIP_RESPONSE_WINDOW and is_response is not None:
        # Ensure mask is boolean of correct length
        resp_mask = np.asarray(is_response, dtype=bool)
        if resp_mask.shape[0] != frame_count:
            # Defensive: ignore mismatched masks
            resp_mask = np.zeros(frame_count, dtype=bool)
    else:
        resp_mask = np.zeros(frame_count, dtype=bool)

    # Combined guard mask: high speed OR response window
    guard = is_high | resp_mask
    # Valid samples: non-NaN and not guarded
    valid = (~is_nan) & (~guard)

    # Cumulative sums for fast window queries
    s = np.where(valid, speed, 0.0)
    csum = np.cumsum(s)
    ccount = np.cumsum(valid.astype(int))
    cguard = np.cumsum(guard.astype(int))

    def win_stats(lo: int, hi: int):
        # inclusive lo..hi, returns (sum_valid, count_valid, count_guard)
        if lo < 0:
            lo = 0
        if hi >= frame_count:
            hi = frame_count - 1
        if lo > hi:
            return 0.0, 0, 0
        sum_valid = csum[hi] - (csum[lo - 1] if lo > 0 else 0.0)
        cnt_valid = ccount[hi] - (ccount[lo - 1] if lo > 0 else 0)
        cnt_guard = cguard[hi] - (cguard[lo - 1] if lo > 0 else 0)
        return sum_valid, cnt_valid, cnt_guard

    for i in range(frame_count):
        lo = i - half_window
        hi = i + half_window
        sum_valid, cnt_valid, cnt_guard = win_stats(lo, hi)
        if cnt_guard > 0:
            # Keep centre raw value if any guard (high speed or response) in window
            out[i] = speed[i]
        elif cnt_valid > 0:
            out[i] = sum_valid / cnt_valid
        else:
            out[i] = np.nan
    return out


def smooth_speed_for_layer1_denoise(df: pd.DataFrame,
                                    *,
                                    speed: str = "Speed",
                                    out_col: str = "DSpeed") -> pd.DataFrame:
    """
    Public helper: compute a smoothed speed track for Layer1_Denoised.
    - Writes `out_col` (default 'DSpeed').
    - Uses centered window identical to Layer2's semantics.
    - Ignores NaNs when averaging.
    - **No smoothing** if ANY sample in the window is ≥ HIGH_SPEED (keeps center raw value).
    """
    df[out_col] = _smooth_speed_centered_array_with_high_guard(
        df[speed].to_numpy(copy=False)
    )
    return df


#%% CELL 04 — LAYER 1
"""
First-pass classification from raw kinematics.
Policy (in precedence order, per frame):
1) Jump           → if speed ≥ HIGH_SPEED
2) Freeze         → else if motion == 0
3) Walk           → else if LOW_SPEED ≤ speed < HIGH_SPEED
4) Stationary     → else if speed < LOW_SPEED
NaN speed remains NaN. Outputs are prefixed strings like 'Layer1_Walk'.
"""


#%%% CELL 04.1 — classify_layer1 (public) + _classify_layer1_array (private)
"""
How this works
- Reads 'speed' [mm/s] and binary 'motion' (0/1/NaN) from the DataFrame.
- Applies the precedence rules above *in order* to each frame.
- Writes exactly one column (default 'Layer1') of prefixed labels.

Why precedence matters
- If a frame is Jump by speed, nothing else can reassign it.
- Freeze (no motion) only applies when the frame didn’t already qualify as Jump.
- Walk beats Stationary only within the low/high speed band.
"""
def _classify_layer1_array(speed_mm_per_s: np.ndarray, motion_binary: np.ndarray) -> np.ndarray:
    frame_count = len(speed_mm_per_s)
    layer1_labels = np.empty(frame_count, dtype=object)
    layer1_labels[:] = np.nan

    # Rule masks
    speed_is_nan = pd.isna(speed_mm_per_s)
    is_jump       = (~speed_is_nan) & (speed_mm_per_s >= HIGH_SPEED)
    is_freeze     = (motion_binary == 0)
    is_walk       = (~speed_is_nan) & (speed_mm_per_s >= LOW_SPEED) & (speed_mm_per_s < HIGH_SPEED)
    is_stationary = (~speed_is_nan) & (speed_mm_per_s < LOW_SPEED)

    # Apply precedence: Jump → Freeze → Walk → Stationary
    layer1_labels[is_jump] = BC_UTILS["ensure_prefixed"](LAYER1_PREFIX, "Jump")
    remaining_mask = ~is_jump

    layer1_labels[remaining_mask & is_freeze] = BC_UTILS["ensure_prefixed"](LAYER1_PREFIX, "Freeze")
    remaining_mask = remaining_mask & (~is_freeze)

    layer1_labels[remaining_mask & is_walk] = BC_UTILS["ensure_prefixed"](LAYER1_PREFIX, "Walk")
    remaining_mask = remaining_mask & (~is_walk)

    layer1_labels[remaining_mask & is_stationary] = BC_UTILS["ensure_prefixed"](LAYER1_PREFIX, "Stationary")
    return layer1_labels


def classify_layer1(df: pd.DataFrame,
                    *,
                    speed: str = "Speed",
                    motion: str = "Motion",
                    out_col: str = "Layer1") -> pd.DataFrame:
    """
Reads 'speed' and 'motion', writes 'out_col' (default 'Layer1').
Speed is in mm/s; motion is 0/1/NaN. See module policy for precedence.
"""
    df[out_col] = _classify_layer1_array(
        df[speed].to_numpy(copy=False),
        df[motion].to_numpy(copy=False),
    )
    return df


#%%% CELL 04.2 — classify_layer1_denoised (public) + _classify_layer1_denoised_array (private)  [REPLACE THIS CELL]
"""
Layer1_Denoised — independent from Layer1, using smoothed speed with high-speed guard.

Process
  1) Compute 'DSpeed' with a centered moving average:
     • Ignore NaNs in averaging.
     • If ANY sample in the window is ≥ HIGH_SPEED, do NOT smooth; keep center raw Speed[i].
     • Otherwise average samples that are non-NaN and < HIGH_SPEED.
     • If no valid samples and no high-speed samples exist in the window, DSpeed[i] = NaN.
  2) Re-run the Layer1 precedence on (DSpeed, Motion):
     Jump (DSpeed ≥ HIGH_SPEED) → Freeze (Motion == 0) → Walk (DSpeed ≥ LOW_SPEED) → Stationary.
  3) Apply micro-bout deletion on this fresh label stream:
     delete Walk/Stationary/Freeze bouts ≤ LAYER1_DENOISE_MICROBOUT_MAX_FRAMES.
     Jump bouts are never deleted.

Outputs
  • Writes 'DSpeed' (smoothed speed) to df.
  • Writes 'Layer1_Denoised' (freshly classified on DSpeed).
The original 'Layer1' column (raw-Speed-based) is untouched.
"""

def _classify_layer1_denoised_array(layer1_like_labels: np.ndarray) -> np.ndarray:
    """
    Apply micro-bout deletion to a Layer1-like label stream.
    Deletes short runs (≤ LAYER1_DENOISE_MICROBOUT_MAX_FRAMES) only for Walk/Stationary/Freeze.
    Jump bouts are preserved.
    """
    source = layer1_like_labels
    output = source.copy()
    frame_count = len(source)

    label_jump       = BC_UTILS["ensure_prefixed"](LAYER1_PREFIX, "Jump")
    label_walk       = BC_UTILS["ensure_prefixed"](LAYER1_PREFIX, "Walk")
    label_stationary = BC_UTILS["ensure_prefixed"](LAYER1_PREFIX, "Stationary")
    label_freeze     = BC_UTILS["ensure_prefixed"](LAYER1_PREFIX, "Freeze")

    i = 0
    while i < frame_count:
        v = source[i]
        if not isinstance(v, str):
            i += 1
            continue
        j = i + 1
        while j < frame_count and source[j] == v:
            j += 1
        run_len = j - i
        if v != label_jump and run_len <= LAYER1_DENOISE_MICROBOUT_MAX_FRAMES:
            if v in (label_walk, label_stationary, label_freeze):
                output[i:j] = np.nan
        i = j

    return output


def classify_layer1_denoised(
    df: pd.DataFrame,
    *,
    in_col: str = "Layer1",          # kept for API compatibility (ignored)
    out_col: str = "Layer1_Denoised",
    speed: str = "Speed",
    motion: str = "Motion",
    dspeed_out: str = "Speed_Denoised",
) -> pd.DataFrame:
    """
    Compute a denoised Layer1-like label stream using smoothed speed.

    This implementation no longer derives its labels from the raw `Layer1` column.
    Instead it performs a fresh classification based on a smoothed speed track.

    Steps
      1) Compute `dspeed_out` = Speed_Denoised using a centered moving average
         defined by `SPEED_DENOISE_AVG_WINDOW_SEC` with high-speed and optional
         response-window guards. NaNs and guarded frames are excluded from
         averaging. If any guard appears in the window, the centre retains its
         raw speed.
      2) Re-run the Layer1 precedence on (`Speed_Denoised`, Motion) to produce
         a fresh label stream (Jump, Walk, Stationary, Freeze).
      3) Apply micro-bout deletion (keeps Jump; deletes short Walk/Stationary/Freeze).

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing at least the columns specified by `speed` and
        `motion`, as well as any stimulus columns required for computing
        response windows when `SPEED_DENOISE_SKIP_RESPONSE_WINDOW` is True.
    in_col : str, optional
        Ignored; preserved for API compatibility.
    out_col : str, optional
        Name of the output column for the denoised Layer1-like labels.
    speed : str, optional
        Name of the column containing raw speed in mm/s.
    motion : str, optional
        Name of the column containing binary motion (0/1/NaN).
    dspeed_out : str, optional
        Name of the column to write the smoothed speed track.

    Returns
    -------
    pd.DataFrame
        The input DataFrame with two new columns: `dspeed_out` and `out_col`.
    """
    # (1) Determine whether response-window guards are needed and build mask
    is_response = None
    if SPEED_DENOISE_SKIP_RESPONSE_WINDOW:
        # Identify stimulus columns relevant for resistant windows
        stim_cols = [c for c in RESISTANT_STIM_COLUMNS if c in df.columns]
        if stim_cols:
            # Extract stimulus sub-DF
            stim_df = df.loc[:, stim_cols]
            # Build post-stimulus windows using 0 pre-sec and STARTLE_POST_STIM_SEC post-sec
            windows = _build_resistant_windows(
                stim_df,
                pre_sec=0.0,
                post_sec=float(STARTLE_POST_STIM_SEC),
            )
            if windows:
                # Construct a boolean mask over frames
                n = len(df)
                mask = np.zeros(n, dtype=bool)
                for start, end in windows:
                    # clamp bounds defensively
                    s = max(0, int(start))
                    e = min(n, int(end))
                    if s < e:
                        mask[s:e] = True
                is_response = mask

    # (2) Smooth speed and expose the denoised track
    df[dspeed_out] = _smooth_speed_centered_array_for_speed_denoise(
        df[speed].to_numpy(copy=False),
        is_response=is_response,
    )

    # (3) Fresh classification using smoothed speed and motion
    fresh_layer1_like = _classify_layer1_array(
        df[dspeed_out].to_numpy(copy=False),
        df[motion].to_numpy(copy=False),
    )

    # (4) Micro-bout deletion
    df[out_col] = _classify_layer1_denoised_array(fresh_layer1_like)
    return df



#%% CELL 05 — LAYER 2
"""
Second-pass classification by local consensus.
Policy per frame:
1) Build a centered window of odd length W around the frame:
   W = EXPERIMENT['seconds_to_frames'](LAYER2_AVG_WINDOW_SEC) + 1
2) Jump override: if any 'Layer1_Jump' appears in the window → 'Layer2_Jump'
3) Otherwise, ignore NaNs and count {Walk, Stationary, Freeze} in the window.
   • If no valid labels → NaN
   • Else choose the max; ties resolved by TIEBREAK_LAYER2 (Walk > Stationary > Freeze)
The denoised variant adds a half-missing rule: valid_count must be > floor(W/2), else NaN.
Outputs are prefixed strings like 'Layer2_Walk'.
"""


#%%% CELL 05.1 — classify_layer2 (public) + _classify_layer2_array (private)
"""
How this works
- Reads 'Layer1' labels.
- Computes W once from the experiment’s seconds→frames converter.
- For each index, applies Jump override, then majority vote with tie-break.
- Writes one column 'Layer2' by default.
"""
def _classify_layer2_array(layer1_labels: np.ndarray) -> np.ndarray:
    frame_count = len(layer1_labels)

    window_size_frames = EXPERIMENT["seconds_to_frames"](LAYER2_AVG_WINDOW_SEC)
    window_length = window_size_frames + 1  # enforce odd
    half_window = window_length // 2

    layer2_labels = np.empty(frame_count, dtype=object)
    layer2_labels[:] = np.nan

    label_l1_jump       = BC_UTILS["ensure_prefixed"](LAYER1_PREFIX, "Jump")
    label_l1_walk       = BC_UTILS["ensure_prefixed"](LAYER1_PREFIX, "Walk")
    label_l1_stationary = BC_UTILS["ensure_prefixed"](LAYER1_PREFIX, "Stationary")
    label_l1_freeze     = BC_UTILS["ensure_prefixed"](LAYER1_PREFIX, "Freeze")

    label_l2_jump       = BC_UTILS["ensure_prefixed"](LAYER2_PREFIX, "Jump")
    label_l2_walk       = BC_UTILS["ensure_prefixed"](LAYER2_PREFIX, "Walk")
    label_l2_stationary = BC_UTILS["ensure_prefixed"](LAYER2_PREFIX, "Stationary")
    label_l2_freeze     = BC_UTILS["ensure_prefixed"](LAYER2_PREFIX, "Freeze")

    for frame_index in range(frame_count):
        left_index  = max(0, frame_index - half_window)
        right_index = min(frame_count, frame_index + half_window + 1)
        window_values = layer1_labels[left_index:right_index]

        # (1) Jump override
        if np.any(window_values == label_l1_jump):
            layer2_labels[frame_index] = label_l2_jump
            continue

        # (2) Count among valid strings only
        valid_labels = [val for val in window_values if isinstance(val, str)]
        if not valid_labels:
            layer2_labels[frame_index] = np.nan
            continue

        class_counts = {
            "Walk":       sum(val == label_l1_walk       for val in valid_labels),
            "Stationary": sum(val == label_l1_stationary for val in valid_labels),
            "Freeze":     sum(val == label_l1_freeze     for val in valid_labels),
        }

        # (3) Tie-break with configured order
        winner = _resolve_tiebreak(class_counts)
        if winner == "Walk":
            layer2_labels[frame_index] = label_l2_walk
        elif winner == "Stationary":
            layer2_labels[frame_index] = label_l2_stationary
        else:
            layer2_labels[frame_index] = label_l2_freeze

    return layer2_labels


def classify_layer2(df: pd.DataFrame,
                    *,
                    in_col: str = "Layer1",
                    out_col: str = "Layer2") -> pd.DataFrame:
    """
Reads 'in_col' (Layer1), writes 'out_col' (default 'Layer2').
Jump override and tie-break semantics as documented above.
"""
    df[out_col] = _classify_layer2_array(
        df[in_col].to_numpy(copy=False)
    )
    return df


#%%% CELL 05.2 — classify_layer2_denoised (public) + _classify_layer2_denoised_array (private)
"""
How this works
- Same as Layer2, but applies the half-missing rule:
  valid_count must be > floor(W/2) or the output is NaN.
- Reads 'Layer1_Denoised', writes 'Layer2_Denoised'.
"""
def _classify_layer2_denoised_array(layer1_denoised_labels: np.ndarray) -> np.ndarray:
    frame_count = len(layer1_denoised_labels)

    window_size_frames = EXPERIMENT["seconds_to_frames"](LAYER2_AVG_WINDOW_SEC)
    window_length = window_size_frames + 1
    half_window = window_length // 2
    min_valid = window_length // 2  # strictly greater than this

    layer2_denoised_labels = np.empty(frame_count, dtype=object)
    layer2_denoised_labels[:] = np.nan

    label_l1_jump       = BC_UTILS["ensure_prefixed"](LAYER1_PREFIX, "Jump")
    label_l1_walk       = BC_UTILS["ensure_prefixed"](LAYER1_PREFIX, "Walk")
    label_l1_stationary = BC_UTILS["ensure_prefixed"](LAYER1_PREFIX, "Stationary")
    label_l1_freeze     = BC_UTILS["ensure_prefixed"](LAYER1_PREFIX, "Freeze")

    label_l2_jump       = BC_UTILS["ensure_prefixed"](LAYER2_PREFIX, "Jump")
    label_l2_walk       = BC_UTILS["ensure_prefixed"](LAYER2_PREFIX, "Walk")
    label_l2_stationary = BC_UTILS["ensure_prefixed"](LAYER2_PREFIX, "Stationary")
    label_l2_freeze     = BC_UTILS["ensure_prefixed"](LAYER2_PREFIX, "Freeze")

    for frame_index in range(frame_count):
        left_index  = max(0, frame_index - half_window)
        right_index = min(frame_count, frame_index + half_window + 1)
        window_values = layer1_denoised_labels[left_index:right_index]

        # (1) Jump override
        if np.any(window_values == label_l1_jump):
            layer2_denoised_labels[frame_index] = label_l2_jump
            continue

        # (2) Half-missing rule
        valid_labels = [val for val in window_values if isinstance(val, str)]
        if len(valid_labels) <= min_valid:
            layer2_denoised_labels[frame_index] = np.nan
            continue

        # (3) Count and tie-break
        class_counts = {
            "Walk":       sum(val == label_l1_walk       for val in valid_labels),
            "Stationary": sum(val == label_l1_stationary for val in valid_labels),
            "Freeze":     sum(val == label_l1_freeze     for val in valid_labels),
        }
        winner = _resolve_tiebreak(class_counts)
        if winner == "Walk":
            layer2_denoised_labels[frame_index] = label_l2_walk
        elif winner == "Stationary":
            layer2_denoised_labels[frame_index] = label_l2_stationary
        else:
            layer2_denoised_labels[frame_index] = label_l2_freeze

    return layer2_denoised_labels


def classify_layer2_denoised(df: pd.DataFrame,
                             *,
                             in_col: str = "Layer1_Denoised",
                             out_col: str = "Layer2_Denoised") -> pd.DataFrame:
    """
Reads 'in_col' (Layer1_Denoised), writes 'out_col' (default 'Layer2_Denoised').
Adds the half-missing rule on top of the standard Layer2 logic.
"""
    df[out_col] = _classify_layer2_denoised_array(
        df[in_col].to_numpy(copy=False)
    )
    return df



#%% CELL 06 — RESISTANT CLASSIFICATION
"""
Stimulus-coupled labeling by full coverage.
Policy
- Build merged [start, end) stimulus windows from RESISTANT_STIM_COLUMNS using
  STARTLE_PRE_STIM_SEC / STARTLE_POST_STIM_SEC converted via the experiment clock.
- For each non-Jump Layer2 bout (Walk/Stationary/Freeze), mark it as resistant
  if a merged stimulus window fits entirely inside the bout.
- Emit one compact per-frame label stream: 'Resistant_Walk' / 'Resistant_Stationary'
  / 'Resistant_Freeze' (priority Walk > Stationary > Freeze), or NaN.
The denoised path is identical but uses 'Layer2_Denoised'.
"""


#%%% CELL 06.1 — Private helpers for resistant
"""
What happens here
- _build_resistant_windows: detection-aware rising edges → per-onset windows → merge touching/overlapping.
- _label_resistant: convert Layer2-like labels + windows into a compact 'Resistant_*' stream
  by testing full coverage inside each contiguous bout (run) of a target class.
"""
def _build_resistant_windows(stim_df: pd.DataFrame,
                             pre_sec: float,
                             post_sec: float) -> list[tuple[int, int]]:
    """
Detection-aware rising edges → windows → merge:
- Resolve (off,on) per stimulus column via Config.experiment (strict, via column_name).
- For each onset t, create [t - pre, t + post] in frames, clamped to [0, N); end is exclusive.
- Merge touching/overlapping windows across all stimulus columns.
"""
    pre_frames  = int(EXPERIMENT["seconds_to_frames"](pre_sec))
    post_frames = int(EXPERIMENT["seconds_to_frames"](post_sec))

    total_frames = len(stim_df)
    raw_windows: list[tuple[int, int]] = []

    for column_name in RESISTANT_STIM_COLUMNS:
        if column_name not in stim_df.columns:
            continue

        # Strict API: pass column_name; resolver checks STIMULI[*]['name'] and returns (off,on) internally
        onset_indices = BC_UTILS["onsets"](stim_df[column_name], column_name=column_name)

        for onset_index in onset_indices:
            start_index = max(0, onset_index - pre_frames)
            end_index   = min(total_frames, onset_index + post_frames + 1)  # end exclusive
            if start_index < end_index:
                raw_windows.append((start_index, end_index))

    if not raw_windows:
        return []

    raw_windows.sort()
    merged: list[tuple[int, int]] = [raw_windows[0]]
    for start_index, end_index in raw_windows[1:]:
        last_start, last_end = merged[-1]
        if start_index <= last_end:  # touch or overlap
            merged[-1] = (last_start, max(last_end, end_index))
        else:
            merged.append((start_index, end_index))
    return merged


def _label_resistant(layer2_like_labels: np.ndarray,
                     windows: list[tuple[int, int]]) -> np.ndarray:
    """
Full-coverage inside bouts:
- For each target class {Walk, Stationary, Freeze}, iterate contiguous runs.
- If any merged window [ws, we) satisfies bout_start ≤ ws and we ≤ bout_end,
  mark the entire run with the corresponding 'Resistant_*' label.
- Priority is enforced by writing lower-priority first (Freeze, then Stationary)
  and higher-priority last (Walk) so it overwrites on overlaps.
"""
    frame_count = len(layer2_like_labels)
    resistant_labels = np.full(frame_count, np.nan, dtype=object)
    if frame_count == 0 or not windows:
        return resistant_labels

    label_walk       = BC_UTILS["ensure_prefixed"](LAYER2_PREFIX, "Walk")
    label_stationary = BC_UTILS["ensure_prefixed"](LAYER2_PREFIX, "Stationary")
    label_freeze     = BC_UTILS["ensure_prefixed"](LAYER2_PREFIX, "Freeze")

    token_walk       = BC_UTILS["ensure_prefixed"](RESISTANT_PREFIX, "Walk")
    token_stationary = BC_UTILS["ensure_prefixed"](RESISTANT_PREFIX, "Stationary")
    token_freeze     = BC_UTILS["ensure_prefixed"](RESISTANT_PREFIX, "Freeze")

    for target_label, resistant_token in [
        (label_freeze,     token_freeze),     # lowest priority
        (label_stationary, token_stationary), # middle
        (label_walk,       token_walk),       # highest priority
    ]:
        for bout_start, bout_end, value in BC_UTILS["iter_label_runs"](layer2_like_labels):
            if value != target_label:
                continue
            # check if any window fully fits inside the bout
            for window_start, window_end in windows:
                if window_start >= bout_start and window_end <= bout_end:
                    resistant_labels[bout_start:bout_end] = resistant_token
                    break
    return resistant_labels


#%%% CELL 06.2 — classify_resistant_behaviors (public) + _classify_resistant_array (private)
"""
How this works (legacy path)
- Reads 'Layer2' and stimulus columns.
- Builds merged stimulus windows using STARTLE_PRE_STIM_SEC/STARTLE_POST_STIM_SEC.
- Produces a *single* compact per-frame resistant label stream (no extra flag columns).
- Writes 'Resistant' by default.
"""
def _classify_resistant_array(layer2_like_labels: np.ndarray,
                              stim_df: pd.DataFrame,
                              *,
                              pre_sec: float,
                              post_sec: float) -> np.ndarray:
	merged_windows = _build_resistant_windows(stim_df, pre_sec, post_sec)
	return _label_resistant(layer2_like_labels, merged_windows)


def classify_resistant_behaviors(df: pd.DataFrame,
                                 *,
                                 l2_col: str = "Layer2",
                                 out_col: str = "Resistant",
                                 stim_cols: Sequence[str] = RESISTANT_STIM_COLUMNS,
                                 pre_sec: float = STARTLE_PRE_STIM_SEC,
                                 post_sec: float = STARTLE_POST_STIM_SEC) -> pd.DataFrame:
	"""
Reads 'l2_col' (Layer2) and stimulus columns, writes compact 'out_col' (default 'Resistant').
Full-coverage criterion and class priority as described in CELL 06.
"""
	stimulus_frame = df.loc[:, list(stim_cols)]
	df[out_col] = _classify_resistant_array(
		df[l2_col].to_numpy(copy=False),
		stimulus_frame,
		pre_sec=pre_sec,
		post_sec=post_sec,
	)
	return df


#%%% CELL 06.3 — classify_resistant_behaviors_denoised (public)
"""
How this works (denoised path)
- Same logic as legacy resistant, but reads 'Layer2_Denoised'.
- Writes a compact per-frame label stream to 'Resistant_Denoised'.
"""
def classify_resistant_behaviors_denoised(df: pd.DataFrame,
                                          *,
                                          l2d_col: str = "Layer2_Denoised",
                                          out_col: str = "Resistant_Denoised",
                                          stim_cols: Sequence[str] = RESISTANT_STIM_COLUMNS,
                                          pre_sec: float = STARTLE_PRE_STIM_SEC,
                                          post_sec: float = STARTLE_POST_STIM_SEC) -> pd.DataFrame:
	stimulus_frame = df.loc[:, list(stim_cols)]
	df[out_col] = _classify_resistant_array(
		df[l2d_col].to_numpy(copy=False),
		stimulus_frame,
		pre_sec=pre_sec,
		post_sec=post_sec,
	)
	return df


#%% CELL 07 — FINAL BEHAVIOR (PUBLISHERS)
"""
Publishers that map Layer-2 outputs (and resistant annotations) into the final
Behavior domain. Two parallel surfaces:

  • classify_behavior(df, l2_col="Layer2", resistant_col="Resistant", out_col="Behavior")
      - Pure mapping from Layer2_* to {"Jump","Walk","Stationary","Freeze"}, with
        Freeze→Resistant_Freeze promotion when resistant coverage warrants.
      - Does not denoise beyond upstream layers and does not alter NaNs.

  • classify_behavior_denoised(df, l2d_col="Layer2_Denoised", resistant_col="Resistant_Denoised",
                               out_col="Behavior_Denoised")
      - Same mapping and promotion as above, using the denoised inputs.
      - Then applies an optional *bounded-NaN cleanup*:
          · Only internal (bounded) NaN runs are considered.
          · Flanks must be the same Behavior token.
          · Gap length must be ≤ MAX_NAN_BOUT_CLEAN_SEC (seconds → frames).
          · If MIN_BOUND_BOUT_SEC is numeric: each flank bout must be ≥ that size.
          · If SKIP_RESPONSE_WINDOW is True: any NaN gap that overlaps the post-stim
            response window [onset, onset + STARTLE_POST_STIM_SEC] is left as NaN.

The non-denoised Behavior path remains a direct mapping+promotion with no NaN filling.
"""

#%%% CELL 07.1 — classify_behavior (public) + _classify_behavior_array (private)
"""
How this works
- Reads 'Layer2' and 'Resistant'.
- Converts Layer2_* strings to Behavior domain tokens {Jump, Walk, Stationary, Freeze}.
- Applies the Freeze→Resistant_Freeze promotion when the compact resistant label indicates full coverage.
- Writes one column (default 'Behavior').
"""
def _classify_behavior_array(layer2_label_stream: np.ndarray,
                             resistant_label_stream: np.ndarray) -> np.ndarray:
    """
    Pure kernel: Layer2_* + Resistant_* → Behavior domain.
    NaNs are preserved (no 'Noisy' fill here).
    """
    frame_count = len(layer2_label_stream)
    behavior_labels = np.empty(frame_count, dtype=object)
    behavior_labels[:] = np.nan

    # Canonical Layer2 tokens
    layer2_jump_label       = BC_UTILS["ensure_prefixed"](LAYER2_PREFIX, "Jump")
    layer2_walk_label       = BC_UTILS["ensure_prefixed"](LAYER2_PREFIX, "Walk")
    layer2_stationary_label = BC_UTILS["ensure_prefixed"](LAYER2_PREFIX, "Stationary")
    layer2_freeze_label     = BC_UTILS["ensure_prefixed"](LAYER2_PREFIX, "Freeze")

    # Canonical Resistant token
    resistant_freeze_label  = BC_UTILS["ensure_prefixed"](RESISTANT_PREFIX, "Freeze")

    for frame_index in range(frame_count):
        layer2_value = layer2_label_stream[frame_index]

        # Skip if no valid Layer2 label
        if not isinstance(layer2_value, str):
            continue

        # Map Layer2_* to Behavior base label
        if layer2_value == layer2_jump_label:
            base_behavior = "Jump"
        elif layer2_value == layer2_walk_label:
            base_behavior = "Walk"
        elif layer2_value == layer2_stationary_label:
            base_behavior = "Stationary"
        elif layer2_value == layer2_freeze_label:
            base_behavior = "Freeze"
        else:
            # Unknown token: leave as NaN
            continue

        # Promotion: only Freeze can become Resistant_Freeze
        resistant_value = resistant_label_stream[frame_index]
        if base_behavior == "Freeze" and resistant_value == resistant_freeze_label:
            behavior_labels[frame_index] = "Resistant_Freeze"
        else:
            behavior_labels[frame_index] = base_behavior

    return behavior_labels


def classify_behavior(df: pd.DataFrame,
                      *,
                      l2_col: str = "Layer2",
                      resistant_col: str = "Resistant",
                      out_col: str = "Behavior") -> pd.DataFrame:
    """
Reads 'l2_col' (Layer2) and 'resistant_col' (Resistant),
writes 'out_col' (default 'Behavior').
"""
    df[out_col] = _classify_behavior_array(
        df[l2_col].to_numpy(copy=False),
        df[resistant_col].to_numpy(copy=False),
    )
    return df



#%%% CELL 07.2 — classify_behavior_denoised (public) + bounded-NaN cleaner (private)
"""
How this works
- Map Layer2_Denoised + Resistant_Denoised to the Behavior domain with
  Freeze→Resistant_Freeze promotion.
- Optionally fill short, bounded NaN runs when evidence strongly supports continuity:
    • Only internal NaN runs (bounded by labels on both sides) are considered.
    • Left/right flanks must be the *same* valid Behavior token.
    • NaN run length must be ≤ MAX_NAN_BOUT_CLEAN_SEC (converted to frames).
    • If MIN_BOUND_BOUT_SEC is numeric: each flanking bout must be ≥ that many seconds.
    • If SKIP_RESPONSE_WINDOW is True: skip any NaN run overlapping the response window
      (union of [onset, onset + STARTLE_POST_STIM_SEC] across RESISTANT_STIM_COLUMNS).
- Writes one column (default 'Behavior_Denoised').
"""

def _overlaps_any(interval_start: int, interval_end: int, intervals: list[tuple[int, int]]) -> bool:
    """Return True if [interval_start, interval_end) intersects any [s, e) in intervals."""
    if not intervals:
        return False
    for s, e in intervals:
        if interval_start < e and interval_end > s:
            return True
    return False


def _fill_bounded_nan_bouts(
    behavior_labels: np.ndarray,
    *,
    response_windows: list[tuple[int, int]],
) -> np.ndarray:
    """
    Return a cleaned copy of 'behavior_labels' where short, bounded NaN runs are
    filled with the flanking label when all guards pass.
    """
    n = len(behavior_labels)
    if n == 0:
        return behavior_labels

    cleaned = behavior_labels.copy()

    # Convert seconds thresholds to frames once
    sec2frm = EXPERIMENT["seconds_to_frames"]
    max_nan_frames = (
        None if MAX_NAN_BOUT_CLEAN_SEC is None
        else int(round(sec2frm(float(MAX_NAN_BOUT_CLEAN_SEC))))
    )
    min_bound_frames = (
        None if MIN_BOUND_BOUT_SEC is None
        else int(round(sec2frm(float(MIN_BOUND_BOUT_SEC))))
    )

    # Quick exit if cleaner disabled
    if max_nan_frames is None or max_nan_frames <= 0:
        return cleaned

    # Helpers to measure contiguous bout lengths to left/right
    def _left_bout_len(idx: int, token) -> int:
        k = idx
        while k >= 0 and cleaned[k] == token:
            k -= 1
        return (idx - k)

    def _right_bout_len(idx: int, token) -> int:
        k = idx
        while k < n and cleaned[k] == token:
            k += 1
        return (k - idx)

    i = 0
    while i < n:
        if pd.isna(cleaned[i]):
            # start of a NaN run
            j = i + 1
            while j < n and pd.isna(cleaned[j]):
                j += 1
            # [i:j) is a maximal NaN run
            internal = (i > 0) and (j < n)
            if internal:
                left_label = cleaned[i - 1]
                right_label = cleaned[j]
                # “internal” implies both neighbors are non-NaN; still guard on type
                same_label = (isinstance(left_label, str) and left_label == right_label)
                run_len = j - i

                # Response-window guard
                in_response = _overlaps_any(i, j, response_windows)

                # Optional flank size guard
                flank_ok = True
                if same_label and min_bound_frames is not None:
                    left_len  = _left_bout_len(i - 1, left_label)
                    right_len = _right_bout_len(j, right_label)
                    flank_ok = (left_len >= min_bound_frames) and (right_len >= min_bound_frames)

                if same_label and (run_len <= max_nan_frames) and flank_ok and (not in_response):
                    cleaned[i:j] = left_label  # fill

            i = j
        else:
            i += 1

    return cleaned


def classify_behavior_denoised(df: pd.DataFrame,
                               *,
                               l2d_col: str = "Layer2_Denoised",
                               resistant_col: str = "Resistant_Denoised",
                               out_col: str = "Behavior_Denoised") -> pd.DataFrame:
    """
Reads 'l2d_col' (Layer2_Denoised) and 'resistant_col' (Resistant_Denoised),
maps to Behavior domain with Freeze→Resistant_Freeze promotion, then applies the
bounded-NaN cleanup described above.
"""
    # Step 1 — base mapping + promotion
    base = _classify_behavior_array(
        df[l2d_col].to_numpy(copy=False),
        df[resistant_col].to_numpy(copy=False),
    )

    # Step 2 — optional response-window computation
    response_windows: list[tuple[int, int]] = []
    if SKIP_RESPONSE_WINDOW:
        stim_cols = [c for c in RESISTANT_STIM_COLUMNS if c in df.columns]
        if stim_cols:
            # response window = [onset, onset + STARTLE_POST_STIM_SEC]
            stim_df = df.loc[:, stim_cols]
            response_windows = _build_resistant_windows(
                stim_df,
                pre_sec=0.0,
                post_sec=float(STARTLE_POST_STIM_SEC),
            )

    # Step 3 — bounded NaN cleanup (returns a new array)
    cleaned = _fill_bounded_nan_bouts(base, response_windows=response_windows)

    df[out_col] = cleaned
    return df



#%% CELL 08 — PUBLIC SURFACE & EXECUTION GUARD
"""
Expose the stable classification API as a single read-only dictionary.
All functions are DataFrame-facing: df in → write one column → return df.
"""


#%%% CELL 08.1 — BC_CLASSIFIER (readonly dict)  [UPDATE — add smoother export]
"""
Immutable mapping of public classification functions.
"""
BC_CLASSIFIER = MappingProxyType({
    "classify_layer1": classify_layer1,
    "classify_layer1_denoised": classify_layer1_denoised,
    "classify_layer2": classify_layer2,
    "classify_layer2_denoised": classify_layer2_denoised,
    "classify_resistant_behaviors": classify_resistant_behaviors,
    "classify_resistant_behaviors_denoised": classify_resistant_behaviors_denoised,
    "classify_behavior": classify_behavior,
    "classify_behavior_denoised": classify_behavior_denoised,
    # Optional: call smoothing directly in notebooks for QC/plots
    "smooth_speed_for_layer1_denoise": smooth_speed_for_layer1_denoise,
})



#%%% CELL 08.2 — POLICY SNAPSHOT (PRIVATE)
"""
_on-demand description of the active classification policy._

Purpose
- Return a structured snapshot of all knobs relevant to classification.
- No prints/logs; import and call interactively when needed.
- Uses the experiment clock to provide derived frame counts alongside seconds.

Usage
-------
from BehaviorClassifier._classifier import _describe_policy
info = _describe_policy()  # dict with thresholds, windows, tie-breaks, vocab, etc.
"""


def _describe_policy() -> dict:
    """Return a structured dictionary describing the current classification policy."""
    sec2frm = EXPERIMENT["seconds_to_frames"]

    # Derived windows (frames)
    layer2_window_frames   = int(sec2frm(LAYER2_AVG_WINDOW_SEC)) + 1  # odd, centered
    resistant_pre_frames   = int(sec2frm(STARTLE_PRE_STIM_SEC))
    resistant_post_frames  = int(sec2frm(STARTLE_POST_STIM_SEC))
    max_nan_clean_frames   = (
        None if MAX_NAN_BOUT_CLEAN_SEC is None
        else int(round(sec2frm(float(MAX_NAN_BOUT_CLEAN_SEC))))
    )
    min_bound_bout_frames  = (
        None if MIN_BOUND_BOUT_SEC is None
        else int(round(sec2frm(float(MIN_BOUND_BOUT_SEC))))
    )

    # Derived ordering (automatic, mirrors current config)
    layer1_follow_after_freeze = tuple(lbl for lbl in TIEBREAK_LAYER2 if lbl != "Freeze")
    layer1_precedence = ("Jump", "Freeze", *layer1_follow_after_freeze)
    resistant_priority = tuple(TIEBREAK_LAYER2)

    return {
        "noise_tolerance_frames": int(NOISE_TOLERANCE),

        "layer1": {
            "high_speed_mm_per_s": float(HIGH_SPEED),
            "low_speed_mm_per_s": float(LOW_SPEED),
            "microbout_max_frames": int(LAYER1_DENOISE_MICROBOUT_MAX_FRAMES),
            "precedence": layer1_precedence,
            "outputs_prefix": LAYER1_PREFIX,
        },

        "layer2": {
            "avg_window_sec": float(LAYER2_AVG_WINDOW_SEC),
            "avg_window_frames": int(layer2_window_frames),
            "denoise_min_fraction": float(LAYER2_DENOISE_MIN_VALID_FRACTION),
            "tie_break_order": tuple(TIEBREAK_LAYER2),
            "outputs_prefix": LAYER2_PREFIX,
        },

        "resistant": {
            "stimulus_columns": tuple(RESISTANT_STIM_COLUMNS),
            "pre_sec": float(STARTLE_PRE_STIM_SEC),
            "pre_frames": int(resistant_pre_frames),
            "post_sec": float(STARTLE_POST_STIM_SEC),
            "post_frames": int(resistant_post_frames),
            "outputs_prefix": RESISTANT_PREFIX,
            "priority": resistant_priority,
        },

        "behavior_cleanup": {
            "max_nan_bout_clean_sec": (
                None if MAX_NAN_BOUT_CLEAN_SEC is None else float(MAX_NAN_BOUT_CLEAN_SEC)
            ),
            "max_nan_bout_clean_frames": max_nan_clean_frames,
            "min_bound_bout_sec": (
                None if MIN_BOUND_BOUT_SEC is None else float(MIN_BOUND_BOUT_SEC)
            ),
            "min_bound_bout_frames": min_bound_bout_frames,
            "skip_response_window": bool(SKIP_RESPONSE_WINDOW) if False else bool(SKIP_RESPONSE_WINDOW),
            "response_window_def": "[onset, onset + STARTLE_POST_STIM_SEC]",
        },

        "vocabulary": {
            "base_behaviors": tuple(BASE_BEHAVIORS),
            "behavior_output": tuple(BEHAVIOR_OUTPUT),
            "noisy_label_policy": NOISY_LABEL,
        },
    }



#%% CELL 09 — REPORT
"""
When run directly (e.g., Spyder 'Run File'), print the current classification policy.
This is for developer convenience; does not run during imports.
"""
if __name__ == "__main__":
    from pprint import pprint
    pprint(_describe_policy())
