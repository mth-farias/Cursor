#%%% CELL 00 — MODULE OVERVIEW
"""
{{COMMIT_DETAILS}}
# <github.com/MoitaLab/Repo>
# <full_commit_hash>
# <DD-MM-YYYY HH:MM:SS>

_colab.py

Purpose
	Colab adapter for the BehaviorClassifier pipeline (Mixed mode only).
	Reads canonical paths from Config.path, enforces experiment.POSE_SCORING
	(no overrides), creates /content mirrors for BehaviorClassification/{Scored,
	Pose, Error, Flag}, and batch-syncs those outputs back to Drive for
	crash-tolerant runs. This module contains no classification, thresholds,
	or QC logic.

Responsibilities
	- Discover Drive locations from PATH and present them as DrivePaths.
	- Validate required inputs on Drive according to experiment.POSE_SCORING.
	- Create local /content mirrors for outputs under BehaviorClassification/.
	- Build a read-only PATH-like namespace: inputs=Drive, outputs=/content.
	- Background sync in batches (+ final flush) from /content → Drive.
	- Print the staging endcap (75/72 banner + kv-lines) after final sync.

Non-Responsibilities
	- No scoring/QC/thresholds (lives in _main, _classifier, _qc_error_flag).
	- No mutation of Config.* policy; no input staging/copying by default.
	- The SESSION|GLOBAL table prints in _main to match legacy output exactly.

Inputs & Outputs (policy)
	Inputs  : PostProcessing/Tracked (and PostProcessing/Sleap if POSE_SCORING=True)
	Outputs : BehaviorClassification/{Scored, Pose, Error, Flag}
	(All names and suffix rules come from Config.path; this module never hardcodes.)

Public API
	load_configs(PATH_map=None) -> (drive_root, DrivePaths)
	validate_inputs(drive_paths, verbose=False) -> bool
	local_mirrors(drive_root, drive_paths, local_root=None, verbose=False) -> LocalPaths
	make_mixed_path_namespace(PATH_map, drive_paths, local_paths) -> MappingProxyType
	start_background_sync(local_paths, drive_paths, pose_scoring, batch_size=30) -> None
	stop_background_sync() -> None
	sync_outputs_back(local_paths, drive_paths, pose_scoring, verbose=True) -> None

Notes
	- Mixed-only design: inputs remain on Drive (skip-logic stays global and correct);
	  outputs land on /content for speed and get synced back in batches.
	- Crash model: at worst, fewer than <batch_size> unsynced files are lost.
	- Endcap formatting here mirrors the legacy 75/72 style; main summary stays in _main.
"""


#%% CELL 01 — IMPORTS & PACKAGE SHIM
"""
Purpose
	Import minimal, stable dependencies for the Colab adapter and ensure the
	Codes/ package is importable in notebook contexts. Follows the developer
	guide ordering: future → stdlib → typing → third-party → local.

Notes
	- Config registries (PATH, EXPERIMENT) are read-only MappingProxyType.
	- This module must not mutate Config.* or any path policy.
"""

# stdlib
import sys
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Optional, Mapping

import threading
import shutil

#%%% CELL 01.1 — PACKAGE IMPORTS (CONFIG SHIM)
"""
Ensure Codes/ is importable for absolute package imports in notebooks/Colab.
No effect when running as an installed package.
"""
ROOT = Path(__file__).resolve().parents[1]  # .../Codes
if str(ROOT) not in sys.path:
	sys.path.insert(0, str(ROOT))

# read-only registries (import exactly as requested)
from Config import PATH
from Config import EXPERIMENT



#%% CELL 02 — DATA CONTAINERS (FROZEN)
"""
Purpose
	Stable containers for Drive and Local locations. Inputs remain on Drive;
	outputs live under BehaviorClassification/ and may be mirrored to /content.

Design
	– DrivePaths mirrors canonical Config.path members actually used at run time.
	– LocalPaths mirrors only the BehaviorClassification outputs subtree.
	– Frozen dataclasses prevent accidental mutation across cells/threads.
"""

@dataclass(frozen=True)
class DrivePaths:
	"""
	Canonical locations on Google Drive (resolved from Config.path).

	Members (absolute):
		experimental_root : Path   # experiment folder root

		# INPUTS (Drive)
		tracked           : Path   # PostProcessing/Tracked/
		sleap             : Path   # PostProcessing/Sleap/  (may be absent)

		# OUTPUTS (Drive, BehaviorClassification/)
		bc_root           : Path   # BehaviorClassification/
		scored            : Path   # BehaviorClassification/Scored/
		pose              : Path   # BehaviorClassification/Pose/
		error             : Path   # BehaviorClassification/Error/
		flag              : Path   # BehaviorClassification/Flag/
	"""
	experimental_root: Path
	# inputs
	tracked: Path
	sleap: Path
	# outputs
	bc_root: Path
	scored: Path
	pose: Path
	error: Path
	flag: Path


@dataclass(frozen=True)
class LocalPaths:
	"""
	Local mirrors under /content for fast writes during the session.

	Members (absolute under /content/<exp_name>/BehaviorClassification/):
		local_root : Path  # /content/.../BehaviorClassification/
		scored     : Path  # /content/.../BehaviorClassification/Scored/
		pose       : Path  # /content/.../BehaviorClassification/Pose/
		error      : Path  # /content/.../BehaviorClassification/Error/
		flag       : Path  # /content/.../BehaviorClassification/Flag/

	Notes
		Inputs are not mirrored (keeps skip-logic + global state on Drive).
	"""
	local_root: Path
	scored: Path
	pose: Path
	error: Path
	flag: Path


#%% CELL 03 — 75/72 FORMATTING HELPERS (STAGING ENDCAP ONLY)
"""
Purpose
	Reproduce the legacy look for *staging* prints (not the SESSION summary).
	Use the same banner width (75) and content width (72). The main pipeline
	summary (SESSION|GLOBAL) prints in BehaviorClassifier/_main.py.

Public helpers (text only)
	_banner(title: str) -> str
	_kv_line(label: str, value: str, longest_label: int) -> str
	_fmt_duration_lettered(seconds: float) -> str
"""

# Shared geometry
BANNER_WIDTH: int  = 75
CONTENT_WIDTH: int = 72
INDENT: str        = "  "   # two spaces
VALUE_SEP: str     = "  "   # two spaces before/after value groups & '---'


def _truncate_left(s: str, max_len: int) -> str:
	"""
	Truncate string from the left, keeping the rightmost characters.
	If max_len <= 3, return the rightmost max_len characters without ellipsis.
	"""
	s = str(s)
	if len(s) <= max_len:
		return s
	if max_len <= 3:
		return s[-max_len:]
	return "..." + s[-(max_len - 3):]


def _banner(title: str) -> str:
	"""
	Return a centered, 75-char banner with '=' fill and a single space padding
	around the UPPERCASED title.
	"""
	t = (title or "").strip().upper()
	pad = max(BANNER_WIDTH - len(t) - 2, 0)
	left = pad // 2
	right = pad - left
	return ("=" * left) + " " + t + " " + ("=" * right)


def _fmt_duration_lettered(seconds: float) -> str:
	"""
	Return a lettered duration:
		< 1 hour  → 'MMmSSs'
		>= 1 hour → 'HHhMMm'  (minutes rounded from seconds: >=30s → +1m)
	Seconds are rounded to the nearest integer before formatting.
	"""
	s = int(round(max(seconds or 0.0, 0.0)))
	h, rem = divmod(s, 3600)
	m, sec = divmod(rem, 60)
	if h > 0:
		# Round minutes from leftover seconds
		if sec >= 30:
			m = (m + 1) % 60
			if m == 0:
				h += 1
		return f"{h:02d}h{m:02d}m"
	return f"{m:02d}m{sec:02d}s"


def _kv_line(label: str, value: str, longest_label: int) -> str:
	"""
	Build a single content row (72 chars total):
		'␣␣' + label + gap + dashes + '␣␣' + value
	where
		gap = (longest_label - len(label)) + 2   # aligns dash start
	The dash fill ends exactly 2 spaces before the (possibly truncated) value.
	"""
	label = str(label)
	value = str(value)

	# Left part: indent + label + gap to align dash start across rows
	left = INDENT + label
	gap = max(longest_label - len(label), 0) + 2
	left += " " * gap

	# Compute max width available for the value (including VALUE_SEP before it)
	max_value_len = max(CONTENT_WIDTH - len(left) - len(VALUE_SEP), 0)
	v = _truncate_left(value, max_value_len)

	# Dash fill to end exactly at CONTENT_WIDTH with VALUE_SEP before value
	dash_len = CONTENT_WIDTH - len(left) - len(VALUE_SEP) - len(v)
	if dash_len < 0:
		# Defensive: re-truncate if rounding created a negative
		v = _truncate_left(v, max_value_len + dash_len)
		dash_len = max(CONTENT_WIDTH - len(left) - len(VALUE_SEP) - len(v), 0)

	return left + ("-" * dash_len) + VALUE_SEP + v


def done_duck(i: int = 24) -> str:
	return f"""\n\n\n{' '*(i+9)}__(·)<    ,\n{' '*(i+6)}O  \\_) )   c|_|\n{' '*i}{'~'*27}"""


#%% CELL 04 — PUBLIC API: DISCOVERY
"""
load_configs(PATH_map=None) -> (drive_root: Path, drive_paths: DrivePaths)

Summary
	Resolve canonical Drive locations from Config.path and assemble DrivePaths.
	No I/O takes place here; this is pure path math based on declared policy.

Params
	PATH_map: Mapping|None
		Optional PATH-like mapping. When None, uses the imported Config.PATH.

Returns
	drive_root: Path     — the experiment root (PATH['pExperimentalFolder'])
	drive_paths: DrivePaths — absolute locations for inputs and outputs on Drive
"""

def load_configs(PATH_map: Mapping | None = None) -> tuple[Path, DrivePaths]:
	# choose the mapping: injected mapping or the imported PATH
	ns = PATH if PATH_map is None else PATH_map

	# helper: coerce to Path if needed
	def P(x) -> Path:
		return x if isinstance(x, Path) else Path(str(x))

	# required keys — fail fast with crisp messages if any is missing
	required_keys = (
		"pExperimentalFolder",
		"pTracked",
		"pSleap",  # may exist even if POSE_SCORING is False; validation happens later
		"pBehaviorClassification",
		"pScored",
		"pPose",
		"pError",
		"pFlag",
	)
	missing = [k for k in required_keys if k not in ns]
	if missing:
		m = ", ".join(missing)
		raise RuntimeError(f"Config.path is missing required keys: {m}")

	# resolve roots and subtrees
	drive_root = P(ns["pExperimentalFolder"])
	drive_paths = DrivePaths(
		experimental_root = drive_root,
		# inputs (Drive)
		tracked = P(ns["pTracked"]),
		sleap   = P(ns["pSleap"]),
		# outputs (Drive; BehaviorClassification subtree)
		bc_root = P(ns["pBehaviorClassification"]),
		scored  = P(ns["pScored"]),
		pose    = P(ns["pPose"]),
		error   = P(ns["pError"]),
		flag    = P(ns["pFlag"]),
	)

	return drive_root, drive_paths


#%% CELL 05 — PUBLIC API: VALIDATION (NO OVERRIDES)  [REPLACE THIS CELL]
"""
validate_inputs(drive_paths, verbose=False) -> bool

Summary
    Read experiment.POSE_SCORING (single source of truth). Validate that Drive
    contains required inputs: PostProcessing/Tracked/ always; PostProcessing/Sleap/
    only when POSE_SCORING is True. Return the validated POSE_SCORING value.

Params
    drive_paths: DrivePaths
    verbose: bool  — optional console hinting

Returns
    pose_scoring: bool — the value read from Config.experiment
"""

def _has_any_csv(folder: Path) -> bool:
    """Return True if 'folder' exists and contains at least one *.csv anywhere."""
    try:
        if not folder.exists():
            return False
        for _ in folder.rglob("*.csv"):
            return True
        return False
    except Exception:
        # Treat transient I/O errors as missing for conservative validation.
        return False


def validate_inputs(drive_paths: DrivePaths, *, verbose: bool = False) -> bool:
    # Read POSE_SCORING from Config.experiment (attribute or mapping-style)
    if hasattr(EXPERIMENT, "POSE_SCORING"):
        pose_scoring = bool(getattr(EXPERIMENT, "POSE_SCORING"))
    elif isinstance(EXPERIMENT, Mapping) and "POSE_SCORING" in EXPERIMENT:
        pose_scoring = bool(EXPERIMENT["POSE_SCORING"])
    else:
        raise RuntimeError(
            "EXPERIMENT.POSE_SCORING not found in Config.experiment "
            "(expected attribute or mapping key)."
        )

    # Always require tracked inputs
    if not _has_any_csv(drive_paths.tracked):
        raise RuntimeError(f"Tracked inputs not found or empty: {drive_paths.tracked}")

    # If pose scoring is enabled, require SLEAP inputs
    if pose_scoring and not _has_any_csv(drive_paths.sleap):
        raise RuntimeError(
            "POSE_SCORING=True but SLEAP inputs not found or empty: "
            f"{drive_paths.sleap}"
        )

    if verbose:
        print(f"Validation OK. pose_scoring={pose_scoring}")

    return pose_scoring



#%% CELL 06 — PUBLIC API: LOCAL MIRRORS (/content)
"""
local_mirrors(drive_root, drive_paths, local_root=None, verbose=False) -> LocalPaths

Summary
	Create an isomorphic outputs subtree under /content for fast writes:
	BehaviorClassification/{Scored, Pose, Error, Flag}. Inputs remain on Drive.

Params
	drive_root: Path
	drive_paths: DrivePaths
	local_root: Optional[Path] — base under /content; default:
	            /content/exp_runs/<experiment_name>/BehaviorClassification
	verbose: bool

Returns
	LocalPaths — absolute local mirror locations

Notes
	• Idempotent: ensures directories exist; performs no copies.
	• Inputs are not mirrored (skip-logic and global state remain on Drive).
"""

def local_mirrors(
	drive_root: Path,
	drive_paths: DrivePaths,
	local_root: Optional[Path] = None,
	*,
	verbose: bool = False
) -> LocalPaths:
	# Derive a stable namespace under /content for this experiment
	exp_name = drive_root.name or "experiment"
	default_base = Path("/content/exp_runs") / exp_name / "BehaviorClassification"
	base = Path(local_root) if local_root is not None else default_base

	# Output subtree mirrors
	local_scored = base / "Scored"
	local_pose   = base / "Pose"
	local_error  = base / "Error"
	local_flag   = base / "Flag"

	# Create directories; safe to call repeatedly
	for d in (local_scored, local_pose, local_error, local_flag):
		d.mkdir(parents=True, exist_ok=True)

	if verbose:
		print("Local output mirrors ready:")
		print(f"  Scored  -> {local_scored}")
		print(f"  Pose    -> {local_pose}")
		print(f"  Error   -> {local_error}")
		print(f"  Flag    -> {local_flag}")

	return LocalPaths(
		local_root = base,
		scored = local_scored,
		pose   = local_pose,
		error  = local_error,
		flag   = local_flag,
	)


#%% CELL 07 — PUBLIC API: MIXED PATH NAMESPACE (READ-ONLY)
"""
make_mixed_path_namespace(PATH_map, drive_paths, local_paths) -> MappingProxyType

Summary
	Build a *shadow* PATH-like mapping for the run where inputs still point to
	Drive and outputs point to /content mirrors. Does *not* mutate Config.path.

Mapping policy
	Inputs  (pTracked, pSleap, input globs/builders)     → Drive (unchanged)
	Outputs (pBehaviorClassification, pScored, pPose,
	         pError, pFlag)                               → /content mirrors

Returns
	A read-only MappingProxyType usable anywhere PATH is expected.

Notes
	• Skip-logic remains Drive-centric; only publishing writes land locally.
	• We intentionally do NOT override output globs (gScored/gPose/gError/gFlag)
	  so any skip-logic that relies on Drive remains correct and idempotent.
"""

def make_mixed_path_namespace(
	PATH_map: Mapping | None,
	drive_paths: DrivePaths,
	local_paths: LocalPaths
) -> MappingProxyType:
	# choose the mapping: injected mapping or the imported PATH
	ns = PATH if PATH_map is None else PATH_map

	# Start from the declared policy; do not mutate the original PATH
	base: dict = dict(ns)

	# Rebind only the BehaviorClassification outputs to /content mirrors
	base["pBehaviorClassification"] = local_paths.local_root
	base["pScored"] = local_paths.scored
	base["pPose"]   = local_paths.pose
	base["pError"]  = local_paths.error
	base["pFlag"]   = local_paths.flag

	# Return a read-only mapping (call sites should treat it like Config.path.PATH)
	return MappingProxyType(base)


#%% CELL 08 — PUBLIC API: BACKGROUND SYNC (BATCH PUSH)  [REPLACE THIS CELL]
"""
start_background_sync(local_paths, drive_paths, pose_scoring, batch_size=30) -> None
stop_background_sync() -> None

Summary
    Daemon loop monitors how many new local *Scored* files exist; when growth
    reaches batch_size since last push, copy BehaviorClassification/{Scored, Pose,
    Error, Flag} from /content to Drive. Stop call joins the thread.

Crash model
    At worst, < batch_size files are unsynced on crash. Everything previously
    pushed is safely on Drive. Reruns are idempotent since skip checks read Drive.

Params
    batch_size: int — throughput vs. risk dial; larger batches = fewer syncs.
"""

_sync_thread: Optional[threading.Thread] = None
_stop_event: threading.Event = threading.Event()


def start_background_sync(
    local_paths: LocalPaths,
    drive_paths: DrivePaths,
    pose_scoring: bool,
    *,
    batch_size: int = 30
) -> None:
    """Start a background thread that syncs new scored files in batches."""
    global _sync_thread, _stop_event

    # Normalize parameters
    batch_size = max(int(batch_size or 1), 1)

    # If a previous thread is running, stop it cleanly before starting a new one
    if _sync_thread is not None and _sync_thread.is_alive():
        stop_background_sync()

    _stop_event.clear()

    def _sync_loop() -> None:
        # Initialize baseline to current count so we don't immediately trigger
        try:
            last_count = sum(1 for _ in local_paths.scored.rglob("*.csv"))
        except Exception:
            last_count = 0

        while not _stop_event.is_set():
            # small sleep to avoid busy loop; tolerate transient delays
            _stop_event.wait(5.0)
            if _stop_event.is_set():
                break

            # Count local scored outputs; ignore transient errors
            try:
                current_count = sum(1 for _ in local_paths.scored.rglob("*.csv"))
            except Exception:
                continue

            # Trigger batch sync once the threshold is met
            if current_count - last_count >= batch_size:
                try:
                    # Quiet push; final endcap is printed by explicit flush in Cell 09
                    sync_outputs_back(
                        local_paths, drive_paths, pose_scoring, verbose=False, scoring_seconds=0.0
                    )
                    last_count = current_count
                except Exception:
                    # Be resilient: skip and retry on the next tick
                    continue

    # Spin the thread as a daemon so it won't block interpreter shutdown
    _sync_thread = threading.Thread(target=_sync_loop, name="bc_bg_sync", daemon=True)
    _sync_thread.start()


def stop_background_sync() -> None:
    """Stop the background sync thread and wait for it to exit."""
    global _sync_thread, _stop_event

    _stop_event.set()
    if _sync_thread is not None:
        try:
            _sync_thread.join(timeout=5.0)
        finally:
            _sync_thread = None


#%% CELL 09 — PUBLIC API: FINAL SYNC (legacy finish only)
"""
sync_outputs_back(local_paths, drive_paths, pose_scoring, *, scoring_seconds) -> None

Summary
	Mirror local /content outputs to Drive, then print the *legacy final* block:
	duck + "SCORING AND SAVING COMPLETE" + "SAVED IN DRIVE: <experiment root>" + "SESSION TIME".

Params
	local_paths      : LocalPaths
	drive_paths      : DrivePaths
	pose_scoring     : bool   # kept for signature symmetry (not used here)
	scoring_seconds  : float  # total session time in seconds (required)
"""

def _mirror_tree(src: Path, dst: Path) -> int:
	"""
	Copy all files from src to dst, preserving metadata. Creates parent dirs.
	Returns number of files copied (best-effort; ignores transient errors).
	"""
	if not src.exists():
		return 0
	count = 0
	dst.mkdir(parents=True, exist_ok=True)
	for f in src.rglob("*"):
		if not f.is_file():
			continue
		try:
			out = dst / f.relative_to(src)
			out.parent.mkdir(parents=True, exist_ok=True)
			shutil.copy2(f, out)
			count += 1
		except Exception:
			continue
	return count


def sync_outputs_back(
	local_paths: LocalPaths,
	drive_paths: DrivePaths,
	pose_scoring: bool,
	*,
	scoring_seconds: float,
) -> None:
	# Mirror each output subtree (order doesn’t matter; keep it stable)
	_mirror_tree(local_paths.scored, drive_paths.scored)
	_mirror_tree(local_paths.pose,   drive_paths.pose)
	_mirror_tree(local_paths.error,  drive_paths.error)
	_mirror_tree(local_paths.flag,   drive_paths.flag)

	# Legacy *final* finish block (identical to old notebook)
	print(done_duck())
	print(_banner("SCORING AND SAVING COMPLETE"))
	print()
	L_saved = len("SAVED IN DRIVE")
	# IMPORTANT: final block uses the *experiment root*
	print(_kv_line("SAVED IN DRIVE", str(drive_paths.experimental_root), L_saved))
	print()
	sec = max(0.0, float(scoring_seconds))
	print(_kv_line("SESSION TIME", _fmt_duration_lettered(sec), L_saved))
	print()
	print("=" * BANNER_WIDTH)



#%% CELL 10 — PUBLIC SURFACE (READ-ONLY)
"""
Expose a stable callable surface as a read-only dict, matching the project's
BC_* pattern (e.g., BC_UTILS, BC_QC, BC_MAIN).
"""

BC_COLAB = MappingProxyType({
	"load_configs":               load_configs,
	"validate_inputs":            validate_inputs,
	"local_mirrors":              local_mirrors,
	"make_mixed_path_namespace":  make_mixed_path_namespace,
	"start_background_sync":      start_background_sync,
	"stop_background_sync":       stop_background_sync,
	"sync_outputs_back":          sync_outputs_back,  # now final-print only
})

__all__ = ("BC_COLAB",)

