#%% CELL 00 — HEADER & SCOPE
'''
{{COMMIT_DETAILS}}
#<github.com/MoitaLab/Repo>
#<full_commit_hash>
#<DD-MM-YYYY HH:MM:SS>

path.py

Overview:
  Canonical experiment folder map and filename API.
  - Declares experiment folder tree (see layout below).
  - Centralizes filename suffix policy (tracked, sleap, scored, pose, media).
  - Provides helpers to derive related filenames and glob discovery.
  - NO filesystem I/O here — pure path math for easy testing.

Design:
  - Single source of truth for folder names and file suffixes.
  - Keep code packages separate from generated outputs.
  - Stable names (constants):
      • pExperimentalFolder          → experiment root
      • pCodes                       → Codes/ (importable source root)
      • pConfig                      → Codes/Config/ (Config package)
      • pBehaviorClassifier          → Codes/BehaviorClassifier/ (package)
      • pBonfly                      → Bonfly/ (bonsai + protocols + tracker)
      • pRawData                     → RawData/ (acquisition data)
      • pPostProcessing              → PostProcessing/ (tracker/pose outputs)
      • pBehaviorClassification      → BehaviorClassification/ (outputs root)
      • pTracked, pSleap, pArenaImage, pFlyVideo, pCropVideo
      • pScored, pPose
      • pError, pErrorTracked, pErrorPose, report_error_path()
      • pFlag,  pFlagScored,  pFlagPose,  report_flag_path()

Canonically expected layout (constants in parentheses)
----------------------------------------------------------------
ExperimentalFolder/                                          (pExperimentalFolder)
├─ Codes/                                                    (pCodes)
│  ├─ Config/                                                (pConfig)
│  │  ├─ experiment.py        (module: Config.experiment)
│  │  ├─ color.py             (module: Config.color)
│  │  ├─ path.py              (module: Config.path)      ← this file
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
├─ Bonfly/                                                   (pBonfly)
│  ├─ Bonsai/                                                (pBonsai)
│  ├─ FlyHigher-Protocol/                                    (pFlyHigherProtocol)
│  └─ FlyHigher-Tracker/                                     (pFlyHigherTracker)
│
├─ RawData/                                                  (pRawData)
│  ├─ BASE.avi
│  └─ BASE.csv
│
├─ PostProcessing/                                           (pPostProcessing)
│  ├─ Tracked/         (pTracked)      → BASE_flyN_tracked.csv
│  ├─ Sleap/           (pSleap)        → BASE_flyN_sleap.csv
│  ├─ ArenaImage/      (pArenaImage)   → BASE_flyN_arenaimg.png
│  ├─ FlyVideo/        (pFlyVideo)     → BASE_flyN_flyvideo.avi
│  └─ CropVideo/       (pCropVideo)    → BASE_flyN_cropvideo.avi
│
└─ BehaviorClassification/                                   (pBehaviorClassification)
   ├─ Scored/        (pScored)        → BASE_flyN_scored.csv
   ├─ Pose/          (pPose)          → BASE_flyN_pose.csv
   ├─ Error/         (pError)
   │  ├─ REPORT_ERROR.csv             → report_error_path()
   │  ├─ Tracked/    (pErrorTracked)  → BASE_flyN_tracked.csv  (verbatim input copy)
   │  └─ Pose/       (pErrorPose)     → BASE_flyN_sleap.csv    (verbatim input copy; only when POSE_SCORING=True)
   └─ Flag/          (pFlag)
      ├─ REPORT_FLAG.csv              → report_flag_path()
      ├─ Scored/     (pFlagScored)    → BASE_flyN_scored.csv   (flagged outputs; folder encodes status)
      └─ Pose/       (pFlagPose)      → BASE_flyN_pose.csv     (flagged outputs; folder encodes status)

Legacy (deprecated; still exported for compatibility)
  - Variable-suffix artifacts under Error/ and Flag/ (e.g., *_error_<CODE>.csv, *_flag_<CODE>.csv).
    New code SHOULD NOT produce these; they remain discoverable for historical runs.
'''



#%% CELL 01 — IMPORTS
"""
Import minimal, stable dependencies used throughout this config.
"""
from pathlib import Path
from typing import Iterable, Callable
from types import MappingProxyType

#%% CELL 02 — ROOT
"""
Define the experiment root and a lightweight join helper.
All paths in this module derive from this single root.
"""
#pExperimentalFolder = Path("{{__EXP_FOLDER__}}")  # experiment root (templated)
pExperimentalFolder = Path("/content/drive/MyDrive/1000DB")  # experiment root (templated)


def _p(sub: str) -> Path:
	"""Join a subpath under the experiment root (no filesystem access)."""
	return pExperimentalFolder / sub


#%% CELL 03 — FOLDER MAP (PACKAGES vs OUTPUTS)
"""
Declare canonical subfolders that mirror the tree in CELL 00.
Each constant points to a folder; logic files should import these.
"""

from pathlib import Path

# Codes/ (importable packages)
pCodes                       = _p("Codes")                         # repo source root
pConfig                      = pCodes / "Config"                   # Config package
pBehaviorClassifier   = pCodes / "BehaviorClassifier"              # Classification package (renamed from BehaviorClassifier)

# Bonfly/ (aux repos & tooling)
pBonfly                      = _p("Bonfly")                        # bonsai + protocols + tracker
pBonsai                      = pBonfly / "Bonsai"                  # portable bonsai
pFlyHigherProtocol           = pBonfly / "FlyHigher-Protocol"      # experimental protocols
pFlyHigherTracker            = pBonfly / "FlyHigher-Tracker"       # tracking modules

# RawData/ (acquisition)
pRawData                     = _p("RawData")

# PostProcessing/ (tracker & pose outputs)
pPostProcessing              = _p("PostProcessing")
pTracked                     = pPostProcessing / "Tracked"         # *_tracked.csv
pSleap                       = pPostProcessing / "Sleap"           # *_sleap.csv
pArenaImage                  = pPostProcessing / "ArenaImage"      # *_arenaimg.png
pFlyVideo                    = pPostProcessing / "FlyVideo"        # *_flyvideo.avi
pCropVideo                   = pPostProcessing / "CropVideo"       # *_cropvideo.avi

# BehaviorClassification/ (outputs root — NOT a Python package)
pBehaviorClassification      = _p("BehaviorClassification")

# Good outputs
pScored                      = pBehaviorClassification / "Scored"      # *_scored.csv
pPose                        = pBehaviorClassification / "Pose"        # *_pose.csv

# Error (reports + verbatim input copies)
pError                       = pBehaviorClassification / "Error"
pErrorTracked                = pError / "Tracked"                       # input copies (tracked)
pErrorPose                   = pError / "Pose"                          # input copies (sleap)

# Flag (reports + flagged outputs in subfolders)
pFlag                        = pBehaviorClassification / "Flag"
pFlagScored                  = pFlag / "Scored"                         # flagged *_scored.csv
pFlagPose                    = pFlag / "Pose"                           # flagged *_pose.csv


#%% CELL 04 — FILENAME SUFFIX POLICY
"""
Centralize all filename suffixes used across artifacts.
These are appended to a base stem like 'BASE_flyN'.
"""

# Fixed per-fly artifact suffixes (discoverable on disk)
SUFFIX_TRACKED: str    = "_tracked.csv"     # per-fly tracked trajectories
SUFFIX_SLEAP: str      = "_sleap.csv"       # per-fly raw pose point estimates
SUFFIX_ARENAIMG: str   = "_arenaimg.png"    # per-fly arena snapshot
SUFFIX_FLYVIDEO: str   = "_flyvideo.avi"    # per-fly arena video
SUFFIX_CROPVIDEO: str  = "_cropvideo.avi"   # per-fly cropped video

SUFFIX_SCORED: str     = "_scored.csv"      # per-fly behavior labels
SUFFIX_POSE: str       = "_pose.csv"        # per-fly pose labels

# Report filenames (fixed) — CSV only
REPORT_ERROR_NAME: str = "REPORT_ERROR.csv"
REPORT_FLAG_NAME: str  = "REPORT_FLAG.csv"

# Ordered list of known fixed suffixes (used by stem_without_suffix and finders)
KNOWN_SUFFIXES: tuple[str, ...] = (
    SUFFIX_TRACKED,
    SUFFIX_SLEAP,
    SUFFIX_ARENAIMG,
    SUFFIX_FLYVIDEO,
    SUFFIX_CROPVIDEO,
    SUFFIX_SCORED,
    SUFFIX_POSE,
)


#%% CELL 05 — NAME & PATH HELPERS
"""
Build/transform filenames following the suffix policy and construct
their canonical Paths. Keep logic free of string literals.

Conventions
- "base" means a stem like 'BASE_flyN' (no policy suffix).
- *_name → string; *_path → Path under canonical folders.
"""

from pathlib import Path

# --- name builders (strings) ---
def stem_without_suffix(filename: str) -> str:
    """
    Return the base stem without any known policy suffix.
    Example: 'BASE_fly3_tracked.csv' → 'BASE_fly3'
    """
    name = Path(filename).name
    for suf in KNOWN_SUFFIXES:
        if name.endswith(suf):
            return name[: -len(suf)]
    return Path(name).stem  # if no policy suffix matches

def tracked_name(base: str)   -> str: return f"{base}{SUFFIX_TRACKED}"
def sleap_name(base: str)     -> str: return f"{base}{SUFFIX_SLEAP}"
def scored_name(base: str)    -> str: return f"{base}{SUFFIX_SCORED}"
def pose_name(base: str)      -> str: return f"{base}{SUFFIX_POSE}"
def arenaimg_name(base: str)  -> str: return f"{base}{SUFFIX_ARENAIMG}"
def flyvideo_name(base: str)  -> str: return f"{base}{SUFFIX_FLYVIDEO}"
def cropvideo_name(base: str) -> str: return f"{base}{SUFFIX_CROPVIDEO}"


# --- path builders (canonical locations) ---
def tracked_path(base: str)   -> Path: return pTracked / tracked_name(base)
def sleap_path(base: str)     -> Path: return pSleap   / sleap_name(base)
def scored_path(base: str)    -> Path: return pScored  / scored_name(base)
def pose_path(base: str)      -> Path: return pPose    / pose_name(base)
def arenaimg_path(base: str)  -> Path: return pArenaImage / arenaimg_name(base)
def flyvideo_path(base: str)  -> Path: return pFlyVideo   / flyvideo_name(base)
def cropvideo_path(base: str) -> Path: return pCropVideo  / cropvideo_name(base)

# New: report files
def report_error_path() -> Path: return pError / REPORT_ERROR_NAME
def report_flag_path()  -> Path: return pFlag  / REPORT_FLAG_NAME

# New: flagged outputs (folder-encoded; filenames identical to good outputs)
def flag_scored_path(base: str) -> Path: return pFlagScored / scored_name(base)
def flag_pose_path(base: str)   -> Path: return pFlagPose   / pose_name(base)

# New: error input copies (verbatim filenames)
def error_tracked_copy_path(original_filename: str) -> Path:
    """
    Copy of the tracked input under Error/Tracked with the same filename.
    Pass the original filename (e.g., 'BASE_flyN_tracked.csv').
    """
    return pErrorTracked / Path(original_filename).name

def error_pose_copy_path(original_filename: str) -> Path:
    """
    Copy of the sleap input under Error/Pose with the same filename.
    Pass the original filename (e.g., 'BASE_flyN_sleap.csv').
    """
    return pErrorPose / Path(original_filename).name


# --- transforms ---
def swap_suffix(filename: str, to_suffix: str) -> str:
    """
    Replace any known policy suffix with `to_suffix`.
    If none matches, append `to_suffix` to the stem.
    """
    base = stem_without_suffix(filename)
    return f"{base}{to_suffix}"

def parse_base_fly(stem: str) -> tuple[str, int | None]:
    """
    Parse a 'BASE_flyN' stem into (BASE, N).
    Returns (stem, None) if the pattern doesn't contain a fly suffix.
    """
    s = Path(stem).stem
    if "_fly" in s:
        head, tail = s.rsplit("_fly", 1)
        try:
            return head, int(tail)
        except ValueError:
            return s, None
    return s, None

# --- siblings resolver ---
def siblings(from_path: Path | str) -> dict[str, Path | Callable[[str], Path]]:
    """
    For any policy filename or stem, return all canonical sibling paths.

    Returns keys:
      base, tracked, sleap, scored, pose, arenaimg, flyvideo, cropvideo,
      flag_scored, flag_pose,
      error_tracked_copy, error_pose_copy,
      (legacy: error(code), flag(code))
    """
    name = Path(from_path).name
    base = stem_without_suffix(name)
    return {
        "base": base,
        "tracked": tracked_path(base),
        "sleap": sleap_path(base),
        "scored": scored_path(base),
        "pose": pose_path(base),
        "arenaimg": arenaimg_path(base),
        "flyvideo": flyvideo_path(base),
        "cropvideo": cropvideo_path(base),
        "flag_scored": flag_scored_path(base),
        "flag_pose": flag_pose_path(base),
        "error_tracked_copy": (lambda orig=name: error_tracked_copy_path(orig)),
        "error_pose_copy":    (lambda orig=name: error_pose_copy_path(orig)),
    }


#%% CELL 06 — DISCOVERY (GLOBS & SIBLINGS)
"""
Glob finders for canonical artifacts and convenience helpers to derive
sibling paths from any known filename.

Notes
- Uses non-recursive glob in the canonical folders.
- Returns sorted Paths for deterministic behavior.
- "Missing X" helpers check expected companions by existence.
"""

from pathlib import Path

# basic glob wrappers
def g_tracked() -> list[Path]:
    return sorted(pTracked.glob(f"*{SUFFIX_TRACKED}"))

def g_sleap() -> list[Path]:
    return sorted(pSleap.glob(f"*{SUFFIX_SLEAP}"))

def g_scored() -> list[Path]:
    return sorted(pScored.glob(f"*{SUFFIX_SCORED}"))

def g_pose() -> list[Path]:
    return sorted(pPose.glob(f"*{SUFFIX_POSE}"))

def g_arenaimg() -> list[Path]:
    return sorted(pArenaImage.glob(f"*{SUFFIX_ARENAIMG}"))

def g_flyvideo() -> list[Path]:
    return sorted(pFlyVideo.glob(f"*{SUFFIX_FLYVIDEO}"))

def g_cropvideo() -> list[Path]:
    return sorted(pCropVideo.glob(f"*{SUFFIX_CROPVIDEO}"))

# NEW: flagged outputs
def g_flag_scored() -> list[Path]:
    return sorted(pFlagScored.glob(f"*{SUFFIX_SCORED}"))

def g_flag_pose() -> list[Path]:
    return sorted(pFlagPose.glob(f"*{SUFFIX_POSE}"))

# NEW: error input copies (verbatim filenames)
def g_error_tracked_copies() -> list[Path]:
    return sorted(pErrorTracked.glob(f"*{SUFFIX_TRACKED}"))

def g_error_pose_copies() -> list[Path]:
    return sorted(pErrorPose.glob(f"*{SUFFIX_SLEAP}"))


# filtered discovery
def g_tracked_missing_sleap() -> list[Path]:
    """
    Tracked files that have no corresponding Sleap file.
    """
    missing = []
    for fp in g_tracked():
        base = stem_without_suffix(fp.name)
        if not (pSleap / sleap_name(base)).exists():
            missing.append(fp)
    return missing

def g_tracked_missing_scored() -> list[Path]:
    """
    Tracked files that have no corresponding Scored file (work to do).
    """
    missing = []
    for fp in g_tracked():
        base = stem_without_suffix(fp.name)
        if not (pScored / scored_name(base)).exists():
            missing.append(fp)
    return missing



#%% CELL 07 — TEMP NAMES & ROOT REBASE
"""
Helpers for atomic-write temp filenames and for rebasing the entire folder map
onto a different experiment root (e.g., Colab or an external drive).

Notes
- Naming only; no filesystem I/O.
- Temp naming inserts '.~tmp' before the final suffix.
  Example: 'BASE_fly1_scored.csv' → 'BASE_fly1_scored.~tmp.csv'
"""

from pathlib import Path
from typing import Iterable

# temp filename helpers
def temp_path(final_path: str | Path) -> Path:
    """
    Insert '.~tmp' before the file's final suffix.
    'a/b.csv' → 'a/b.~tmp.csv'
    """
    p = Path(final_path)
    if p.suffix:
        return p.with_name(f"{p.stem}.~tmp{p.suffix}")
    return p.with_name(f"{p.name}.~tmp")

def is_temp_path(path: str | Path) -> bool:
    """
    True if the path name matches the '.~tmp' convention defined in temp_path().
    """
    p = Path(path)
    return p.stem.endswith(".~tmp")

def final_from_temp(temp_path_like: str | Path) -> Path:
    """
    Remove the '.~tmp' marker from a temp filename.
    If not a temp path, returns the path unchanged.
    """
    p = Path(temp_path_like)
    if p.stem.endswith(".~tmp"):
        return p.with_name(f"{p.stem[:-5]}{p.suffix}")
    return p

# root rebase (build a shadow mapping under a different root)
_REBASE_KEYS: tuple[str, ...] = (
    # packages / tools
    "pCodes", "pConfig", "pBehaviorClassifier",
    "pBonfly", "pBonsai", "pFlyHigherProtocol", "pFlyHigherTracker",
    # data roots
    "pRawData",
    # postprocessing root and subfolders
    "pPostProcessing", "pTracked", "pSleap", "pArenaImage", "pFlyVideo", "pCropVideo",
    # classification root and subfolders
    "pBehaviorClassification", "pScored", "pPose",
    "pError", "pErrorTracked", "pErrorPose",
    "pFlag", "pFlagScored", "pFlagPose",
)

def _rebase_path(p: Path, new_root: Path) -> Path:
    """
    Compute new_root / relative_to(pExperimentalFolder) for a given path p.
    If p is not under pExperimentalFolder, returns p unchanged.
    """
    try:
        rel = p.relative_to(pExperimentalFolder)
    except Exception:
        return p
    return (Path(new_root) / rel).resolve()

def with_root(new_root: str | Path) -> dict[str, Path]:
    """
    Return a dict with the same folder keys rebased under `new_root`.
    This does not mutate globals. Useful for ephemeral runs (e.g., Colab).

    Example:
        PATH_COLAB = with_root('/content/drive/MyDrive/ExperimentX')
    """
    new_root = Path(new_root)
    mapping: dict[str, Path] = {"pExperimentalFolder": new_root.resolve()}
    for key in _REBASE_KEYS:
        p = globals().get(key, None)
        if isinstance(p, Path):
            mapping[key] = _rebase_path(p, new_root)
    return mapping


#%% CELL 08 — EXPORT (READ-ONLY PATH BUNDLE)
"""
Expose a single, read-only mapping with canonical folders, suffix policy,
and helper functions. Callers should import PATH and use its members.
"""

from types import MappingProxyType

_PATH_RW = {
    # --- roots & packages ---
    "pExperimentalFolder": pExperimentalFolder,
    "pCodes": pCodes,
    "pConfig": pConfig,
    "pBehaviorClassifier": pBehaviorClassifier,

    # --- Bonfly tree ---
    "pBonfly": pBonfly,
    "pBonsai": pBonsai,
    "pFlyHigherProtocol": pFlyHigherProtocol,
    "pFlyHigherTracker": pFlyHigherTracker,

    # --- data roots ---
    "pRawData": pRawData,
    "pPostProcessing": pPostProcessing,

    # --- postprocessing subfolders ---
    "pTracked": pTracked,
    "pSleap": pSleap,
    "pArenaImage": pArenaImage,
    "pFlyVideo": pFlyVideo,
    "pCropVideo": pCropVideo,

    # --- classification outputs (NOT a package) ---
    "pBehaviorClassification": pBehaviorClassification,
    "pScored": pScored,
    "pPose": pPose,

    # --- error & flag (new structure) ---
    "pError": pError,
    "pErrorTracked": pErrorTracked,
    "pErrorPose": pErrorPose,
    "pFlag": pFlag,
    "pFlagScored": pFlagScored,
    "pFlagPose": pFlagPose,

    # --- suffix policy ---
    "SUFFIX_TRACKED": SUFFIX_TRACKED,
    "SUFFIX_SLEAP": SUFFIX_SLEAP,
    "SUFFIX_SCORED": SUFFIX_SCORED,
    "SUFFIX_POSE": SUFFIX_POSE,
    "SUFFIX_ARENAIMG": SUFFIX_ARENAIMG,
    "SUFFIX_FLYVIDEO": SUFFIX_FLYVIDEO,
    "SUFFIX_CROPVIDEO": SUFFIX_CROPVIDEO,
    "REPORT_ERROR_NAME": REPORT_ERROR_NAME,
    "REPORT_FLAG_NAME": REPORT_FLAG_NAME,
    "KNOWN_SUFFIXES": KNOWN_SUFFIXES,

    # --- name builders (strings) ---
    "stem_without_suffix": stem_without_suffix,
    "filename": stem_without_suffix,  # alias kept for compatibility
    "tracked_name": tracked_name,
    "sleap_name": sleap_name,
    "scored_name": scored_name,
    "pose_name": pose_name,
    "arenaimg_name": arenaimg_name,
    "flyvideo_name": flyvideo_name,
    "cropvideo_name": cropvideo_name,

    # --- path builders (Paths) ---
    "tracked_path": tracked_path,
    "sleap_path": sleap_path,
    "scored_path": scored_path,
    "pose_path": pose_path,
    "arenaimg_path": arenaimg_path,
    "flyvideo_path": flyvideo_path,
    "cropvideo_path": cropvideo_path,

    # NEW paths
    "report_error_path": report_error_path,
    "report_flag_path": report_flag_path,
    "flag_scored_path": flag_scored_path,
    "flag_pose_path": flag_pose_path,
    "error_tracked_copy_path": error_tracked_copy_path,
    "error_pose_copy_path": error_pose_copy_path,


    # --- transforms & parsing ---
    "swap_suffix": swap_suffix,
    "parse_base_fly": parse_base_fly,

    # --- discovery (globs & siblings) ---
    "g_tracked": g_tracked,
    "g_sleap": g_sleap,
    "g_scored": g_scored,
    "g_pose": g_pose,
    "g_arenaimg": g_arenaimg,
    "g_flyvideo": g_flyvideo,
    "g_cropvideo": g_cropvideo,

    # NEW discovery
    "g_flag_scored": g_flag_scored,
    "g_flag_pose": g_flag_pose,
    "g_error_tracked_copies": g_error_tracked_copies,
    "g_error_pose_copies": g_error_pose_copies,


    # --- utility ---
    "siblings": siblings,

    # --- temp & rebase helpers ---
    "temp_path": temp_path,
    "is_temp_path": is_temp_path,
    "final_from_temp": final_from_temp,
    "with_root": with_root,
}

PATH = MappingProxyType(_PATH_RW)
__all__ = ["PATH"]



#%% CELL 09 — DIAGNOSTICS & __main__
"""
Lightweight, opt-in diagnostics. Safe to run; no writes.

Functions
- missing_folders()  → list[Path]
- tree_counts()      → dict[str, int]
- sample_files(n)    → dict[str, list[str]]
- sanity_checks()    → list[str]  # empty means clean
- demo(n)            → pretty print overview

Notes
- Reads directory listings only.
- Keep imports local to this cell to avoid polluting module namespace.
"""

from pathlib import Path

def _exists_all(paths: Iterable[Path]) -> list[Path]:
    return [p for p in paths if not Path(p).exists()]

def missing_folders() -> list[Path]:
    folders = [
        pCodes, pConfig, pBehaviorClassifier,
        pBonfly, pBonsai, pFlyHigherProtocol, pFlyHigherTracker,
        pRawData,
        pPostProcessing, pTracked, pSleap, pArenaImage, pFlyVideo, pCropVideo,
        pBehaviorClassification, pScored, pPose,
        pError, pErrorTracked, pErrorPose,
        pFlag, pFlagScored, pFlagPose,
    ]
    return _exists_all(folders)

def tree_counts() -> dict[str, int]:
    return {
        "Tracked":     len(list(pTracked.glob(f"*{SUFFIX_TRACKED}"))),
        "Sleap":       len(list(pSleap.glob(f"*{SUFFIX_SLEAP}"))),
        "ArenaImage":  len(list(pArenaImage.glob(f"*{SUFFIX_ARENAIMG}"))),
        "FlyVideo":    len(list(pFlyVideo.glob(f"*{SUFFIX_FLYVIDEO}"))),
        "CropVideo":   len(list(pCropVideo.glob(f"*{SUFFIX_CROPVIDEO}"))),

        "Scored":      len(list(pScored.glob(f"*{SUFFIX_SCORED}"))),
        "Pose":        len(list(pPose.glob(f"*{SUFFIX_POSE}"))),

        # New structure
        "Flag/Scored": len(list(pFlagScored.glob(f"*{SUFFIX_SCORED}"))),
        "Flag/Pose":   len(list(pFlagPose.glob(f"*{SUFFIX_POSE}"))),
        "Error/Tracked": len(list(pErrorTracked.glob(f"*{SUFFIX_TRACKED}"))),
        "Error/Pose":    len(list(pErrorPose.glob(f"*{SUFFIX_SLEAP}"))),
    }

def sample_files(n: int = 3) -> dict[str, list[str]]:
    def _names(folder: Path, pattern: str) -> list[str]:
        return [p.name for p in sorted(folder.glob(pattern))[:n]]
    return {
        "Tracked":       _names(pTracked, f"*{SUFFIX_TRACKED}"),
        "Sleap":         _names(pSleap, f"*{SUFFIX_SLEAP}"),
        "Scored":        _names(pScored, f"*{SUFFIX_SCORED}"),
        "Pose":          _names(pPose, f"*{SUFFIX_POSE}"),
        "ArenaImage":    _names(pArenaImage, f"*{SUFFIX_ARENAIMG}"),
        "FlyVideo":      _names(pFlyVideo, f"*{SUFFIX_FLYVIDEO}"),
        "CropVideo":     _names(pCropVideo, f"*{SUFFIX_CROPVIDEO}"),
        "Flag/Scored":   _names(pFlagScored, f"*{SUFFIX_SCORED}"),
        "Flag/Pose":     _names(pFlagPose, f"*{SUFFIX_POSE}"),
        "Error/Tracked": _names(pErrorTracked, f"*{SUFFIX_TRACKED}"),
        "Error/Pose":    _names(pErrorPose, f"*{SUFFIX_SLEAP}"),
    }

def sanity_checks() -> list[str]:
    issues: list[str] = []
    # distinct package vs outputs root
    if pBehaviorClassifier.resolve() == pBehaviorClassification.resolve():
        issues.append("pBehaviorClassifier equals pBehaviorClassification (package vs outputs collision).")
    # rebase keys present in PATH export
    for k in _REBASE_KEYS:
        if k not in PATH:
            issues.append(f"_REBASE_KEYS entry '{k}' not exported in PATH.")
    # name collision risk guard
    if "pBehaviorClassification" in PATH and "pBehaviorClassifier" in PATH:
        if PATH["pBehaviorClassification"] == PATH["pBehaviorClassifier"]:
            issues.append("PATH exports collide: pBehaviorClassification == pBehaviorClassifier.")
    return issues

def demo(n: int = 3) -> None:
    from pprint import pprint
    print(f"Experiment root: {pExperimentalFolder}")
    miss = missing_folders()
    if miss:
        print("\nMissing folders:")
        for m in miss: print(" -", m)
    print("\nCounts:")
    pprint(tree_counts(), sort_dicts=False)
    print(f"\nSamples (first {n}):")
    for k, v in sample_files(n).items():
        if v:
            print(f" {k}:")
            for name in v: print("   -", name)
    probs = sanity_checks()
    if probs:
        print("\nSanity checks:")
        for s in probs: print(" -", s)

if __name__ == "__main__":
    demo(3)
