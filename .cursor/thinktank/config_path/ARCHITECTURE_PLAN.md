# 🏗️ **Architecture Plan: Config/path.py Refactoring**

## 🎯 **Target Architecture Overview**

Transform the monolithic `path.py` (647 lines) into a clean, scalable, configuration-based architecture following the proven pattern established in `experiment.py` and `color.py` refactoring.

## 🏗️ **New Structure Design**

### **Main Controller: `path.py` (~200 lines)**
```python
# User constants and configuration
# Single configure() function
# Clean public API
# Immutable PATH bundle
```

### **Internal Modules: `_path/` Package**
```
_path/
├── __init__.py         # Configuration function & exports
├── canonical.py        # Canonical path builders
├── per_fly.py          # Per-fly data access functions
├── temp_files.py       # Atomic write handling
├── rebase.py           # Root rebasing (Colab/Drive)
├── diagnostics.py      # QC & validation
└── report.py           # Path structure reports
```

## 🎯 **Configuration Pattern Application**

### **Phase 1: Structure Creation**
1. **Create `_path/` package** with all internal modules
2. **Implement `configure()` function** in `_path/__init__.py`
3. **Move canonical path builders** to `_path/canonical.py`
4. **Preserve all existing functions** exactly

### **Phase 2: Per-Fly Capabilities**
1. **Implement per-fly functions** in `_path/per_fly.py`
2. **Add BASE_flyN pattern handling**
3. **Create fly discovery and status functions**
4. **Test per-fly functionality**

### **Phase 3: Structural Changes**
1. **Merge BehaviorClassification → PostProcessing**
2. **Implement column-based file structure**
3. **Update path builders** for new structure
4. **Test structural changes**

### **Phase 4: Integration & Validation**
1. **Transform main path.py file**
2. **Comprehensive validation** of all functions
3. **Test per-fly capabilities**
4. **Verify structural changes**

## 🚀 **Per-Fly Capabilities Design**

### **New Functions for Column-Based Structure**
```python
# Per-fly data access functions
def get_fly_data_path(fly_id: str, data_type: str) -> Path:
    """Get path to specific data type directory for a fly."""
    # Returns: PostProcessing/BASE_fly{fly_id}/{data_type}/

def get_fly_column_file(fly_id: str, data_type: str, column: str) -> Path:
    """Get path to specific column file for a fly."""
    # Returns: PostProcessing/BASE_fly{fly_id}/{data_type}/{column}.csv

def discover_flies() -> list[str]:
    """Discover all fly IDs from BASE_flyN directories in PostProcessing."""

def get_fly_status(fly_id: str) -> str:
    """Get processing status for a fly by checking available data directories."""
    # Returns: "complete", "partial", "missing_input", "needs_processing"

def get_fly_data_types(fly_id: str) -> list[str]:
    """Get available data types for a specific fly."""
    # Returns: ["tracked", "sleap", "scored", "pose"] based on existing directories

def get_fly_columns(fly_id: str, data_type: str) -> list[str]:
    """Get available columns for a specific fly's data type."""
    # Returns: ["FrameIndex", "Speed", "Behavior"] based on existing CSV files

def get_fly_media_files(fly_id: str) -> dict[str, Path]:
    """Get media files (images, videos) for a specific fly."""
    # Returns: {"arenaimg": Path, "flyvideo": Path, "cropvideo": Path}
```

## 🏗️ **Column-Based File Structure**

### **Target PostProcessing Structure**
```
PostProcessing/                 # Derived intermediates (BASE_flyN pattern)
├── BASE_fly1/                  # Per-fly directory for fly 1
│   ├── tracked/                # Fly 1 tracking data (column-based)
│   │   ├── FrameIndex.csv      # Header: FrameIndex, Data: 0,1,2,3,4,5...
│   │   ├── VisualStim.csv      # Header: VisualStim, Data: 0,0,0,0,0,0...
│   │   ├── Stim0.csv           # Header: Stim0, Data: 0,0,0,0,0,0...
│   │   ├── Stim1.csv           # Header: Stim1, Data: 0,0,0,0,0,0...
│   │   ├── NormalizedCentroidX.csv # Header: NormalizedCentroidX, Data: 0.774286747,0.776573777...
│   │   ├── NormalizedCentroidY.csv # Header: NormalizedCentroidY, Data: 0.138588518,0.138957903...
│   │   └── PixelChange.csv     # Header: PixelChange, Data: 0,406,272,318,116,482...
│   ├── sleap/                  # Fly 1 SLEAP body-parts data (column-based)
│   │   ├── FrameIndex.csv      # Header: FrameIndex, Data: 0,1,2,3,4,5...
│   │   ├── Left_Position_X.csv # Header: Left_Position_X, Data: NaN,NaN,NaN,NaN,NaN...
│   │   ├── Left_Position_Y.csv # Header: Left_Position_Y, Data: NaN,NaN,NaN,NaN,NaN...
│   │   ├── Left_Confidence.csv # Header: Left_Confidence, Data: 0.093549653887748718,0.081384599208831787...
│   │   └── ... (all body part columns)
│   ├── scored/                 # Fly 1 behavior classification (column-based, CROPPED)
│   │   ├── FrameIndex.csv      # Header: FrameIndex, Data: 299,300,301,302,303,304...
│   │   ├── VisualStim.csv      # Header: VisualStim, Data: 0,0,0,0,0,0...
│   │   ├── Position_X.csv      # Header: Position_X, Data: 1.3369401539999999,1.2823935240000002...
│   │   ├── Speed.csv           # Header: Speed, Data: 3.7,7.59,23.54,3.03,13.16,3.38...
│   │   ├── Behavior.csv        # Header: Behavior, Data: Walk,Walk,Walk,Walk,Walk,Walk...
│   │   └── ... (all behavior columns)
│   ├── pose/                   # Fly 1 pose analysis (column-based, CROPPED)
│   │   ├── FrameIndex.csv      # Header: FrameIndex, Data: 301,302,303,304,305,306...
│   │   ├── Orientation.csv     # Header: Orientation, Data: 172.67,169.7,169.7,169.08,169.7,172.67...
│   │   ├── View.csv            # Header: View, Data: Top,Top,Top,Top,Top,Top...
│   │   └── ... (all pose columns)
│   ├── arenaimg.png            # Fly 1 arena image (single file)
│   ├── flyvideo.avi            # Fly 1 video (single file)
│   └── cropvideo.avi           # Fly 1 crop video (single file)
├── BASE_fly2/                  # Per-fly directory for fly 2
│   └── ...                     # Same column-based structure as fly 1
├── BASE_fly3/                  # Per-fly directory for fly 3
│   └── ...                     # Same column-based structure as fly 1
├── Error/                      # QC error handling (merged from BehaviorClassification)
│   ├── Tracked/                # Error tracked files
│   └── Pose/                   # Error pose files
└── Flag/                       # QC flag handling (merged from BehaviorClassification)
    ├── Scored/                 # Flagged scored files
    └── Pose/                   # Flagged pose files
```

## 🎯 **Hybrid Approach Implementation**

### **Phase 1: Immediate Memory Solution**
```python
# Instead of loading entire CSV (memory killer):
df = pd.read_csv('tracked.csv')  # Loads everything
speed = df['Speed']

# Use selective loading (memory efficient):
speed = pd.read_csv('tracked.csv', usecols=['Speed'])['Speed']
```

### **Phase 2: Column-Based Architecture (Future)**
- Keep big files for compatibility
- Add column-based access as convenience layer
- Gradual migration to per-fly directories
- Full scalability for 1000+ flies

## 🔧 **Module Responsibilities**

### **`_path/__init__.py`**
- **Purpose**: Configuration function and exports
- **Functions**: `configure()`, `get_path_bundle()`
- **Exports**: Immutable PATH bundle

### **`_path/canonical.py`**
- **Purpose**: Canonical path builders
- **Functions**: All 25+ path variables
- **Updates**: Support new column-based structure

### **`_path/per_fly.py`**
- **Purpose**: Per-fly data access functions
- **Functions**: Fly discovery, status tracking, data access
- **New**: BASE_flyN pattern handling

### **`_path/temp_files.py`**
- **Purpose**: Atomic write handling
- **Functions**: `temp_path`, atomic write utilities
- **Preservation**: Existing functionality

### **`_path/rebase.py`**
- **Purpose**: Root rebasing (Colab/Drive)
- **Functions**: `with_root`, rebase logic
- **Preservation**: Cross-platform compatibility

### **`_path/diagnostics.py`**
- **Purpose**: QC & validation
- **Functions**: `sanity_checks`, `demo`, `_count`
- **Preservation**: Existing diagnostic functions

### **`_path/report.py`**
- **Purpose**: Path structure reports
- **Functions**: Report generation, structure analysis
- **New**: Column-based structure reporting

## 🚀 **Scalability Benefits**

### **Data Isolation**
- Each fly's data is completely separate and organized
- No file naming conflicts between flies
- Easy to backup, move, or delete individual fly data

### **Parallel Processing**
- Can process multiple flies simultaneously without conflicts
- Each fly has its own namespace
- Scalable to thousands of flies

### **Memory Efficiency**
- Load only needed columns for analysis
- Column-based access for specific parameters
- No need to load entire CSV files

### **Tool Compatibility**
- Works with pandas, R, Excel, MATLAB
- Professional CSV format with headers
- Scientific standard format

## 🔧 **FrameIndex Handling Architecture**

### **Input Data (External Tools)**
- **tracked/FrameIndex.csv**: 0,1,2,3,4,5... (full video frames)
- **sleap/FrameIndex.csv**: 0,1,2,3,4,5... (full video frames, MUST match tracked)

### **Output Data (Our Pipeline - CROPPED)**
- **scored/FrameIndex.csv**: 299,300,301,302,303,304... (cropped to experiment onset + padding)
- **pose/FrameIndex.csv**: 301,302,303,304,305,306... (cropped to experiment onset + padding)

### **QC Integration (Handled in BehaviorClassifier/_qc_error_flag.py)**
- **FrameIndex alignment validation**: Ensure tracked and sleap have identical FrameIndex ranges
- **Timeline validation**: Check experiment onset, baseline headroom, and tail coverage
- **Data consistency checks**: Validate scored and pose data alignment
- **Cropping validation**: Ensure proper experiment onset detection and cropping

**Note**: FrameIndex safety and validation functions belong in `BehaviorClassifier/_qc_error_flag.py`, not in `Config/path.py`. The path module provides path access functions; the QC module validates data consistency.

## 📝 **Key References**

- **Pattern Examples**: `Codes/Config/experiment.py`, `Codes/Config/color.py`
- **QC Module**: `Codes_Before/BehaviorClassifier/_qc_error_flag.py`
- **Data Flow**: `.cursor/guides/project/data_flow.md`
- **Example Data**: `ExampleFiles/` directory

---

**This architecture plan provides the detailed design for the path.py refactoring project.**
