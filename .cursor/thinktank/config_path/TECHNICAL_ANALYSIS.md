# 📊 **Technical Analysis: Config/path.py Refactoring**

## 📋 **Power User Technical Analysis**

### **Target File: `Codes_Working/Config/path.py`**
- **Lines**: 647 lines
- **Functions**: 17 functions
- **Structure**: 9 cells with mixed responsibilities
- **Pattern**: Monolithic file with no separation of concerns

### **🎯 Complexity Assessment**
- **High Complexity**: 25+ interdependent path variables
- **Medium Complexity**: 4 glob functions with pattern matching
- **Low Complexity**: 3 diagnostic functions
- **Critical Dependencies**: All functions depend on path constants

### **File Structure Breakdown**
```
CELL 00: Header & Overview (61 lines)
CELL 01: Imports & Types (16 lines) 
CELL 02: Root & Helper (8 lines)
CELL 03: Folder Map (60 lines) - 25+ path variables
CELL 04: File Suffix Policy (22 lines) - 4 suffixes + validation
CELL 05: Name & Path Helpers (58 lines) - 4 helper functions
CELL 06: Discovery (Globs) (57 lines) - 4 glob functions
CELL 07: Temp Names & Root Rebase (106 lines) - 3 functions + rebase logic
CELL 08: Public API (72 lines) - PATH bundle assembly
CELL 09: Diagnostics & Report (87 lines) - 3 diagnostic functions
```

## 🔍 **Key Functions Analysis**

### **Path Builders (25+ variables)**
- **Purpose**: Define canonical paths for all file types
- **Examples**: `pTracked`, `pSleap`, `pScored`, `pPose`
- **Complexity**: High - many interdependent paths
- **Preservation**: **CRITICAL** - All must work identically

### **Helper Functions (4 functions)**
- **`stem_without_suffix`**: Extract base name from filename
- **`siblings`**: Find related files
- **QC routing functions**: Error and flag path handling
- **Preservation**: **CRITICAL** - Core functionality

### **Discovery Functions (4 glob functions)**
- **`g_tracked`**: Find tracked files
- **`g_sleap`**: Find SLEAP files
- **`g_scored`**: Find scored files
- **`g_pose`**: Find pose files
- **Preservation**: **CRITICAL** - File discovery core

### **Utility Functions (3 functions)**
- **`temp_path`**: Temporary file handling
- **`with_root`**: Root path management
- **Rebase logic**: Colab/Drive path handling
- **Preservation**: **CRITICAL** - Cross-platform compatibility

### **Diagnostic Functions (3 functions)**
- **`sanity_checks`**: Path validation
- **`demo`**: Demonstration functions
- **`_count`**: File counting utilities
- **Preservation**: **IMPORTANT** - Debugging and validation

## 📊 **Data Structure Analysis**

### **Current PostProcessing Structure**
```
PostProcessing/
├── Tracked/
│   └── BASE_flyN_tracked.csv
├── Sleap/
│   └── BASE_flyN_sleap.csv
├── ArenaImage/
│   └── BASE_flyN_arenaimg.png
├── FlyVideo/
│   └── BASE_flyN_flyvideo.avi
└── CropVideo/
    └── BASE_flyN_cropvideo.avi
```

### **Target Column-Based Structure**
```
PostProcessing/
├── BASE_fly1/
│   ├── tracked/
│   │   ├── FrameIndex.csv
│   │   ├── Speed.csv
│   │   └── Position_X.csv
│   ├── sleap/
│   │   ├── FrameIndex.csv
│   │   ├── Head_Position_X.csv
│   │   └── Head_Position_Y.csv
│   ├── scored/
│   │   ├── FrameIndex.csv
│   │   ├── Behavior.csv
│   │   └── Speed.csv
│   └── pose/
│       ├── FrameIndex.csv
│       ├── Orientation.csv
│       └── View.csv
└── BASE_fly2/
    └── ... (same structure)
```

## 🔍 **FrameIndex Handling Analysis**

### **Input Data (External Tools)**
- **tracked/FrameIndex.csv**: 0,1,2,3,4,5... (full video frames)
- **sleap/FrameIndex.csv**: 0,1,2,3,4,5... (full video frames, MUST match tracked)

### **Output Data (Our Pipeline - CROPPED)**
- **scored/FrameIndex.csv**: 299,300,301,302,303,304... (cropped to experiment onset + padding)
- **pose/FrameIndex.csv**: 301,302,303,304,305,306... (cropped to experiment onset + padding)

### **Cropping Logic (from `Codes_Before/BehaviorClassifier/_qc_error_flag.py`)**
1. **Find first stimulus onset** using `EXPERIMENT["ALIGNMENT_STIM"]`
2. **Compute experiment_start** = first_onset - baseline_frames (floored at 0)
3. **Crop data** to remove setup/calibration frames before experiment onset
4. **Output FrameIndex** starts at experiment_start (e.g., 299)

### **Key Constraints**
- **Input consistency**: tracked and sleap MUST have identical FrameIndex ranges
- **Output alignment**: scored and pose should have aligned FrameIndex ranges (but may differ slightly)
- **Timeline validation**: QC checks ensure sufficient headroom and tail for experiment periods

## 📊 **Column Analysis from Example Files**

### **BASE.csv** (Shared across flies)
- **Columns**: `GPIO,FrameID,Timestamp`
- **Location**: Stays in `RawData/` (not per-fly)

### **tracked.csv** (Per-fly column-based directories)
- **Columns**: `FrameIndex,VisualStim,Stim0,Stim1,NormalizedCentroidX,NormalizedCentroidY,PixelChange`
- **Structure**: Each column becomes separate CSV file

### **sleap.csv** (Per-fly column-based directories)
- **Columns**: `FrameIndex,Left.Position.X,Left.Position.Y,Left.Confidence,Right.Position.X,Right.Position.Y,Right.Confidence,Top.Position.X,Top.Position.Y,Top.Confidence,Head.Position.X,Head.Position.Y,Head.Confidence,Thorax.Position.X,Thorax.Position.Y,Thorax.Confidence,Abdomen.Position.X,Abdomen.Position.Y,Abdomen.Confidence,LeftWing.Position.X,LeftWing.Position.Y,LeftWing.Confidence,RightWing.Position.X,RightWing.Position.Y,RightWing.Confidence`
- **Structure**: Each column becomes separate CSV file

### **pose.csv** (Per-fly column-based directories)
- **Columns**: `FrameIndex,Orientation,View,View_X,View_Y,Head_X,Head_Y,Thorax_X,Thorax_Y,Abdomen_X,Abdomen_Y,LeftWing_X,LeftWing_Y,RightWing_X,RightWing_Y`
- **Structure**: Each column becomes separate CSV file

### **scored.csv** (Per-fly column-based directories)
- **Columns**: `FrameIndex,VisualStim,Stim0,Stim1,Position_X,Position_Y,Speed,Motion,Layer1,Layer1_Denoised,Layer2,Layer2_Denoised,Resistant,Resistant_Denoised,Behavior,Behavior_Denoised`
- **Structure**: Each column becomes separate CSV file

## 🚀 **Scalability Benefits Analysis**

### **Current Limitations**
1. **Memory Issues**: Loading entire CSV files for single columns
2. **File Conflicts**: Multiple flies in same directories
3. **No Isolation**: All data mixed together
4. **Hard to Scale**: Difficult to handle 1000+ flies

### **Column-Based Benefits**
1. **Data Isolation**: Each fly's data is completely separate
2. **Parallel Processing**: Can process multiple flies simultaneously
3. **Individual Analysis**: Easy to analyze specific flies
4. **Scalable Storage**: Can handle thousands of flies
5. **No File Naming Conflicts**: Each fly has its own namespace
6. **Easy Data Management**: Simple to backup, move, or delete individual fly data
7. **Column Scalability**: Each data type gets its own directory for future column additions
8. **Memory Efficiency**: Load only needed columns for analysis
9. **Tool Compatibility**: Works with pandas, R, Excel, MATLAB
10. **Scientific Standard**: Professional CSV format with headers

## 🔧 **Technical Challenges**

### **1. Path Function Updates**
- **Challenge**: Update all 25+ path variables for new structure
- **Solution**: Systematic update of canonical path builders
- **Risk**: High - many interdependent paths

### **2. Glob Function Updates**
- **Challenge**: Update discovery functions for new structure
- **Solution**: Update glob patterns for BASE_flyN directories
- **Risk**: Medium - file discovery logic changes

### **3. Per-Fly Function Implementation**
- **Challenge**: Implement new per-fly capabilities
- **Solution**: Create new functions in `_path/per_fly.py`
- **Risk**: Medium - new functionality

### **4. FrameIndex Handling**
- **Challenge**: Different FrameIndex ranges for input vs output
- **Solution**: Clear separation of concerns - path module for paths, QC module for validation
- **Risk**: Low - well-defined separation

### **5. Backward Compatibility**
- **Challenge**: Existing code expects old structure
- **Solution**: Hybrid approach - support both old and new structures
- **Risk**: Medium - transition period complexity

## 📊 **Power User Technical Summary**

### **🎯 Refactoring Complexity Matrix**
| Component | Current Lines | Target Lines | Reduction | Complexity | Risk |
|-----------|---------------|--------------|-----------|------------|------|
| Path Builders | 60 | 20 | 67% | High | Medium |
| Helper Functions | 58 | 15 | 74% | Medium | Low |
| Discovery Functions | 57 | 20 | 65% | Medium | Medium |
| Utility Functions | 106 | 30 | 72% | High | Medium |
| Diagnostic Functions | 87 | 25 | 71% | Low | Low |
| **TOTAL** | **647** | **~200** | **70%** | **High** | **Medium** |

### **🚀 Power User Implementation Strategy**
1. **Phase 1**: Configuration Pattern (70% reduction)
2. **Phase 2**: Per-Fly Capabilities (new functionality)
3. **Phase 3**: Column-Based Structure (scalability)
4. **Phase 4**: Integration & Validation (100% preservation)

### **⚡ Performance Optimization Opportunities**
- **Memory Efficiency**: Column-based files enable selective loading
- **Parallel Processing**: Per-fly structure enables parallel analysis
- **Scalability**: Ready for 1000+ flies with column-based architecture
- **Maintainability**: Clean separation of concerns

## 📝 **Key References**

- **Original File**: `Codes_Working/Config/path.py`
- **Pattern Examples**: `Codes/Config/experiment.py`, `Codes/Config/color.py`
- **QC Module**: `Codes_Before/BehaviorClassifier/_qc_error_flag.py`
- **Example Data**: `ExampleFiles/` directory
- **Data Flow**: `.cursor/guides/project/data_flow.md`

---

**This technical analysis provides detailed understanding of the current state and challenges for the path.py refactoring project.**
