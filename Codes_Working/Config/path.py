#%% CELL 00 — HEADER & OVERVIEW
"""
{{COMMIT_DETAILS}}
# <github.com/YourLab/Repo>
# <commit_hash>
# <DD-MM-YYYY HH:MM:SS>

Config/path.py

Overview
	Define canonical folder tree and filename suffix policy.
	Provide pure helpers for path math, sibling derivation, glob discovery,
	and symbolic rebasing for Colab/Drive. No filesystem I/O.


Canonical layout
------------------------------------------------------------------------------------
	ExperimentalFolder/                                      (pExperimentalFolder)
	├─ Codes/                                                (pCodes)
	│  ├─ Config/                                            (pConfig)
	│  │  ├─ experiment.py        (module: Config.experiment)
	│  │  ├─ color.py             (module: Config.color)
	│  │  ├─ path.py              (module: Config.path)   ← this file
	│  │  └─ param.py             (module: Config.param)
	│  ├─ BehaviorClassifier/                                (pBehaviorClassifier)
	│  │  ├─ __init__.py
	│  │  ├─ _utils.py
	│  │  ├─ _qc_error_flag.py
	│  │  ├─ _classifier.py
	│  │  ├─ _colab.py
	│  │  └─ _main.py
	│  └─ BehaviorClassifier_Run.ipynb
	│
	├─ Bonfly/                                               (pBonfly)
	│  ├─ Bonsai/                                            (pBonsai)
	│  ├─ FlyHigher-Protocol/                                (pFlyHigherProtocol)
	│  └─ FlyHigher-Tracker/                                 (pFlyHigherTracker)
	│
	├─ RawData/                                              (pRawData)
	│  ├─ BASE.avi
	│  └─ BASE.csv
	│
	├─ PostProcessing/                                       (pPostProcessing)
	│  ├─ Tracked/       (pTracked)      → BASE_flyN_tracked.csv
	│  ├─ Sleap/         (pSleap)        → BASE_flyN_sleap.csv
	│  ├─ ArenaImage/    (pArenaImage)   → BASE_flyN_arenaimg.png
	│  ├─ FlyVideo/      (pFlyVideo)     → BASE_flyN_flyvideo.avi
	│  └─ CropVideo/     (pCropVideo)    → BASE_flyN_cropvideo.avi
	│
	└─ BehaviorClassification/                               (pBehaviorClassification)
	   ├─ Scored/      (pScored)        → BASE_flyN_scored.csv
	   ├─ Pose/        (pPose)          → BASE_flyN_pose.csv
	   ├─ Error/       (pError)
	   │  ├─ REPORT_ERROR.csv           → report_error_path()
	   │  ├─ Tracked/  (pErrorTracked)  → BASE_flyN_tracked.csv  (verbatim input copy)
	   │  └─ Pose/     (pErrorPose)     → BASE_flyN_sleap.csv    (verbatim input copy; only when POSE_SCORING=True)
	   └─ Flag/        (pFlag)
	      ├─ REPORT_FLAG.csv            → report_flag_path()
	      ├─ Scored/   (pFlagScored)    → BASE_flyN_scored.csv   (flagged outputs; folder encodes status)
	      └─ Pose/     (pFlagPose)      → BASE_flyN_pose.csv     (flagged outputs; folder encodes status)
"""


#%% CELL 01 — IMPORTS

from __future__ import annotations

"""
Purpose
	Import minimal, stable dependencies used throughout this config.
	Order mirrors other finished modules: stdlib → typing → local types.
"""

# Standard library
from pathlib import Path
from types import MappingProxyType

# Typing
from typing import Iterator


#%% CELL 02 — ROOT
"""
Define the experiment root and a lightweight join helper.
All paths in this module derive from this single root.
"""

# pExperimentalFolder = Path("{{__EXP_FOLDER__}}")  # experiment root (templated)
pExperimentalFolder = Path("/content/drive/MyDrive/1000DB")  # experiment root (canonical)


def _p(sub: str) -> Path:
	"""
	Join a subpath under the experiment root.

	Args:
		sub: Folder or file path relative to the experiment root.

	Returns:
		Path: The joined path under pExperimentalFolder.
	"""
	return pExperimentalFolder / sub


#%% CELL 03 — FOLDER MAP (PACKAGES & OUTPUTS)
"""
Declare canonical subfolders under the single experiment root.
Pure path math; no I/O. All variables here are Path objects.
Folders may not exist until created by downstream code (Config never writes).
"""


# CODES
pCodes = _p("Codes")  # Codes/

# Config package
pConfig = pCodes / "Config"  # Codes/Config/
# (module files shown for orientation; paths point to folders)
#   experiment.py, color.py, path.py, param.py

# BehaviorClassifier package (source code)
pBehaviorClassifier = pCodes / "BehaviorClassifier"  # Codes/BehaviorClassifier/
#   __init__.py, _utils.py, _qc_error_flag.py, _classifier.py, _colab.py, _main.py

# Notebook entry point (for convenience; not used programmatically here)
pBehaviorClassifierRun = pCodes / "BehaviorClassifier_Run.ipynb"  # Codes/BehaviorClassifier_Run.ipynb



# BONFLY
pBonfly = _p("Bonfly")  # Bonfly/
pBonsai = pBonfly / "Bonsai"  # Bonfly/Bonsai/
pFlyHigherProtocol = pBonfly / "FlyHigher-Protocol"  # Bonfly/FlyHigher-Protocol/
pFlyHigherTracker = pBonfly / "FlyHigher-Tracker"  # Bonfly/FlyHigher-Tracker/



# RAW DATA
pRawData = _p("RawData")  # RawData/
#   BASE.avi, BASE.csv



# POSTPROCESSING (DERIVED INTERMEDIATES)
pPostProcessing = _p("PostProcessing")  # PostProcessing/

pTracked = pPostProcessing / "Tracked"  # PostProcessing/Tracked/           → BASE_flyN_tracked.csv
pSleap = pPostProcessing / "Sleap"  # PostProcessing/Sleap/                 → BASE_flyN_sleap.csv
pArenaImage = pPostProcessing / "ArenaImage"  # PostProcessing/ArenaImage/  → BASE_flyN_arenaimg.png
pFlyVideo = pPostProcessing / "FlyVideo"  # PostProcessing/FlyVideo/        → BASE_flyN_flyvideo.avi
pCropVideo = pPostProcessing / "CropVideo"  # PostProcessing/CropVideo/     → BASE_flyN_cropvideo.avi



# BEHAVIORCLASSIFICATION (PUBLISHED OUTPUTS)
pBehaviorClassification = _p("BehaviorClassification")  # BehaviorClassification/

pScored = pBehaviorClassification / "Scored"  # BehaviorClassification/Scored/   → BASE_flyN_scored.csv
pPose = pBehaviorClassification / "Pose"  # BehaviorClassification/Pose/         → BASE_flyN_pose.csv

# QC: errors (verbatim copies + report)
pError = pBehaviorClassification / "Error"  # BehaviorClassification/Error/
pErrorTracked = pError / "Tracked"  # BehaviorClassification/Error/Tracked/ → BASE_flyN_tracked.csv (verbatim)
pErrorPose = pError / "Pose"  # BehaviorClassification/Error/Pose/         → BASE_flyN_sleap.csv (verbatim; when POSE_SCORING=True)

# QC: flags (flagged outputs + report)
pFlag = pBehaviorClassification / "Flag"  # BehaviorClassification/Flag/
pFlagScored = pFlag / "Scored"  # BehaviorClassification/Flag/Scored/      → BASE_flyN_scored.csv (flagged)
pFlagPose = pFlag / "Pose"  # BehaviorClassification/Flag/Pose/            → BASE_flyN_pose.csv   (flagged)


#%% CELL 04 — FILE SUFFIX POLICY
"""
Define canonical filename suffixes for all data products.
These suffixes are used to generate and parse filenames consistently.
"""

# FILE SUFFIXES
TRACKED_SUFFIX = "_tracked.csv"  # tracked data
SLEAP_SUFFIX = "_sleap.csv"      # sleap body-parts data
SCORED_SUFFIX = "_scored.csv"    # behavior classification
POSE_SUFFIX = "_pose.csv"        # derived pose

KNOWN_SUFFIXES = [
	TRACKED_SUFFIX,
	SLEAP_SUFFIX,
	SCORED_SUFFIX,
	POSE_SUFFIX,
    ]

# Validate uniqueness (fail fast)
if len(set(KNOWN_SUFFIXES)) != len(KNOWN_SUFFIXES):
	raise ValueError("Duplicate filename suffix detected in KNOWN_SUFFIXES")


#%% CELL 05 — NAME & PATH HELPERS
"""
Helpers for deriving canonical names and sibling paths.
All functions here are pure (no filesystem I/O).
"""

def stem_without_suffix(path: Path) -> str:
	"""
	Return the canonical stem of a file by removing a known suffix.

	Args:
		path: Input file path.

	Returns:
		str: Stem of the file with a known canonical suffix removed.

	Raises:
		ValueError: If the filename does not end with a known canonical suffix.

	Notes:
		- This is strict: only KNOWN_SUFFIXES are allowed.
	"""
	name = path.name
	known = ", ".join(KNOWN_SUFFIXES)
	for suf in KNOWN_SUFFIXES:
		if name.endswith(suf):
			return name[: -len(suf)]

	raise ValueError(
		f"Filename '{name}' does not end with a known suffix. "
		f"Expected one of: {known}"
        )


def siblings(path: Path) -> dict[str, Path]:
	"""
	Generate sibling file paths using canonical suffixes **in the same directory**.

	Args:
		path: Input file path.

	Returns:
		dict[str, Path]: Mapping from logical name to sibling path.
			- 'tracked'/'sleap'/'scored'/'pose': Path objects with the suffix swapped.

	Notes:
		- Parent directory of the input is preserved.
		- QC destinations (Error/Flag trees) are **not** included here; use the
		  explicit helper functions below (error_tracked_dest, error_pose_dest,
		  flag_scored_dest, flag_pose_dest) to route to canonical QC folders.
	"""
	stem = stem_without_suffix(path)  # strict canonical stem
	parent = path.parent  # keep siblings in the same directory

	# Direct siblings with canonical suffixes
	return {
		"tracked": parent / f"{stem}{TRACKED_SUFFIX}",  # tracked data
		"sleap": parent / f"{stem}{SLEAP_SUFFIX}",      # sleap body-parts data
		"scored": parent / f"{stem}{SCORED_SUFFIX}",    # behavior classification
		"pose": parent / f"{stem}{POSE_SUFFIX}",        # derived pose
        }


def error_tracked_dest(src_tracked: Path) -> Path:
	"""
	Route a tracked CSV (source) to the canonical Error/Tracked destination.

	Args:
		src_tracked: Path to the original tracked CSV (any location).

	Returns:
		Path: BehaviorClassification/Error/Tracked/<basename>.
	"""
	return pErrorTracked / src_tracked.name


def error_pose_dest(src_sleap: Path) -> Path:
	"""
	Route a SLEAP CSV (source) to the canonical Error/Pose destination.

	Args:
		src_sleap: Path to the original SLEAP CSV (any location).

	Returns:
		Path: BehaviorClassification/Error/Pose/<basename>.
	"""
	return pErrorPose / src_sleap.name


def flag_scored_dest(src_scored: Path) -> Path:
	"""
	Route a scored CSV (source) to the canonical Flag/Scored destination.

	Args:
		src_scored: Path to the original scored CSV (any location).

	Returns:
		Path: BehaviorClassification/Flag/Scored/<basename>.
	"""
	return pFlagScored / src_scored.name


def flag_pose_dest(src_pose: Path) -> Path:
	"""
	Route a pose CSV (source) to the canonical Flag/Pose destination.

	Args:
		src_pose: Path to the original pose CSV (any location).

	Returns:
		Path: BehaviorClassification/Flag/Pose/<basename>.
	"""
	return pFlagPose / src_pose.name


#%% CELL 06 — DISCOVERY (GLOBS)
"""
Glob helpers for canonical products.
Pure path math; no filesystem I/O beyond globbing.
All functions return sorted lists of Path for deterministic behavior.
"""

def g_tracked(folder: Path = pTracked) -> list[Path]:
	"""
	List tracked files.

	Args:
		folder: Folder to search (defaults to pTracked).

	Returns:
		list[Path]: Sorted list of tracked CSVs.
	"""
	return sorted(folder.glob(f"*{TRACKED_SUFFIX}"))


def g_sleap(folder: Path = pSleap) -> list[Path]:
	"""
	List SLEAP body-parts files.

	Args:
		folder: Folder to search (defaults to pSleap).

	Returns:
		list[Path]: Sorted list of SLEAP CSVs.
	"""
	return sorted(folder.glob(f"*{SLEAP_SUFFIX}"))


def g_scored(folder: Path = pScored) -> list[Path]:
	"""
	List scored behavior files.

	Args:
		folder: Folder to search (defaults to pScored).

	Returns:
		list[Path]: Sorted list of scored CSVs.
	"""
	return sorted(folder.glob(f"*{SCORED_SUFFIX}"))


def g_pose(folder: Path = pPose) -> list[Path]:
	"""
	List derived pose files.

	Args:
		folder: Folder to search (defaults to pPose).

	Returns:
		list[Path]: Sorted list of pose CSVs.
	"""
	return sorted(folder.glob(f"*{POSE_SUFFIX}"))


#%% CELL 07 — TEMP NAMES & ROOT REBASE
"""
Helpers for atomic write temp names and symbolic rebasing of the tree.
Pure path math; no filesystem resolution or touching disk.
"""

def temp_path(path: Path, tag: str = "tmp") -> Path:
	"""
	Return a deterministic temporary path alongside the target file.

	Args:
		path: Target path (final destination file).
		tag: Suffix tag to append as an extra extension (default: "tmp").

	Returns:
		Path: A sibling path with an extra extension appended (e.g., ".tmp").

	Notes:
		- Example: 'BASE_fly1_scored.csv' → 'BASE_fly1_scored.csv.tmp'
		- Keep temp files in the same directory to allow atomic replace patterns.
	"""
	# Append ".<tag>" to the existing extension chain (e.g., ".csv.tmp")
	return path.with_suffix(path.suffix + f".{tag}")


def _rebase_path(old_root: Path, new_root: Path, p: Path) -> Path:
	"""
	Symbolically map a path from one root to another, preserving structure.

	Args:
		old_root: The current experiment root (pExperimentalFolder).
		new_root: The desired experiment root to rebase into.
		p: A path under old_root.

	Returns:
		Path: The same relative path under new_root.

	Raises:
		ValueError: If 'p' is not under 'old_root'.

	Notes:
		- This is strictly symbolic; it does not touch the filesystem.
		- Uses Path.relative_to(...) to fail fast when 'p' is outside 'old_root'.
	"""
	rel = p.relative_to(old_root)  # fails if p is not under old_root
	return new_root / rel


# Keys eligible for rebasing — update if new top-level paths are added
_REBASE_KEYS = [
	# roots
	"pExperimentalFolder",
	"pCodes",
	"pConfig",
	"pBehaviorClassifier",
	"pBehaviorClassifierRun",
	# bonfly stack
	"pBonfly",
	"pBonsai",
	"pFlyHigherProtocol",
	"pFlyHigherTracker",
	# raw data
	"pRawData",
	# postprocessing
	"pPostProcessing",
	"pTracked",
	"pSleap",
	"pArenaImage",
	"pFlyVideo",
	"pCropVideo",
	# published outputs
	"pBehaviorClassification",
	"pScored",
	"pPose",
	"pError",
	"pErrorTracked",
	"pErrorPose",
	"pFlag",
	"pFlagScored",
	"pFlagPose",
    ]


def with_root(new_root: Path) -> dict[str, Path]:
	"""
	Return a shallow mapping of rebased paths for notebook/Colab sessions.

	Args:
		new_root: The experiment root to adopt for this session.

	Returns:
		dict[str, Path]: A mapping limited to _REBASE_KEYS where each path is
			rebased from the current pExperimentalFolder to 'new_root'.

	Raises:
		ValueError: If any path to be rebased is not under pExperimentalFolder.

	Notes:
		- This does not mutate globals. The caller can choose to use the returned
		  mapping directly or to install it into a session-local namespace.
		- Keep Config as the SSOT; do not reassign module globals in notebooks.
	"""
	old_root = pExperimentalFolder
	rebased: dict[str, Path] = {}
	for key in _REBASE_KEYS:
		# Fetch the current Path object from module globals
		current = globals()[key]
		# Rebase symbolically; fail fast if a path is outside old_root
		rebased[key] = _rebase_path(old_root, new_root, current)
	return rebased


#%% CELL 08 — PUBLIC API
"""
Expose a single immutable public bundle (PATH).
No other globals are part of the public surface.
"""

_PUBLIC: dict[str, object] = {
	# ROOT
	"pExperimentalFolder": pExperimentalFolder,

	# CODES
	"pCodes": pCodes,
	"pConfig": pConfig,
	"pBehaviorClassifier": pBehaviorClassifier,
	"pBehaviorClassifierRun": pBehaviorClassifierRun,

	# BONFLY
	"pBonfly": pBonfly,
	"pBonsai": pBonsai,
	"pFlyHigherProtocol": pFlyHigherProtocol,
	"pFlyHigherTracker": pFlyHigherTracker,

	# RAW DATA
	"pRawData": pRawData,

	# POSTPROCESSING
	"pPostProcessing": pPostProcessing,
	"pTracked": pTracked,
	"pSleap": pSleap,
	"pArenaImage": pArenaImage,
	"pFlyVideo": pFlyVideo,
	"pCropVideo": pCropVideo,

	# BEHAVIORCLASSIFICATION
	"pBehaviorClassification": pBehaviorClassification,
	"pScored": pScored,
	"pPose": pPose,

	# QC SUBTREES
	"pError": pError,
	"pErrorTracked": pErrorTracked,
	"pErrorPose": pErrorPose,
	"pFlag": pFlag,
	"pFlagScored": pFlagScored,
	"pFlagPose": pFlagPose,

	# FILE SUFFIX POLICY
	"TRACKED_SUFFIX": TRACKED_SUFFIX,
	"SLEAP_SUFFIX": SLEAP_SUFFIX,
	"SCORED_SUFFIX": SCORED_SUFFIX,
	"POSE_SUFFIX": POSE_SUFFIX,
	"KNOWN_SUFFIXES": tuple(KNOWN_SUFFIXES),  # immutable view

	# NAME & PATH HELPERS
	"stem_without_suffix": stem_without_suffix,
	"siblings": siblings,

	# QC DESTINATION HELPERS (canonical routing)
	"error_tracked_dest": error_tracked_dest,
	"error_pose_dest": error_pose_dest,
	"flag_scored_dest": flag_scored_dest,
	"flag_pose_dest": flag_pose_dest,

	# DISCOVERY (GLOBS)
	"g_tracked": g_tracked,
	"g_sleap": g_sleap,
	"g_scored": g_scored,
	"g_pose": g_pose,

	# TEMP & REBASE
	"temp_path": temp_path,
	"with_root": with_root,  # returns a shallow mapping of rebased paths
    }


PATH = MappingProxyType(_PUBLIC)
__all__ = ["PATH"]


#%% CELL 09 — DIAGNOSTICS & REPORT
"""
Lightweight diagnostics and a console summary for humans.
This cell must only *consume* PATH; no side effects beyond printing.
"""

def _count(glob_iter: Iterator[Path]) -> int:
	"""
	Count matches from a Path.glob iterator without materializing the list.

	Args:
		glob_iter: An iterator of Paths, typically from Path.glob.

	Returns:
		int: Number of matches.
	"""
	n = 0
	for _ in glob_iter:
		n += 1
	return n


def sanity_checks() -> None:
	"""
	Fail fast on common configuration mistakes.

	Raises:
		ValueError: If BehaviorClassifier (code) collides with BehaviorClassification (outputs),
			or if rebase-eligible keys are missing from PATH.
	"""
	# Distinguish package (code) vs outputs (results)
	code_dir = PATH["pBehaviorClassifier"]
	out_dir = PATH["pBehaviorClassification"]
	if code_dir == out_dir:
		raise ValueError(
			"Folder collision: pBehaviorClassifier and pBehaviorClassification must be different."
            )

	# Ensure all rebase-eligible keys are exposed via PATH
	required = {
		"pExperimentalFolder", "pCodes", "pConfig", "pBehaviorClassifier", "pBehaviorClassifierRun",
		"pBonfly", "pBonsai", "pFlyHigherProtocol", "pFlyHigherTracker",
		"pRawData",
		"pPostProcessing", "pTracked", "pSleap", "pArenaImage", "pFlyVideo", "pCropVideo",
		"pBehaviorClassification", "pScored", "pPose",
		"pError", "pErrorTracked", "pErrorPose",
		"pFlag", "pFlagScored", "pFlagPose",
	}
	missing = sorted(k for k in required if k not in PATH)
	if missing:
		raise ValueError(f"Missing PATH entries (rebase coverage): {', '.join(missing)}")


def demo() -> None:
	"""
	Print a compact summary of key folders and counts for quick sanity checks.
	"""
	print("=== PATH summary ===")
	for k in (
		"pTracked", "pSleap", "pScored", "pPose",
		"pErrorTracked", "pErrorPose", "pFlagScored", "pFlagPose",
        ):
		print(f"{k:16s} : {PATH[k]}")

	print()
	print("=== Discovery counts ===")
	counts = {
		"tracked": _count(PATH["g_tracked"]()),
		"sleap": _count(PATH["g_sleap"]()),
		"scored": _count(PATH["g_scored"]()),
		"pose": _count(PATH["g_pose"]()),
        }
	for k in ("tracked", "sleap", "scored", "pose"):
		print(f"{k:8s} : {counts[k]}")
	print()

	print("=== Sanity checks ===")
	try:
		sanity_checks()
		print("OK: folder separation and rebase coverage look good.")
	except Exception as e:
		print(f"FAIL: {e}")


if __name__ == "__main__":
	demo()
