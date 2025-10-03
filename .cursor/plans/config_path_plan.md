# Config path.py Refactoring Plan

## 🎯 **Mission: Apply Configuration Pattern to Path Management**

Transform path.py using the proven configuration pattern established in experiment.py and color.py while **preserving your exact canonical folder structure** and **enhancing with per-fly capabilities**. This maintains your existing data organization while enabling individual fly analysis.

**Strategy**: Apply the revolutionary configuration pattern to your working system (647 lines, 17 functions) while adding per-fly functions that work with your BASE_flyN filename pattern.

## 🏗️ **Canonical Structure (Preserved with BASE_flyN Pattern)**

```
ExperimentalFolder/
├── Codes/                          # Source code packages
│   ├── Config/                     # Config package (configuration pattern)
│   │   ├── __init__.py
│   │   ├── experiment.py           # Experiment configuration ✅ COMPLETED
│   │   ├── color.py                # Color schemes & visualization ✅ COMPLETED
│   │   ├── path.py                 # Path management (target for refactoring)
│   │   │   └── _path/              # Internal path modules
│   │   │       ├── __init__.py     # configure() function
│   │   │       ├── canonical.py    # Canonical path builders
│   │   │       ├── per_fly.py      # Per-fly data access (BASE_flyN pattern)
│   │   │       ├── temp_files.py   # Atomic write handling
│   │   │       ├── rebase.py       # Root rebasing (Colab/Drive)
│   │   │       ├── diagnostics.py  # QC & validation
│   │   │       └── report.py       # Path structure reports
│   │   └── param.py                # Parameter schemas & metadata
│   ├── BehaviorClassifier/         # Classification package
│   │   ├── __init__.py
│   │   ├── _utils.py               # Utilities
│   │   ├── _qc_error_flag.py       # QC error/flag handling
│   │   ├── _classifier.py          # Core classification logic
│   │   ├── _colab.py               # Colab-specific functions
│   │   └── _main.py                # Main execution
│   └── BehaviorClassifier_Run.ipynb
├── Bonfly/                         # Bonsai + protocols + tracker
│   ├── Bonsai/                     # Bonsai configuration files
│   ├── FlyHigher-Protocol/         # Protocol definitions
│   └── FlyHigher-Tracker/          # Tracker configurations
├── RawData/                        # BASE data (shared across flies)
│   ├── BASE.avi                    # Original video
│   └── BASE.csv                    # GPIO, FrameID, Timestamp (shared)
├── PostProcessing/                 # Derived intermediates (BASE_flyN pattern)
│   ├── Tracked/                    # Tracking data
│   │   ├── BASE_fly1_tracked.csv   # Fly 1 tracking data
│   │   ├── BASE_fly2_tracked.csv   # Fly 2 tracking data
│   │   └── ...                     # Additional flies
│   ├── Sleap/                      # SLEAP body-parts data
│   │   ├── BASE_fly1_sleap.csv     # Fly 1 SLEAP data
│   │   ├── BASE_fly2_sleap.csv     # Fly 2 SLEAP data
│   │   └── ...                     # Additional flies
│   ├── ArenaImage/                 # Arena images (single files)
│   │   ├── BASE_fly1_arenaimg.png  # Fly 1 arena image
│   │   ├── BASE_fly2_arenaimg.png  # Fly 2 arena image
│   │   └── ...                     # Additional flies
│   ├── FlyVideo/                   # Cropped videos (single files)
│   │   ├── BASE_fly1_flyvideo.avi  # Fly 1 video
│   │   ├── BASE_fly2_flyvideo.avi  # Fly 2 video
│   │   └── ...                     # Additional flies
│   ├── CropVideo/                  # Crop videos (single files)
│   │   ├── BASE_fly1_cropvideo.avi # Fly 1 crop video
│   │   ├── BASE_fly2_cropvideo.avi # Fly 2 crop video
│   │   └── ...                     # Additional flies
│   ├── Scored/                     # Behavior classification (merged from BehaviorClassification)
│   │   ├── BASE_fly1_scored.csv    # Fly 1 behavior scores
│   │   ├── BASE_fly2_scored.csv    # Fly 2 behavior scores
│   │   └── ...                     # Additional flies
│   ├── Pose/                       # Pose analysis (merged from BehaviorClassification)
│   │   ├── BASE_fly1_pose.csv      # Fly 1 pose data
│   │   ├── BASE_fly2_pose.csv      # Fly 2 pose data
│   │   └── ...                     # Additional flies
│   ├── Error/                      # QC error handling
│   │   ├── Tracked/                # Error tracked files
│   │   └── Pose/                   # Error pose files
│   └── Flag/                       # QC flag handling
│       ├── Scored/                 # Flagged scored files
│       └── Pose/                   # Flagged pose files
```

## 🚀 **Configuration Pattern Application**

### **Target Architecture**

```
Codes/Config/
├── path.py                     # Main controller & user interface (200 lines)
└── _path/                      # Internal processing modules
    ├── __init__.py            # Configuration function & exports (80 lines)
    ├── canonical.py           # Canonical path builders (300 lines)
    ├── per_fly.py            # Per-fly data access functions (200 lines)
    ├── temp_files.py         # Atomic write handling (50 lines)
    ├── rebase.py            # Root rebasing (100 lines)
    ├── diagnostics.py       # QC & validation (80 lines)
    └── report.py            # Path structure reports (60 lines)
```

### **User Constants (path.py CELL 02)**

```python
#%% CELL 02 — USER INPUT
"""
Authoritative path configuration. Purely declarative (no derivations).
"""

# Experiment root
pExperimentalFolder = Path("{{__EXP_FOLDER__}}")

# File extensions (preserved from working version)
CSV_EXTENSION = ".csv"
PNG_EXTENSION = ".png"
AVI_EXTENSION = ".avi"

# Temporary file suffix (for atomic writes)
TEMP_SUFFIX = ".tmp"

# Filename suffixes (preserved from working version)
TRACKED_SUFFIX = "_tracked.csv"
SLEAP_SUFFIX = "_sleap.csv"
SCORED_SUFFIX = "_scored.csv"
POSE_SUFFIX = "_pose.csv"
```

### **Configuration Pattern (_path/__init__.py)**

```python
def configure(experimental_folder, file_extensions, filename_suffixes):
    """
    Configure all path modules with user parameters.
    This updates the module-level bundles.
    
    Args:
        experimental_folder: Path to experiment root
        file_extensions: Dict of file extensions (CSV_EXTENSION, etc.)
        filename_suffixes: Dict of filename suffixes (TRACKED_SUFFIX, etc.)
    """
    global _CANONICAL, _PER_FLY, _TEMP_FILES, _REBASE, _DIAGNOSTICS, _HELPERS
    
    # Create canonical path system
    _CANONICAL = canonical.create_canonical_bundle(experimental_folder, filename_suffixes)
    
    # Create per-fly data access functions
    _PER_FLY = per_fly.create_per_fly_bundle(_CANONICAL)
    
    # Create other bundles
    _TEMP_FILES = temp_files.create_temp_files_bundle()
    _REBASE = rebase.create_rebase_bundle(experimental_folder, _CANONICAL)
    _DIAGNOSTICS = diagnostics.create_diagnostics_bundle(experimental_folder, _CANONICAL)
    _HELPERS = helpers.create_helpers_bundle()

# These will be set by configure()
_CANONICAL = None
_PER_FLY = None
_TEMP_FILES = None
_REBASE = None
_DIAGNOSTICS = None
_HELPERS = None
_REPORT = report._REPORT
```

## 🎯 **Per-Fly Implementation (BASE_flyN Pattern)**

### **Per-Fly Data Access Functions**

The per-fly implementation adds functions that work with the BASE_flyN filename pattern:

```python
# NEW: Per-fly data access functions using BASE_flyN pattern
def get_fly_files(fly_id: str, data_type: str) -> list[Path]:
    """Get all files for a specific fly using BASE_flyN pattern."""
    if data_type == "tracked":
        files = canonical_bundle["g_tracked"]()
        return [p for p in files if f"_fly{fly_id}_" in str(p)]
    elif data_type == "sleap":
        files = canonical_bundle["g_sleap"]()
        return [p for p in files if f"_fly{fly_id}_" in str(p)]
    elif data_type == "scored":
        files = canonical_bundle["g_scored"]()
        return [p for p in files if f"_fly{fly_id}_" in str(p)]
    elif data_type == "pose":
        files = canonical_bundle["g_pose"]()
        return [p for p in files if f"_fly{fly_id}_" in str(p)]
    elif data_type == "base":
        # BASE data is shared, not per-fly
        base_file = canonical_bundle["pRawData"] / "BASE.csv"
        return [base_file] if base_file.exists() else []
    else:
        raise ValueError(f"Unknown data type: {data_type}")

def get_fly_parameter(fly_id: str, data_type: str, parameter: str) -> Path:
    """Get path to specific parameter file for a fly."""
    fly_files = get_fly_files(fly_id, data_type)
    for file_path in fly_files:
        if parameter in file_path.name:
            return file_path
    raise FileNotFoundError(f"No {parameter} file found for fly {fly_id} in {data_type}")

def discover_flies() -> list[str]:
    """Discover all fly IDs from BASE_flyN pattern in filenames."""
    flies = set()
    
    # Check all data types for fly IDs
    for data_type in ["tracked", "sleap", "scored", "pose"]:
        files = canonical_bundle[f"g_{data_type}"]()
        for file_path in files:
            # Extract fly ID from filename like "BASE_fly1_tracked.csv"
            if "_fly" in file_path.name:
                parts = file_path.name.split("_fly")
                if len(parts) > 1:
                    fly_part = parts[1].split("_")[0]
                    if fly_part.isdigit():
                        flies.add(fly_part)
    
    return sorted(list(flies))

def get_fly_status(fly_id: str) -> str:
    """Get processing status for a fly by checking available files."""
    tracked_files = get_fly_files(fly_id, "tracked")
    scored_files = get_fly_files(fly_id, "scored")
    
    if not tracked_files:
        return "missing_input"
    elif not scored_files:
        return "needs_processing"
    else:
        return "processed"

def discover_parameters(fly_id: str, data_type: str) -> list[str]:
    """Discover available parameters for a fly and data type."""
    fly_files = get_fly_files(fly_id, data_type)
    parameters = []
    
    for file_path in fly_files:
        # Extract parameter from filename
        stem = canonical_bundle["stem_without_suffix"](file_path)
        if "_fly" in stem:
            # Extract parameter from filename like "BASE_fly1_tracked"
            parts = stem.split("_fly")[1].split("_")
            if len(parts) > 1:
                param = "_".join(parts[1:])  # Everything after fly number
                parameters.append(param)
    
    return sorted(list(set(parameters)))
```

## 🏗️ **Implementation Strategy**

### **Phase 1: Apply Configuration Pattern**

#### **User Constants (path.py CELL 02)**

```python
#%% CELL 02 — USER INPUT
"""
Authoritative path configuration. Purely declarative (no derivations).
"""

# Experiment root
pExperimentalFolder = Path("{{__EXP_FOLDER__}}")

# File extensions (preserved from working version)
CSV_EXTENSION = ".csv"
PNG_EXTENSION = ".png"
AVI_EXTENSION = ".avi"

# Temporary file suffix (for atomic writes)
TEMP_SUFFIX = ".tmp"

# Filename suffixes (preserved from working version)
TRACKED_SUFFIX = "_tracked.csv"
SLEAP_SUFFIX = "_sleap.csv"
SCORED_SUFFIX = "_scored.csv"
POSE_SUFFIX = "_pose.csv"
```

#### **Internal Module Structure**

```
_path/
├── __init__.py          # configure() function
├── canonical.py         # Canonical path builders (from working version)
├── per_fly.py          # Per-fly data access functions (BASE_flyN pattern)
├── temp_files.py        # Temporary file handling (from working version)
├── rebase.py           # Root rebasing (from working version)
├── diagnostics.py      # QC and diagnostic functions (from working version)
└── report.py           # Path structure reports
```

### **Phase 2: Canonical Path Functions (_path/canonical.py)**

```python
def create_canonical_bundle(experimental_folder, filename_suffixes):
    """Create canonical path system (from your working version)."""
    
    # All your existing path builders (preserved exactly)
    def _p(sub: str) -> Path:
        """Join a subpath under the experiment root."""
        return experimental_folder / sub
    
    # All your canonical paths (preserved exactly)
    pCodes = _p("Codes")
    pConfig = pCodes / "Config"
    pBehaviorClassifier = pCodes / "BehaviorClassifier"
    pBehaviorClassifierRun = pCodes / "BehaviorClassifier_Run.ipynb"
    
    pBonfly = _p("Bonfly")
    pBonsai = pBonfly / "Bonsai"
    pFlyHigherProtocol = pBonfly / "FlyHigher-Protocol"
    pFlyHigherTracker = pBonfly / "FlyHigher-Tracker"
    
    pRawData = _p("RawData")
    
    pPostProcessing = _p("PostProcessing")
    pTracked = pPostProcessing / "Tracked"
    pSleap = pPostProcessing / "Sleap"
    pArenaImage = pPostProcessing / "ArenaImage"
    pFlyVideo = pPostProcessing / "FlyVideo"
    pCropVideo = pPostProcessing / "CropVideo"
    
    # Merged BehaviorClassification into PostProcessing
    pScored = pPostProcessing / "Scored"
    pPose = pPostProcessing / "Pose"
    
    pError = pPostProcessing / "Error"
    pErrorTracked = pError / "Tracked"
    pErrorPose = pError / "Pose"
    
    pFlag = pPostProcessing / "Flag"
    pFlagScored = pFlag / "Scored"
    pFlagPose = pFlag / "Pose"
    
    # All your existing functions (preserved exactly)
    def stem_without_suffix(path: Path) -> str:
        """Return the canonical stem of a file by removing a known suffix."""
        # ... exact implementation from your working version
    
    def siblings(path: Path) -> dict[str, Path]:
        """Generate sibling file paths using canonical suffixes."""
        # ... exact implementation from your working version
    
    # All your glob functions (preserved exactly)
    def g_tracked(folder: Path = pTracked) -> list[Path]:
        """List tracked files."""
        return sorted(folder.glob(f"*{filename_suffixes['TRACKED_SUFFIX']}"))
    
    def g_sleap(folder: Path = pSleap) -> list[Path]:
        """List SLEAP body-parts files."""
        return sorted(folder.glob(f"*{filename_suffixes['SLEAP_SUFFIX']}"))
    
    def g_scored(folder: Path = pScored) -> list[Path]:
        """List scored behavior files."""
        return sorted(folder.glob(f"*{filename_suffixes['SCORED_SUFFIX']}"))
    
    def g_pose(folder: Path = pPose) -> list[Path]:
        """List derived pose files."""
        return sorted(folder.glob(f"*{filename_suffixes['POSE_SUFFIX']}"))
    
    # All your other functions (preserved exactly)
    # ... temp_path, with_root, etc.
    
    return MappingProxyType({
        # All your canonical paths
        "pExperimentalFolder": experimental_folder,
        "pCodes": pCodes,
        "pConfig": pConfig,
        "pBehaviorClassifier": pBehaviorClassifier,
        "pBehaviorClassifierRun": pBehaviorClassifierRun,
        "pBonfly": pBonfly,
        "pBonsai": pBonsai,
        "pFlyHigherProtocol": pFlyHigherProtocol,
        "pFlyHigherTracker": pFlyHigherTracker,
        "pRawData": pRawData,
        "pPostProcessing": pPostProcessing,
        "pTracked": pTracked,
        "pSleap": pSleap,
        "pArenaImage": pArenaImage,
        "pFlyVideo": pFlyVideo,
        "pCropVideo": pCropVideo,
        "pScored": pScored,
        "pPose": pPose,
        "pError": pError,
        "pErrorTracked": pErrorTracked,
        "pErrorPose": pErrorPose,
        "pFlag": pFlag,
        "pFlagScored": pFlagScored,
        "pFlagPose": pFlagPose,
        
        # All your functions
        "stem_without_suffix": stem_without_suffix,
        "siblings": siblings,
        "g_tracked": g_tracked,
        "g_sleap": g_sleap,
        "g_scored": g_scored,
        "g_pose": g_pose,
        # ... all other functions
    })
```

### **Phase 3: Main File Transformation**

#### **Revolutionary Main File Structure**

```python
#%% CELL 00 — HEADER & OVERVIEW
"""
Canonical path management with per-fly capabilities.
Preserves existing folder structure while enabling individual fly analysis.
"""

#%% CELL 01 — IMPORTS & TYPES
from __future__ import annotations
import sys
from pathlib import Path
from types import MappingProxyType

# Package path setup (for safe absolute imports)
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Config import _path

#%% CELL 02 — USER INPUT
"""
Authoritative path configuration. Purely declarative (no derivations).
"""
pExperimentalFolder = Path("{{__EXP_FOLDER__}}")

# File extensions
CSV_EXTENSION = ".csv"
PNG_EXTENSION = ".png"
AVI_EXTENSION = ".avi"
TEMP_SUFFIX = ".tmp"

# Filename suffixes
TRACKED_SUFFIX = "_tracked.csv"
SLEAP_SUFFIX = "_sleap.csv"
SCORED_SUFFIX = "_scored.csv"
POSE_SUFFIX = "_pose.csv"

#%% CELL 03 — CONFIGURATION
"""
Single function call configures the canonical path system with per-fly capabilities.
"""
_path.configure(
    pExperimentalFolder,
    {
        "CSV_EXTENSION": CSV_EXTENSION,
        "PNG_EXTENSION": PNG_EXTENSION,
        "AVI_EXTENSION": AVI_EXTENSION,
        "TEMP_SUFFIX": TEMP_SUFFIX,
    },
    {
        "TRACKED_SUFFIX": TRACKED_SUFFIX,
        "SLEAP_SUFFIX": SLEAP_SUFFIX,
        "SCORED_SUFFIX": SCORED_SUFFIX,
        "POSE_SUFFIX": POSE_SUFFIX,
    }
)

#%% CELL 04 — PUBLIC API ASSEMBLY
"""
Clean assembly from configured bundles.
"""
_PUBLIC = {
    # File extensions
    "CSV_EXTENSION": CSV_EXTENSION,
    "PNG_EXTENSION": PNG_EXTENSION,
    "AVI_EXTENSION": AVI_EXTENSION,
    "TEMP_SUFFIX": TEMP_SUFFIX,
    
    # Canonical path system (preserved from working version)
    **_path._CANONICAL,
    
    # Per-fly capabilities (added)
    **_path._PER_FLY,
    
    # Other capabilities (preserved from working version)
    **_path._TEMP_FILES,
    **_path._REBASE,
    **_path._DIAGNOSTICS,
    **_path._HELPERS,
}

PATH = MappingProxyType(_PUBLIC)
__all__ = ["PATH"]

#%% CELL 05 — REPORT
if __name__ == "__main__":
    _path._REPORT["render_path_report"](PATH)
```

## 🧪 **Usage Examples**

### **1. Canonical Usage (Preserved)**
```python
# All your existing functions work exactly the same
tracked_files = PATH["g_tracked"]()
sleap_files = PATH["g_sleap"]()
scored_files = PATH["g_scored"]()

# All your existing paths work exactly the same
raw_data_path = PATH["pRawData"]
post_processing_path = PATH["pPostProcessing"]
```

### **2. Per-Fly Usage (Added)**
```python
# Discover all flies
flies = PATH["discover_flies"]()

# Get files for specific fly
fly1_tracked = PATH["get_fly_files"]("1", "tracked")
fly1_scored = PATH["get_fly_files"]("1", "scored")

# Get specific parameter for fly
fly1_speed = PATH["get_fly_parameter"]("1", "scored", "Speed")

# Check fly status
status = PATH["get_fly_status"]("1")  # "processed", "needs_processing", "missing_input"

# Discover parameters for fly
params = PATH["discover_parameters"]("1", "scored")
```

## 🎯 **Implementation Timeline**

### **Day 1: Canonical Module Creation**
- Create _path/ package structure
- Implement canonical.py with all your existing functions
- Test canonical path system works identically

### **Day 2: Per-Fly Module Creation**
- Implement per_fly.py with fly discovery and data access
- Test per-fly functions work with BASE_flyN pattern
- Ensure no breaking changes to existing functionality

### **Day 3: Integration & Configuration**
- Create configure() function
- Implement other modules (temp_files, rebase, diagnostics)
- Test complete integration

### **Day 4: Main File Transformation**
- Transform main path.py file with configuration pattern
- Test complete system
- Ensure backward compatibility

### **Day 5: Validation & Testing**
- Comprehensive testing of both canonical and per-fly functionality
- Performance validation
- Final documentation

## 🎯 **Key Benefits**

### **✅ What's Preserved**
1. **Exact canonical folder structure** - No changes to data organization
2. **All 17 functions** from your working version
3. **All path constants** and folder mappings
4. **Backward compatibility** - existing code continues to work

### **✅ What's Added**
1. **Per-fly data access** - Individual fly analysis capabilities using BASE_flyN pattern
2. **Fly discovery** - Find all flies in the system
3. **Status tracking** - Check processing status per fly
4. **Parameter discovery** - Find available parameters per fly
5. **Configuration pattern** - Modern, maintainable code structure

### **✅ What's Improved**
1. **Merged structure** - BehaviorClassification merged into PostProcessing
2. **Single files** - Arena images, videos as single files (no subdirectories)
3. **BASE_flyN pattern** - Correct filename logic for per-fly data
4. **Configuration approach** - Follows proven pattern from experiment.py and color.py

This approach gives you the best of both worlds: **preserves your proven canonical structure** while **adding per-fly capabilities** for individual fly analysis using the correct BASE_flyN filename pattern.