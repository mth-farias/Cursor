#%%% CELL 00 — MODULE OVERVIEW
'''
{{COMMIT_DETAILS}}
#<github.com/MoitaLab/Repo>
#<full_commit_hash>
#<DD-MM-YYYY HH:MM:SS>

_main.py


Overview
	Skinny orchestrator for end-to-end behavior scoring. This module contains
	no business rules; it sequences dedicated components and returns a small
	session summary. Thresholds, paths, schemas, timing, and QC live in their
	respective modules.

Responsibilities
	• Discover tracked files and decide what to process (skip if already done).
	• For each file, coordinate the conveyor:
	  load → clean ALL stimulus channels → pre-flight QC (fatal) → features →
	  classification → resistant labels → (optional) pose scoring → align/crop →
	  post-class flags (non-fatal, block publish) → publish clean outputs (atomic).
	• Maintain session counters and return the summary payload.

Non-Responsibilities (delegated)
	– Path & naming policy .......... Config.path (PATH)
	– Timebase, periods, stimuli .... Config.experiment (EXPERIMENT)
	– Thresholds & schemas .......... Config.param (PARAM)
	– Mechanics & I/O helpers ........BehaviorClassifier._utils (BC_UTILS)
	– Algorithms (labels) ........... BehaviorClassifier._classifier (BC_CLASSIFIER)
	– QC (errors/flags & REPORTs) ... BehaviorClassifier._qc_error_flag (BC_QC)

Public surface
	behavior_classifier_main()  →  dict

Return payload (exact keys)
	{
		"scoring_seconds": float,
		"files_scored_session": int,
		"session_errors": int,
		"files_processed_session": int,
	}

Notes
	• No path invention here; filenames/locations come from PATH. Parent dirs
	  are ensured by BC_UTILS.write_csv_atomic (mkdir -p inside).
	• Frame math uses EXPERIMENT; stimulus detection uses per-column (off,on)
	  mapping from the registry.
	• Schema selection at publish time is built from PARAM (pose/non-pose lists).
'''

#%% CELL 01 — IMPORTS & PACKAGE SHIM
"""
Purpose
Import required modules for orchestrating behavior classification. Follows the
developer guide style: annotations first, then stdlib, then third-party, then
internal shims.

Notes
- Config registries (PATH, EXPERIMENT, PARAM) are read-only.
- Internal helpers (BC_UTILS, BC_CLASSIFIER, BC_QC) are read-only mappings.
"""

# stdlib
import sys
from pathlib import Path
import time
from types import MappingProxyType
from typing import Optional, Tuple, Dict
import re
from collections import defaultdict

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

# read-only registries
from Config import PATH, EXPERIMENT

# read-only public surfaces (use MappingProxyType dicts, not raw modules)
from BehaviorClassifier import BC_UTILS, BC_CLASSIFIER, BC_QC

# -----------------------------------------------------------------------------
# Local helpers for orchestrator file management
#
# QC only logs errors and flags. Copying of input files on fatal errors and
# saving of flagged outputs is performed here in the main orchestrator. These
# helpers centralize that logic so it can be reused in multiple branches.
def _copy_error_inputs_for_base(base: str, tracked_path: Path) -> None:
    """
    Copy the raw tracked and sleap inputs into the Error folder for forensic
    inspection. This should be invoked whenever a fatal error occurs for a
    particular fly (e.g., failed preflight QC, file unreadable).

    Parameters
    ----------
    base : str
        The base stem (e.g., 'BASE_fly1') used to derive paths.
    tracked_path : Path
        The path to the original tracked CSV on disk.

    Notes
    -----
    - Uses Config.path helpers to build destination paths.
    - Best effort: any exception during copying is suppressed.
    """
    try:
        # Copy tracked input verbatim
        if tracked_path is not None and tracked_path.exists():
            dest_tracked = PATH["error_tracked_copy_path"](tracked_path.name)
            dest_tracked.parent.mkdir(parents=True, exist_ok=True)
            BC_UTILS["copy_atomic"](tracked_path, dest_tracked)

        # Copy sleap input if present
        sleap_src = PATH["sleap_path"](base)
        if sleap_src.exists():
            dest_pose = PATH["error_pose_copy_path"](sleap_src.name)
            dest_pose.parent.mkdir(parents=True, exist_ok=True)
            BC_UTILS["copy_atomic"](sleap_src, dest_pose)
    except Exception:
        # Never abort session on copy failures
        pass


def _save_flagged_outputs(df: pd.DataFrame, base: str) -> None:
    """
    Persist flagged scored and pose outputs for a fly. Called when
    post-classification QC detects one or more non-fatal flags. Files are
    written into BehaviorClassification/Flag/Scored and /Flag/Pose.

    Parameters
    ----------
    df : pandas.DataFrame
        The combined dataframe after classification and pose scoring.
    base : str
        The base stem (e.g., 'BASE_fly1') used to derive output paths.

    Notes
    -----
    - Writes only existing columns, silently dropping any missing ones.
    - Uses the canonical scored schema with 'Speed_Denoised' inserted.
    - Uses Config.path helpers for destination paths.
    - Best effort: exceptions are suppressed to avoid interrupting the session.
    """
    try:
        # Construct scored view with the canonical columns (includes Speed_Denoised)
        scored_cols = [
            "FrameIndex", "VisualStim", "Stim0", "Stim1",
            "Position_X", "Position_Y", "Speed", "Motion",
            "Speed_Denoised",
            "Layer1", "Layer1_Denoised",
            "Layer2", "Layer2_Denoised",
            "Resistant", "Resistant_Denoised",
            "Behavior", "Behavior_Denoised",
        ]
        existing_scored = [c for c in scored_cols if c in df.columns]
        if existing_scored:
            scored_view = df.loc[:, existing_scored].copy()
        else:
            scored_view = pd.DataFrame()
        dest_scored = PATH["flag_scored_path"](base)
        dest_scored.parent.mkdir(parents=True, exist_ok=True)
        BC_UTILS["write_csv_atomic"](scored_view, dest_scored, index=False)

        # Pose view (only when POSE_SCORING is enabled)
        if EXPERIMENT.get("POSE_SCORING", False):
            pose_cols = [
                "FrameIndex", "Orientation", "View", "View_X", "View_Y",
                "Head_X", "Head_Y", "Thorax_X", "Thorax_Y",
                "Abdomen_X", "Abdomen_Y", "LeftWing_X", "LeftWing_Y",
                "RightWing_X", "RightWing_Y",
            ]
            existing_pose = [c for c in pose_cols if c in df.columns]
            if existing_pose:
                pose_view = df.loc[:, existing_pose].copy()
            else:
                pose_view = pd.DataFrame()
            dest_pose = PATH["flag_pose_path"](base)
            dest_pose.parent.mkdir(parents=True, exist_ok=True)
            BC_UTILS["write_csv_atomic"](pose_view, dest_pose, index=False)
    except Exception:
        # Suppress any exceptions during flagged output saving
        pass


#%% CELL 02 — SESSION SETUP (NO REDEFINITION, NO MKDIR)
"""
Imports and light session scaffolding.
- Pull read-only registries from Config (PATH, EXPERIMENT).
- Pull package surfaces (BC_QC, BC_UTILS, BC_CLASSIFIER) — no side effects.
- Provide minimal shared imports for the runner cells (time, Path, pandas).
- Define the error codes that show Δ+N on the 'ERROR last:' line.

Rules:
- Do NOT mkdir here.
- Do NOT redefine shared globals already exported elsewhere.
- Keep this cell side-effect free; printing happens in the runner.
"""

# ---- Error-code families (kept here so runner logic stays declarative) ----
# Delta-style errors: render as Δ±N using per-file metrics.
DELTA_ERROR_CODES = {
    "wrong_stimulus_count",
    "wrong_stimulus_duration",
    "timeline_misaligned",
    "sleap_len_mismatch",
}

# Categorical errors: render with no tail (no %), just the message.
CATEGORICAL_ERROR_CODES = {
    "error_reading_file",
    "missing_sleap_file",
}

#%% CELL 02.3 — PRINT & FORMAT HELPERS (reads CSV reports)  [REPLACED]
"""
Formatting + QC helpers with strict geometry:

- Banner width: 75 (centered with '=' fill)
- Content width: 72 with INDENT="  " (2 spaces)

CSV reports
  We now read the last row from the ERROR and FLAG CSVs:
    columns = ["kind","code","file_stem","unit","delta","metrics_observed","metrics_expected"]

Delta notation
  - Delta-style errors render per-file deviation as: "Δ±N".
    (Units are implicit: counts or frames.)
  - Categorical errors render the plain message with no tail.
  - Percent tails for flags are computed from metrics_observed (walk_frac or nan_fraction),
    just like before, but now reading from the CSV row instead of parsing a TXT line.
"""

# stdlib
import re
from pathlib import Path
from typing import Optional, Tuple

# Geometry constants
BANNER_WIDTH  = 75
CONTENT_WIDTH = 72
INDENT        = "  "

def _banner(title: str) -> str:
    return f" {title} ".center(BANNER_WIDTH, "=")

def _left_ellipsize(s: str, max_len: int) -> str:
    s = str(s)
    if len(s) <= max_len:
        return s
    if max_len <= 3:
        return "." * max_len
    return "." + s[-(max_len - 3):]

# -------------------------
# Key–value line formatting
# -------------------------

def _kv_line(key: str, val: str, key_pad: int | None = None) -> str:
    if key_pad is None:
        key_pad = max(14, len(key))
    max_val_len = max(1, CONTENT_WIDTH - len(INDENT) - key_pad - 3)
    val_s = _left_ellipsize(str(val), max_val_len)
    dash_len = CONTENT_WIDTH - len(INDENT) - key_pad - 3 - len(val_s)
    if dash_len >= 2:
        return f"{INDENT}{key.ljust(key_pad)} " + ("-" * dash_len) + f"  {val_s}"
    left = f"{INDENT}{key}"
    spaces = max(2, CONTENT_WIDTH - len(left) - len(val_s))
    return left + (" " * spaces) + val_s

def _kv_line_msg(key: str, msg: str, val: str, key_pad: int | None = None) -> str:
    if key_pad is None:
        key_pad = max(14, len(key))
    prefix = f"{INDENT}{key.ljust(key_pad)} "
    max_val_len = max(1, CONTENT_WIDTH - len(prefix) - len(str(msg)) - 2)
    val_s = _left_ellipsize(str(val), max_val_len)
    dash_len = CONTENT_WIDTH - len(prefix) - len(str(msg)) - 2 - len(val_s)
    if dash_len < 0:
        msg = _left_ellipsize(str(msg), CONTENT_WIDTH - len(prefix) - 2 - len(val_s))
        dash_len = 0
    return f"{prefix}{msg}{'-' * dash_len}  {val_s}"

def _kv_line_3c(left: str, mid: str, right: str, key_pad: int | None = None) -> str:
    if key_pad is None:
        key_pad = 14
    prefix = f"{INDENT}{''.ljust(key_pad)} "
    tail   = f"{left}  ---  {mid}  ---  {right}"
    dash_len = CONTENT_WIDTH - len(prefix) - 2 - len(tail)
    if dash_len < 0:
        tail = _left_ellipsize(tail, CONTENT_WIDTH - len(prefix) - 2)
        dash_len = 0
    return f"{prefix}{'-' * dash_len}  {tail}"

# -------------------------
# Progress block
# -------------------------

def _progress_bar(i: int, total: int, sec_per_file: float) -> tuple[str, str]:
    bar_width = CONTENT_WIDTH - (len(INDENT) + len("SCORING  [") + 1)
    bar_width = max(0, bar_width)
    done = min(max(i, 0), max(total, 1))
    filled = int(round(bar_width * (0 if total <= 0 else done / total)))
    filled = min(max(filled, 0), bar_width)
    bar = "#" * filled + "." * (bar_width - filled)
    remain  = max(0, total - done)
    eta_sec = max(0.0, remain * max(sec_per_file, 0.0))
    mm, ss  = divmod(int(round(eta_sec)), 60)
    eta     = f"{mm:02d}m{ss:02d}s"
    line1 = f"{INDENT}SCORING  [{bar}]"
    right = f"file {done}/{total}  ---  {sec_per_file:.2f}s/file  ---  {eta} eta"
    indent_cols = len("SCORING  ")
    hyphens = CONTENT_WIDTH - (len(INDENT) + indent_cols + 2 + len(right))
    if hyphens < 0:
        right = _left_ellipsize(right, CONTENT_WIDTH - (len(INDENT) + indent_cols + 2))
        hyphens = 0
    line2 = f"{INDENT}{' ' * indent_cols}{'-' * hyphens}  {right}"
    return line1, line2

# -------------------------
# QC report / grid helpers (CSV)
# -------------------------

def _report_paths() -> Tuple[Path, Path]:
    """Paths to the global append-only QC CSV reports (errors, flags)."""
    err = Path(PATH["report_error_path"]())
    flg = Path(PATH["report_flag_path"]())
    return err, flg

def _read_last_csv_row(p: Path) -> Optional[dict]:
    """Return the last row of a CSV report as a dict, or None."""
    try:
        if not p.exists():
            return None
        import pandas as _pd
        df = _pd.read_csv(p, dtype=str)
        if df.shape[0] == 0:
            return None
        row = df.iloc[-1].to_dict()
        # normalize missing values to empty strings
        for k, v in list(row.items()):
            if v != v:  # NaN check
                row[k] = ""
        return row
    except Exception:
        return None

def _percent_from_row(row: Optional[dict]) -> Optional[int]:
    """Extract an integer percent from metrics_observed when present."""
    if not row:
        return None
    metrics = str(row.get("metrics_observed", "") or "")
    for key in ("walk_frac", "nan_fraction"):
        m = re.search(rf"{key}\s*[:=]\s*([0-9]*\.?[0-9]+)", metrics)
        if m:
            try:
                return int(round(100 * float(m.group(1))))
            except Exception:
                pass
    return None

_QC_CELL_INNER = 11

def _qc_cell(text: str) -> str:
    s = str(text)
    if len(s) > _QC_CELL_INNER:
        s = s[:_QC_CELL_INNER - 1] + "…" if _QC_CELL_INNER >= 2 else "…"
    return f"{s:^{_QC_CELL_INNER}}"

def _qc_value(session_text: str, global_text: str) -> str:
    sess = _qc_cell(f"{str(session_text):^7}")
    glob = _qc_cell(f"{str(global_text):^7}")
    grid = f"|{sess}|---|{glob}|"
    assert len(grid) == 29, f"QC grid must be 29 chars, got {len(grid)}"
    return grid

def _qc_row(label: str, session_count: int, global_count: int, key_pad: int) -> str:
    left_fixed = f"{INDENT}-----   "
    label_full = label
    section_dashcol = len(INDENT) + key_pad + 1
    left = left_fixed + label_full
    if len(left) < section_dashcol:
        left = left + (" " * (section_dashcol - len(left)))
    grid = _qc_value(session_count, global_count)
    dash_len = CONTENT_WIDTH - len(left) - 2 - len(grid)
    if dash_len >= 0:
        return f"{left}{'-' * dash_len}  {grid}"
    trim = -dash_len
    keep = max(len(label_full) - (trim + 1), 0)
    label_trimmed = "…" if keep <= 0 else ((label_full[:keep] + "…") if keep < len(label_full) else label_full)
    left = left_fixed + label_trimmed
    dash_len = max(CONTENT_WIDTH - len(left) - 2 - len(grid), 0)
    return f"{left}{'-' * dash_len}  {grid}"

# -------------------------
# Delta-from-threshold for ERROR 'last:' (from CSV row)
# -------------------------

def _delta_from_row(row: Optional[dict]) -> Optional[int]:
    """
    Return an integer deviation for delta-based errors using the CSV row.
    If 'delta' column is present and numeric, use it; else fall back to metrics_observed.
    Units are implicit to the check (frames or counts).
    """
    if not row:
        return None

    # Preferred path: explicit delta column
    raw = (row.get("delta") or "").strip()
    if raw != "":
        try:
            return int(round(float(raw)))
        except Exception:
            pass

    # Fallbacks (parse metrics_observed like the old path)
    metrics = str(row.get("metrics_observed", "") or "")

    def _get_float(keys: tuple[str, ...]) -> Optional[float]:
        for k in keys:
            m = re.search(rf"{re.escape(k)}\s*[:=]\s*([+-]?[0-9]*\.?[0-9]+)", metrics)
            if m:
                try:
                    return float(m.group(1))
                except Exception:
                    pass
        return None

    code = (row.get("code") or "").strip().lower()
    if code == "wrong_stimulus_count":
        exp_v = _get_float(("expected_onsets", "expected"))
        obs_v = _get_float(("observed_onsets", "observed"))
        if exp_v is not None and obs_v is not None:
            return int(round(abs(obs_v - exp_v)))
        return None

    if code == "wrong_stimulus_duration":
        exp = _get_float(("expected_duration_frames", "expected_frames"))
        tol = _get_float(("tolerance_frames", "tolerance"))
        mn  = _get_float(("min_observed_duration_frames", "min_obs_frames", "min_obs"))
        mx  = _get_float(("max_observed_duration_frames", "max_obs_frames", "max_obs"))
        if exp is None or tol is None or (mn is None and mx is None):
            return None
        worst = 0.0
        if mn is not None:
            worst = max(worst, abs(mn - exp))
        if mx is not None:
            worst = max(worst, abs(mx - exp))
        dev = max(0.0, worst - (tol or 0.0))
        return int(round(dev))

    if code == "timeline_misaligned":
        d = _get_float(("deficit_frames", "deficit"))
        return int(round(abs(d))) if d is not None else None

    if code == "sleap_len_mismatch":
        t = _get_float(("tracked_len", "tracked"))
        s = _get_float(("sleap_len", "sleap"))
        if t is not None and s is not None:
            return int(round(abs(t - s)))
        return None

    return None




#%% CELL 03 — PER-FILE CONVEYOR (DEFINED BEFORE RUNNER)
"""
Process a single tracked file end-to-end and return an outcome tag.

Stages
  03.1 Load tracked CSV
  03.2 Clean all stimulus channels
  03.3 Pre-flight QC (fatal)
  03.4 Minimal features
  03.5 Classification (full set, no "Noisy" here)
  03.6 Pose/SLEAP scoring
  03.7 Align/crop to experiment window
  03.8 Post-class QC flags (non-fatal)
  03.9 Publish Scored (atomic; apply "Noisy" if configured)
  03.10 Publish Pose (separate artifact; only if POSE_SCORING=True)

Return values
  "scored"                    — clean publish
  ("flagged", summary_codes)  — flags triggered; publish skipped (summary_codes is []|['CODE']|['multiple'])
  "error"                     — fatal pre-flight issue
"""

#%%% CELL 03.1 — LOAD TRACKED CSV (AND FULL PER-FILE CONVEYOR)
"""
Strictly load the *_tracked.csv and run the full per-file conveyor.

Additions
- If POSE_SCORING is True and a SLEAP CSV exists, perform a silent, safe
  tail-trim alignment BEFORE any QC:
    • Load sleap.csv.
    • BC_UTILS["align_tracked_sleap_lengths"](df, sleap_df).
      - On safe overlap: truncate the longer DF's tail.
      - If SLEAP was trimmed: atomically overwrite the SLEAP CSV so QC reads the new length.
      - On any overlap mismatch: log fatal 'timeline_misaligned' and bail out for this file.

Return (outcome, code_or_None, percent_or_None)
- ("scored",  None, None)                  → clean publish
- ("error",   error_code, None)            → fatal pre-flight error
- ("flagged", flag_code, trigger_percent)  → flagged; publish skipped
"""

def _process_one(tracked_path: Path) -> tuple[str, str | None, int | None]:
    # 03.1 — Load tracked CSV
    try:
        df = pd.read_csv(tracked_path)
    except Exception:
        # Fail to read tracked file → log error and copy inputs
        base = PATH["stem_without_suffix"](tracked_path.name)
        BC_QC["log_error"](base, "error_reading_file")
        # Copy tracked/sleap inputs for forensic analysis
        _copy_error_inputs_for_base(base, tracked_path)
        return ("error", "error_reading_file", None)

    base = PATH["stem_without_suffix"](tracked_path.name)

    # 03.1.a — (Optional) silent tail-trim alignment with SLEAP before QC
    if EXPERIMENT.get("POSE_SCORING", False):
        try:
            sleap_path = PATH["sleap_path"](base)
            if sleap_path.exists():
                sleap_df = pd.read_csv(sleap_path)

                # Attempt safe tail-only alignment using FrameIndex
                try:
                    df_aligned, sleap_aligned, info = BC_UTILS["align_tracked_sleap_lengths"](df, sleap_df, key="FrameIndex")
                except ValueError:
                    # Overlap mismatch or key issues → fatal timeline error
                    BC_QC["log_error"](base, "timeline_misaligned")
                    # Copy inputs for investigation
                    _copy_error_inputs_for_base(base, tracked_path)
                    return ("error", "timeline_misaligned", None)

                # Apply aligned tracked DF in-memory
                df = df_aligned

                # If SLEAP was longer, persist the trimmed copy so QC reads matching length
                if info.get("action") == "tail_trim" and int(info.get("trimmed_sleap", 0)) > 0:
                    BC_UTILS["write_csv_atomic"](sleap_aligned, sleap_path, index=False)

            # If sleap file is missing/unreadable, let QC handle the fatal later.
        except Exception:
            # Unexpected I/O here should defer to QC
            pass

    # 03.2 — Clean stimuli (in place)
    df = _clean_stimuli(df)

    # 03.3 — Pre-flight QC (fatal)
    qc_status, df = _preflight_qc(base, df)
    if qc_status == "error":
        # Determine which error fired from the last ERROR CSV row
        err_path, _ = _report_paths()
        last_err_row = _read_last_csv_row(err_path)
        code = (last_err_row or {}).get("code") or "error_reading_file"
        # Copy the raw inputs for inspection
        _copy_error_inputs_for_base(base, tracked_path)
        return ("error", code, None)

    # 03.4 — Minimal features
    df = _build_features(df)

    # 03.5 — Classification (all layers; no "Noisy" fill here)
    df = _classify_behavior(df)

    # 03.6 — Pose/SLEAP scoring (only enrichment; pre-flight already guaranteed presence/length)
    df = _score_pose(df, tracked_path)

    # 03.7 — Align/crop to experiment window
    df = _align_to_experiment(df)

    # 03.8 — Post-class QC flags (non-fatal, block publish)
    ok, flag_code, flag_pct = _postclass_flags(base, df)
    if not ok:
        # Save flagged outputs into Flag/Scored and Flag/Pose
        _save_flagged_outputs(df, base)
        return ("flagged", flag_code, flag_pct)

    # 03.9 — Publish Scored (atomic; apply "Noisy" if configured)
    outcome = _publish_scored(df, tracked_path)

    # 03.10 — Publish Pose (separate artifact; only if POSE_SCORING=True)
    _publish_pose(df, tracked_path)

    return (outcome, None, None)



#%%% CELL 03.2 — CLEAN ALL STIMULUS CHANNELS (BINARY 0/1)
"""
Clean every declared stimulus column in place using bounded run-length smoothing.

Rules
- Operates on binary channels (0 = off, 1 = on).
- Uses EXPERIMENT["NOISE_TOLERANCE"] as max run length when not provided by caller.
- Skips any declared stimulus column that is absent in df (QC will handle it later).

Note
- Detection mapping (off/on) is handled where needed by onsets/durations.
  Cleaners do not require detection; they only look for 0 and 1.
"""
def _clean_stimuli(df: pd.DataFrame) -> pd.DataFrame:
    stimuli = EXPERIMENT.get("STIMULI", {})
    for _, stim_info in stimuli.items():
        col = stim_info.get("name")
        if not col or col not in df.columns:
            continue  # missing column — QC will decide later if that's a problem

        # In-place smoothing (bounded zero-holes, bounded one-spikes)
        BC_UTILS["fill_zeros"](df, col)
        BC_UTILS["clean_ones"](df, col)

    return df


#%%% CELL 03.3 — PRE-FLIGHT QC (FATAL, FIRST-FAIL)
"""
Run pre-flight quality checks on the cleaned DataFrame.

Checks (fixed order, stop on first failure)
  1. Schema validity (required columns present).
  2. Stimulus count matches expected onsets.
  3. Stimulus pulse durations within jitter tolerance.
  4. Timeline alignment across Baseline/Stimulation/Recovery.
  5. Centroid NaN fraction under threshold.
  6. If pose scoring enabled: SLEAP/pose file presence and row count match.

Behavior
- On first failure: QC logs error artifact + report line.
- Return "error" so the session runner increments session_errors.
- If all pass, return the DataFrame unchanged.
"""
def _preflight_qc(base: str, df: pd.DataFrame) -> tuple[str, pd.DataFrame]:
    ok = BC_QC["error_check"](base, df)  # UPDATED: use unified QC error API
    if not ok:
        return "error", df
    return "ok", df


#%%% CELL 03.4 — MINIMAL FEATURES
"""
Derive canonical features from the cleaned tracked DataFrame.

Inputs (tracked.csv)
- FrameIndex (optional; if absent we synthesize from the row index)
- NormalizedCentroidX, NormalizedCentroidY  ← normalized [0,1] from tracker
- PixelChange (optional; Motion falls back to <NA> if missing)
- Cleaned stimulus columns (VisualStim, Stim0, Stim1, …) forwarded from _clean_stimuli

Outputs (added columns)
- Position_X / Position_Y (mm)  ← from NormalizedCentroidX/Y via BC_UTILS (Y is flipped to top-positive)
- Speed (mm/s)                  ← Euclidean displacement using EXPERIMENT['SEC_PER_FRAME']
- Motion                        ← binary from PixelChange (>0 → 1, ==0 → 0, NaN → <NA>)

Notes
- Do NOT read Position_X/Y prior to this step; they do not exist on input.
- Stimulus columns are left in place for downstream alignment/classification.
"""
def _build_features(df: pd.DataFrame) -> pd.DataFrame:
    # Ensure frame index column
    if "FrameIndex" not in df.columns:
        df["FrameIndex"] = df.index

    # Positions in mm from normalized centroid (tracked domain)
    if ("NormalizedCentroidX" not in df.columns) or ("NormalizedCentroidY" not in df.columns):
        # Schema preflight should have enforced presence, but guard anyway
        raise KeyError("Tracked input missing NormalizedCentroidX/NormalizedCentroidY")
    df["Position_X"] = BC_UTILS["norm_to_mm_x"](df["NormalizedCentroidX"])
    df["Position_Y"] = BC_UTILS["norm_to_mm_y"](df["NormalizedCentroidY"])

    # Speed (mm/s) — use SEC_PER_FRAME from EXPERIMENT
    df["Speed"] = BC_UTILS["compute_speed_mm_per_s"](
        df["Position_X"], df["Position_Y"], frame_span_sec=float(EXPERIMENT["SEC_PER_FRAME"])
    )

    # Motion from PixelChange (nullable Int64)
    if "PixelChange" in df.columns:
        df["Motion"] = BC_UTILS["motion_from_pixel_change"](df["PixelChange"])
    else:
        df["Motion"] = pd.Series([pd.NA] * len(df), index=df.index, dtype="Int64")

    return df



#%%% CELL 03.5 — CLASSIFICATION (FULL SET, NO “NOISY” HERE)
"""
Apply all classification stages in sequence and append results to the DataFrame.

Steps
- Layer1            → From Speed/Motion thresholds. Jump ≥ HIGH_SPEED;
                      else precedence: Freeze (no motion) > Walk ≥ LOW_SPEED > Stationary.
- Layer1_Denoised   → Deletes micro-bouts of Walk/Stationary/Freeze ≤ tolerance; Jump preserved.
- Layer2            → Window consensus (odd W). Jump override if any Jump in window;
                      ties resolved Walk > Stationary > Freeze.
- Layer2_Denoised   → Same as Layer2 but requires >50% valid frames in window (half-missing rule).
- Resistant         → For Walk/Stationary/Freeze bouts that fully cover [pre,post] stim windows;
                      priority Walk > Stationary > Freeze.
- Resistant_Denoised→ Same resistant logic but applied on Layer2_Denoised.
- Behavior          → Maps Layer2 labels to compact {Jump,Walk,Stationary,Freeze};
                      promotion rule: Freeze + Resistant_Freeze → Resistant_Freeze.
- Behavior_Denoised → Same promotion but on Layer2_Denoised + Resistant_Denoised.

Notes
- Thresholds, windows, precedence, and coverage rules live in _classifier.
- This stage does NOT apply the “Noisy” replacement; deferred to publish.
"""
def _classify_behavior(df: pd.DataFrame) -> pd.DataFrame:
    df = BC_CLASSIFIER["classify_layer1"](df)
    df = BC_CLASSIFIER["classify_layer1_denoised"](df)
    df = BC_CLASSIFIER["classify_layer2"](df)
    df = BC_CLASSIFIER["classify_layer2_denoised"](df)
    df = BC_CLASSIFIER["classify_resistant_behaviors"](df)
    df = BC_CLASSIFIER["classify_resistant_behaviors_denoised"](df)
    df = BC_CLASSIFIER["classify_behavior"](df)
    df = BC_CLASSIFIER["classify_behavior_denoised"](df)
    return df


#%%% CELL 03.6 — POSE / SLEAP SCORING (dotted schema only; vectorized)  [REPLACE THIS CELL]
"""
Augment df with pose-derived metrics (View, Orientation, keypoints) from SLEAP input.

Assumptions
- SLEAP CSV always uses the dotted schema, e.g. 'Head.Position.X', 'Left.Confidence', etc.
- Flat '*_X/*_Y' columns are created here (in millimetres), not present in the input.

Steps
1) Read SLEAP input for this base.
2) Promote dotted keypoints → flat mm columns: Head/Thorax/Abdomen/LeftWing/RightWing.
3) Vectorized view selection via Config.utils determine_view(row) → (label, x_norm, y_norm).
4) Convert view coords to mm → View_X, View_Y; keep 'View' label.
5) Compute Orientation.
6) Length-align with tracked df (defensive; preflight should already ensure equality).
7) Join a safe subset of pose columns into the combined df.
"""

from pathlib import Path

def _score_pose(df: pd.DataFrame, tracked_path: Path) -> pd.DataFrame:
    if not EXPERIMENT.get("POSE_SCORING", False):
        return df

    base = PATH["stem_without_suffix"](tracked_path.name)
    sleap_csv = PATH["sleap_path"](base)

    try:
        pose_df = pd.read_csv(sleap_csv)
    except Exception:
        # Pre-flight QC should have caught this; continue without pose columns.
        return df

    # --- 2) Promote dotted keypoints to flat mm columns ---
    keypoints = ("Head", "Thorax", "Abdomen", "LeftWing", "RightWing")
    for kp in keypoints:
        xdot = f"{kp}.Position.X"
        ydot = f"{kp}.Position.Y"
        if xdot in pose_df.columns and ydot in pose_df.columns:
            pose_df[f"{kp}_X"] = BC_UTILS["norm_to_mm_x"](pose_df[xdot])
            pose_df[f"{kp}_Y"] = BC_UTILS["norm_to_mm_y"](pose_df[ydot])

    # --- 3) Vectorized view selection over dotted schema ---
    view_df = pose_df.apply(lambda row: pd.Series(BC_UTILS["determine_view"](row)), axis=1)
    view_df.columns = ["View", "View_X_norm", "View_Y_norm"]

    # --- 4) Convert view coords to mm; drop temp norm columns ---
    pose_df["View"]   = view_df["View"]
    pose_df["View_X"] = BC_UTILS["norm_to_mm_x"](view_df["View_X_norm"])
    pose_df["View_Y"] = BC_UTILS["norm_to_mm_y"](view_df["View_Y_norm"])

    # --- 5) Orientation (best-effort; tolerate partial keypoints) ---
    try:
        pose_df["Orientation"] = BC_UTILS["compute_orientation"](pose_df)
    except Exception:
        pass  # downstream QC/flags will catch quality problems

    # --- 6) Defensive length alignment ---
    n = min(len(df), len(pose_df))
    if len(df) != len(pose_df):
        pose_df = pose_df.iloc[:n].reset_index(drop=True)
        df = df.iloc[:n].reset_index(drop=True)

    # --- 7) Join a safe set of pose columns into the tracked df ---
    join_cols = []
    for c in (
        "View", "Orientation",
        "View_X", "View_Y",
        "Head_X", "Head_Y",
        "Thorax_X", "Thorax_Y",
        "Abdomen_X", "Abdomen_Y",
        "LeftWing_X", "LeftWing_Y",
        "RightWing_X", "RightWing_Y",
    ):
        if c in pose_df.columns:
            join_cols.append(c)

    if join_cols:
        df = df.join(pose_df[join_cols], how="left")

    return df

#%%% CELL 03.7 — ALIGN/CROP TO EXPERIMENT WINDOW  [REPLACE THIS CELL]
"""
Align and crop DataFrame to the configured experiment window.

Steps
- Locate first onset of EXPERIMENT['ALIGNMENT_STIM'] (strict: CSV column must equal STIMULI[label]['name']).
- Use EXPERIMENT['EXPERIMENTAL_PERIODS']['Experiment']['duration_frames'].
- Slice DataFrame deterministically to that range.
- Optionally reset the pandas index for convenience, but DO NOT overwrite 'FrameIndex'.

Notes
- Length/coverage mismatches are enforced in pre-flight QC (03.3).
- This step only performs deterministic alignment/cropping; 'FrameIndex' values are preserved.
"""
def _align_to_experiment(df: pd.DataFrame) -> pd.DataFrame:
    # Resolve the alignment stimulus CSV column name from the registry
    stim_label = EXPERIMENT["ALIGNMENT_STIM"]
    stim_info  = EXPERIMENT["STIMULI"][stim_label]
    column_name = stim_info["name"]

    if column_name not in df.columns:
        # Preflight QC should have caught this; fail soft here to keep session going.
        return df

    series = df[column_name]

    # Strict API: provide column_name so (off,on) comes from Config.experiment.STIMULI
    onset_frames = BC_UTILS["onsets"](series, column_name=column_name)
    if len(onset_frames) == 0:
        # QC already enforced presence of onsets; be defensive.
        return df

    first_onset = int(onset_frames[0])

    periods = EXPERIMENT["EXPERIMENTAL_PERIODS"]
    baseline_frames   = int(periods["Baseline"]["duration_frames"])
    experiment_frames = int(periods["Experiment"]["duration_frames"])

    start = first_onset - baseline_frames
    stop  = start + experiment_frames

    # Clamp to dataframe bounds just in case; preflight should guarantee feasibility
    start = max(0, start)
    stop  = min(len(df), max(start, stop))

    aligned = df.iloc[start:stop].copy().reset_index(drop=True)
    return aligned


#%%% CELL 03.8 — POST-CLASS QC FLAGS (NON-FATAL, BLOCK PUBLISH)
"""
Run non-fatal QC after alignment/classification.

Behavior
- Delegates to QC: BC_QC['flag_check'](base, df) → (ok: bool, summary_codes: list[str])
    ok=True,  summary_codes=[]           → clean (no flags)
    ok=False, summary_codes=['CODE']     → exactly one flag (QC logged it; flagged CSV saved)
    ok=False, summary_codes=['multiple'] → >1 flags (QC logged them all; flagged CSV saved)

Return (ok, label_code, trigger_percent_or_None)
- label_code:
    • 'multiple' if multiple flags fired in QC summary
    • otherwise the single flag code (e.g., 'low_baseline_exploration')
- trigger_percent_or_None:
    • parsed from the last FLAG CSV row's metrics (walk_frac / nan_fraction)
    • None if not present (falls back to session % in the runner)
"""
def _postclass_flags(base: str, df: pd.DataFrame) -> tuple[bool, str | None, int | None]:
    ok, summary_codes = BC_QC["flag_check"](base, df)
    if ok:
        return True, None, None

    # Read the last FLAG CSV row to extract the latest code + trigger metric (if any)
    _, flag_path = _report_paths()
    last_flag_row = _read_last_csv_row(flag_path)
    last_code = (last_flag_row or {}).get("code", "")
    pct = _percent_from_row(last_flag_row)

    if summary_codes == ["multiple"]:
        label_code = "multiple"
    else:
        label_code = last_code or (summary_codes[0] if summary_codes else "multiple")

        # If we didn't get a percent from the CSV (e.g., categorical-style flag), try to compute here
        if pct is None and last_flag_row:
            pct = _percent_from_row(last_flag_row)

    return False, label_code, pct



#%%% CELL 03.9 — PUBLISH (ATOMIC; APPLY “NOISY” IF CONFIGURED)
"""
Publish the Scored CSV with canonical behavioral outputs.
Apply 'Noisy' fill (if configured) to classification columns, then
slice to the fixed schema (scored_cols), and write atomically.

Scored CSV (PATH['scored_path']):
  FrameIndex, VisualStim, Stim0, Stim1,
  Position_X, Position_Y, Speed, Motion,
  Layer1, Layer1_Denoised,
  Layer2, Layer2_Denoised,
  Resistant, Resistant_Denoised,
  Behavior, Behavior_Denoised

Pose CSV (PATH['pose_path']) is a separate artifact, with its own schema.
"""
def _publish_scored(df: pd.DataFrame, tracked_path: Path) -> str:
    base = PATH["stem_without_suffix"](tracked_path.name)

    # 1) Fixed schema for Scored CSV
    # Define the canonical schema for the Scored CSV. A new column
    # 'Speed_Denoised' is included between 'Speed' and 'Motion'.
    scored_cols = [
        "FrameIndex",
        "VisualStim", "Stim0", "Stim1",
        "Position_X", "Position_Y",
        "Motion",
        "Speed", "Speed_Denoised",
        "Layer1", "Layer1_Denoised",
        "Layer2", "Layer2_Denoised",
        "Resistant", "Resistant_Denoised",
        "Behavior", "Behavior_Denoised",
    ]

    # 2) Optional 'Noisy' fill
    noisy_label = (
        BC_CLASSIFIER.get("NOISY_LABEL", None)
        if isinstance(BC_CLASSIFIER, dict) else None
    )

    if noisy_label is not None:
        for col in (
            "Layer1",
            "Layer1_Denoised",
            "Layer2",
            "Layer2_Denoised",
            "Resistant",
            "Resistant_Denoised",
            "Behavior",
            "Behavior_Denoised",
        ):
            if col in df.columns:
                df[col] = df[col].fillna(noisy_label)

    # 3) Slice to scored schema (only existing cols)
    existing = [c for c in scored_cols if c in df.columns]
    out_df = df.loc[:, existing].copy()

    # 4) Atomic write
    scored_path = PATH["scored_path"](base)
    BC_UTILS["write_csv_atomic"](out_df, scored_path, index=False)

    return "scored"


#%%% CELL 03.10 — PUBLISH POSE (SEPARATE ARTIFACT)
def _publish_pose(df: pd.DataFrame, tracked_path: Path) -> None:
    if not EXPERIMENT.get("POSE_SCORING", False):
        return

    base = PATH["stem_without_suffix"](tracked_path.name)

    pose_cols = [
        "FrameIndex", "Orientation", "View", "View_X", "View_Y",
        "Head_X", "Head_Y", "Thorax_X", "Thorax_Y", "Abdomen_X", "Abdomen_Y",
        "LeftWing_X", "LeftWing_Y", "RightWing_X", "RightWing_Y",
    ]

    existing = [c for c in pose_cols if c in df.columns]
    if not existing:
        return

    out_df = df.loc[:, existing].copy()

    # Good outputs always land in BehaviorClassification/Pose
    pose_out_path = PATH["pose_path"](base)
    BC_UTILS["write_csv_atomic"](out_df, pose_out_path, index=False)


#%% CELL 04 — RUNNER (FINAL BLANK-LINE FORMATTING)  [REPLACE THIS CELL]
"""
Session runner with strict alignment.

- Banner: 75 chars
- Content lines: 72 chars, 2-space indent
- Section pads PAD1.PAD5 define the dash columns
- Progress: hyphens on the second line start under '['
- QC rows: dashed to the QC grid using _qc_row
- TOTAL row removed
- FLAGS line shows raw counts only
- Blank lines printed as true empty lines
- No final tail printing here (handled elsewhere)

Delta notation:
- Delta-style error tails show "Δ±N" from this file's metrics.
"""

from collections import defaultdict
from typing import Dict
from IPython.display import display, HTML
from html import escape
import time

def _run_session() -> dict:
    ERROR_LABELS: dict = BC_QC.get("error_labels", {})
    FLAG_LABELS:  dict = BC_QC.get("flag_labels", {})

    ERROR_ORDER = list(ERROR_LABELS.keys())
    FLAG_ORDER  = list(FLAG_LABELS.keys())
    delta_codes = DELTA_ERROR_CODES
    categorical_errors = CATEGORICAL_ERROR_CODES

    tracked_files = list(PATH["g_tracked"]())
    total_found   = len(tracked_files)

    to_process: list[Path] = []
    for t in tracked_files:
        stem = PATH["stem_without_suffix"](t.name)
        if not BC_QC["is_file_already_classified"](stem):
            to_process.append(t)

    files_to_score = len(to_process)
    files_skipping = total_found - files_to_score

    counters = {
        "scored_files": 0,
        "session_errors": 0,
        "session_flagged": 0,
        "processed": 0,
    }
    session_err_types: Dict[str, int] = defaultdict(int)
    session_flg_types: Dict[str, int] = defaultdict(int)

    last_error_code: str | None = None
    last_flag_code:  str | None = None
    last_flag_pct:   int | None = None

    t0 = time.perf_counter()

    PAD1 = len("POSE SCORING") + 1
    PAD2 = len("FILES FOUND") + 1
    PAD3 = len("SCORING") + 1
    PAD4 = len("FILES PROCESSED") + 1
    PAD5 = len("ERRORS") + 1

    print(_banner("SCORING SESSION"))
    print()
    exp_root = str(PATH["pExperimentalFolder"])
    print(_kv_line("PROCESSING",   exp_root, key_pad=PAD1))
    print(_kv_line("POSE SCORING", f"{EXPERIMENT['POSE_SCORING']}", key_pad=PAD1))
    print()
    print(_kv_line("FILES FOUND", f"{total_found}",      key_pad=PAD2))
    print(_kv_line("TO SCORE",    f"{files_to_score}",   key_pad=PAD2))
    print(_kv_line("SKIPPING",    f"{files_skipping}",   key_pad=PAD2))
    print(_kv_line_3c("scored: 0", "errors: 0", "flags: 0", key_pad=PAD2))
    print()
    print()

    progress_handle = display(HTML("<pre style='margin:0'></pre>"), display_id=True)

    err_path, flg_path = _report_paths()

    for idx, tracked_path in enumerate(to_process, start=1):
        start = time.perf_counter()
        outcome, code, flag_pct = _process_one(tracked_path)
        end = time.perf_counter()

        if outcome == "scored":
            counters["scored_files"] += 1
        elif outcome == "error":
            counters["session_errors"] += 1
            if code:
                session_err_types[code] += 1
                last_error_code = code
        elif outcome == "flagged":
            counters["session_flagged"] += 1
            if code:
                session_flg_types[code] += 1
                last_flag_code = code
                last_flag_pct  = flag_pct

        counters["processed"] += 1

        sec_per_file = max(0.0, end - start)

        line1, line2 = _progress_bar(idx, files_to_score, sec_per_file)
        scored_line = _kv_line("SCORED", f"{counters['scored_files']}", key_pad=PAD3)

        # ----- ERROR line (with 'last:' tail) — read LAST ERROR CSV row
        if counters["session_errors"] > 0 and last_error_code:
            elabel = ERROR_LABELS.get(last_error_code, last_error_code.replace("_", " "))
            last_err_row = _read_last_csv_row(err_path)

            etail: str
            if last_error_code in delta_codes:
                dval = _delta_from_row(last_err_row) if last_err_row and last_err_row.get("code") == last_error_code else None
                etail = f"{elabel} (Δ±{dval})" if dval is not None else elabel
            elif last_error_code in categorical_errors:
                etail = elabel  # plain, no percent
            else:
                # metric-style error (e.g., centroid NaNs) → per-file %
                pct = _percent_from_row(last_err_row) if last_err_row and last_err_row.get("code") == last_error_code else None
                etail = f"{elabel} ({pct}%)" if pct is not None else elabel

            error_line = _kv_line_msg("ERROR", f"last: {etail}", f"{counters['session_errors']}", key_pad=PAD3)
        else:
            error_line = _kv_line("ERROR", "0", key_pad=PAD3)

        # ----- FLAG line (with 'last:' tail) — we already stored last flag info per file
        if counters["session_flagged"] > 0 and last_flag_code:
            flabel = FLAG_LABELS.get(last_flag_code, last_flag_code.replace("_", " "))
            if last_flag_code == "multiple":
                ftail = flabel  # no percent for 'multiple'
            else:
                ftail = f"{flabel} ({last_flag_pct}%)" if last_flag_pct is not None else flabel
            flag_line = _kv_line_msg("FLAG", f"last: {ftail}", f"{counters['session_flagged']}", key_pad=PAD3)
        else:
            flag_line = _kv_line("FLAG", "0", key_pad=PAD3)

        progress_text = "\n".join((line1, line2, "", scored_line, error_line, flag_line))
        progress_handle.update(HTML(f"<pre style='margin:0'>{escape(progress_text)}</pre>"))

    print()
    print()
    print()
    print(_banner("SESSION SUMMARY"))
    print()
    print(_kv_line("FILES FOUND",     f"{total_found}",              key_pad=PAD4))
    print(_kv_line("FILES PROCESSED", f"{counters['processed']}",    key_pad=PAD4))
    print(_kv_line("FILES SCORED",    f"{counters['scored_files']}", key_pad=PAD4))
    print()
    print()
    print("  QUALITY CHECK  ------------------------  |  SESSION  |---|  GLOBAL   |")

    # --- Aggregate GLOBAL counts from CSVs ---
    import pandas as _pd

    def _accumulate_report_csv(p: Path, bucket: Dict[str, int]) -> int:
        if not p.exists():
            return 0
        try:
            df = _pd.read_csv(p, dtype=str)
        except Exception:
            return 0
        if df.empty or "code" not in df.columns:
            return 0
        counts = df["code"].value_counts()
        total = int(counts.sum())
        for code_key, cnt in counts.to_dict().items():
            bucket[code_key] += int(cnt)
        return total

    global_err_types: Dict[str, int] = defaultdict(int)
    global_flg_types: Dict[str, int] = defaultdict(int)

    global_error_total = _accumulate_report_csv(err_path, global_err_types)
    global_flag_total  = _accumulate_report_csv(flg_path, global_flg_types)

    session_error_total = counters["session_errors"]
    session_flag_total  = counters["session_flagged"]

    err_sess_pct = int(round(100 * session_error_total / max(1, counters["processed"])))
    err_glob_pct = int(round(100 * global_error_total  / max(1, total_found)))
    print(_kv_line("ERRORS",
                   _qc_value(f"{session_error_total} ({err_sess_pct}%)",
                             f"{global_error_total} ({err_glob_pct}%)"),
                   key_pad=PAD5))

    for code in ERROR_ORDER:
        label = ERROR_LABELS.get(code, code.replace("_", " "))
        sess = session_err_types.get(code, 0)
        glob = global_err_types.get(code, 0)
        print(_qc_row(label, sess, glob, key_pad=PAD5))

    print()
    print(_kv_line("FLAGS",
                   _qc_value(str(session_flag_total), str(global_flag_total)),
                   key_pad=PAD5))

    for code in FLAG_ORDER:
        label = FLAG_LABELS.get(code, code.replace("_", " "))
        sess = session_flg_types.get(code, 0)
        glob = global_flg_types.get(code, 0)
        print(_qc_row(label, sess, glob, key_pad=PAD5))

    scoring_seconds = max(0.0, time.perf_counter() - t0)
    return {
        "scoring_seconds": scoring_seconds,
        "files_scored_session": counters["scored_files"],
        "session_errors": counters["session_errors"],
        "files_processed_session": counters["processed"],
    }


#%% CELL 05 — PUBLIC SURFACE (ZERO-ARG ENTRY POINT)
"""
Expose the callable API for external callers/notebooks.

behavior_classifier_main() -> dict
  Returns the legacy-shaped payload with exact keys:
    {
      "scoring_seconds": float,
      "files_scored_session": int,
      "session_errors": int,
      "files_processed_session": int,
    }

Notes
- All orchestration and policy are handled upstream (Cells 02–04).
- This function performs no printing or file I/O beyond what the runner
  and the delegated modules already do.
"""
def behavior_classifier_main() -> dict:
    return _run_session()


#%% CELL 06 — PUBLIC SURFACE (READ-ONLY)
"""
Surface
- behavior_classifier_main() -> dict
    Zero-arg entry point that runs the full session and returns legacy-shaped payload.
    {
      "scoring_seconds": float,
      "files_scored_session": int,
      "session_errors": int,
      "files_processed_session": int,
    }

Notes
- Keeps _main orchestration private.
- Exposed via read-only MappingProxyType to prevent accidental mutation.
"""

BC_MAIN = MappingProxyType({
    "behavior_classifier_main": behavior_classifier_main,
})

__all__ = ("BC_MAIN",)
