# 📝 **References: Config/path.py Refactoring**

## 📋 **File References**

This file contains all relevant file references and links for the path.py refactoring project.

## 🎯 **Target Files**

### **Primary Target**
- **`Codes_Working/Config/path.py`** - Main target file (647 lines, 17 functions)
  - **Purpose**: Configuration and path management
  - **Status**: Monolithic file requiring refactoring
  - **Target**: ~200 lines (70% reduction)

### **Pattern Examples**
- **`Codes/Config/experiment.py`** - Completed refactoring (570→230 lines, 60% reduction)
  - **Purpose**: Experiment configuration using configuration pattern
  - **Status**: ✅ **COMPLETED** - Reference for pattern application
  - **Structure**: Main controller + `_experiment/` package

- **`Codes/Config/color.py`** - Completed refactoring (1,293→273 lines, 78.9% reduction)
  - **Purpose**: Color configuration using configuration pattern
  - **Status**: ✅ **COMPLETED** - Reference for pattern application
  - **Structure**: Main controller + `_color/` package

## 🔧 **Related Files**

### **QC Module**
- **`Codes_Before/BehaviorClassifier/_qc_error_flag.py`** - QC error handling
  - **Purpose**: FrameIndex validation and data consistency checks
  - **Status**: Existing file - reference for QC integration
  - **Note**: FrameIndex safety functions belong here, not in path.py

### **Data Flow Documentation**
- **`.cursor/guides/project/data_flow.md`** - Technical data flow documentation
  - **Purpose**: Complete pipeline flow from raw data to final results
  - **Status**: Reference documentation
  - **Content**: Data transformation, FrameIndex handling, cropping logic

### **Example Data Files**
- **`ExampleFiles/BASE.csv.csv`** - Shared timing data
  - **Columns**: `GPIO,FrameID,Timestamp`
  - **Purpose**: Reference for column structure

- **`ExampleFiles/tracked.csv.csv`** - Tracking data example
  - **Columns**: `FrameIndex,VisualStim,Stim0,Stim1,NormalizedCentroidX,NormalizedCentroidY,PixelChange`
  - **Purpose**: Reference for column-based structure

- **`ExampleFiles/sleap.csv.csv`** - SLEAP body-parts data example
  - **Columns**: `FrameIndex,Left.Position.X,Left.Position.Y,Left.Confidence,...` (20+ columns)
  - **Purpose**: Reference for column-based structure

- **`ExampleFiles/pose.csv.csv`** - Pose analysis data example
  - **Columns**: `FrameIndex,Orientation,View,View_X,View_Y,Head_X,Head_Y,...` (15+ columns)
  - **Purpose**: Reference for column-based structure

- **`ExampleFiles/scored.csv.csv`** - Behavior classification data example
  - **Columns**: `FrameIndex,VisualStim,Stim0,Stim1,Position_X,Position_Y,Speed,Motion,Layer1,...` (15+ columns)
  - **Purpose**: Reference for column-based structure

## 📊 **Configuration Pattern References**

### **Completed Refactoring Examples**
- **`Codes/Config/experiment.py`** - Main controller (230 lines)
  - **Pattern**: User constants → configure() → use configured bundles
  - **Structure**: Clean separation of user interface vs implementation
  - **Result**: 60% line reduction

- **`Codes/Config/_experiment/`** - Internal modules
  - **`__init__.py`** - Configuration function & exports
  - **`stimuli.py`** - Stimulus validation & enrichment
  - **`periods.py`** - Period validation & enrichment
  - **`time.py`** - Time conversion & query utilities
  - **`report.py`** - Report generation functions

- **`Codes/Config/color.py`** - Main controller (273 lines)
  - **Pattern**: User constants → configure() → use configured bundles
  - **Structure**: Clean separation of user interface vs implementation
  - **Result**: 78.9% line reduction

- **`Codes/Config/_color/`** - Internal modules
  - **`__init__.py`** - Configuration function & exports
  - **`processing.py`** - Color processing & layer generation
  - **`colormaps.py`** - Matplotlib colormap construction
  - **`resolvers.py`** - Hex resolver functions
  - **`report.py`** - Visual report generation

## 🏗️ **Target Architecture References**

### **New Structure Design**
- **`Codes/Config/path.py`** - Main controller (target ~200 lines)
  - **Pattern**: User constants → configure() → use configured bundles
  - **Structure**: Clean separation of user interface vs implementation
  - **Target**: 70% line reduction

- **`Codes/Config/_path/`** - Internal modules
  - **`__init__.py`** - Configuration function & exports
  - **`canonical.py`** - Canonical path builders
  - **`per_fly.py`** - Per-fly data access functions
  - **`temp_files.py`** - Atomic write handling
  - **`rebase.py`** - Root rebasing (Colab/Drive)
  - **`diagnostics.py`** - QC & validation
  - **`report.py`** - Path structure reports

## 📊 **Data Structure References**

### **Current Structure**
- **`PostProcessing/Tracked/`** - Tracking data
- **`PostProcessing/Sleap/`** - SLEAP body-parts data
- **`PostProcessing/ArenaImage/`** - Arena reference images
- **`PostProcessing/FlyVideo/`** - Per-fly video clips
- **`PostProcessing/CropVideo/`** - Cropped analysis videos

### **Target Structure**
- **`PostProcessing/BASE_flyN/`** - Per-fly directories
  - **`tracked/`** - Column-based tracking data
  - **`sleap/`** - Column-based SLEAP data
  - **`scored/`** - Column-based behavior data
  - **`pose/`** - Column-based pose data
  - **Media files** - Images and videos

## 🔧 **Technical References**

### **FrameIndex Handling**
- **Input Data**: `tracked/FrameIndex.csv`, `sleap/FrameIndex.csv` (0,1,2,3,4,5...)
- **Output Data**: `scored/FrameIndex.csv`, `pose/FrameIndex.csv` (299,300,301,302,303,304...)
- **Cropping Logic**: `Codes_Before/BehaviorClassifier/_qc_error_flag.py`
- **QC Integration**: FrameIndex validation in QC module, not path module

### **Column Analysis**
- **BASE.csv**: `GPIO,FrameID,Timestamp` (shared across flies)
- **tracked.csv**: 7 columns (FrameIndex,VisualStim,Stim0,Stim1,NormalizedCentroidX,NormalizedCentroidY,PixelChange)
- **sleap.csv**: 20+ columns (body parts with Position.X, Position.Y, Confidence)
- **pose.csv**: 15+ columns (Orientation,View,View_X,View_Y,Head_X,Head_Y,...)
- **scored.csv**: 15+ columns (FrameIndex,VisualStim,Stim0,Stim1,Position_X,Position_Y,Speed,Motion,Layer1,...)

## 📝 **Documentation References**

### **Thinktank Files**
- **`EXECUTIVE_SUMMARY.md`** - High-level overview
- **`DECISIONS_LOG.md`** - All decisions made
- **`TECHNICAL_ANALYSIS.md`** - Current state analysis
- **`ARCHITECTURE_PLAN.md`** - Future architecture design
- **`IMPLEMENTATION_ROADMAP.md`** - Step-by-step implementation
- **`REFERENCES.md`** - This file

### **Project Documentation**
- **`.cursor/guides/project/data_flow.md`** - Data flow documentation
- **`.cursor/logs/completed/config_experiment.md`** - Experiment refactoring log
- **`.cursor/logs/completed/config_color.md`** - Color refactoring log
- **`.cursor/logs/decisions/architecture_decisions.md`** - Architecture decisions

## 🚀 **Implementation References**

### **Best Practices**
- **Configuration Pattern**: User constants → configure() → use configured bundles
- **Immutable APIs**: Using `MappingProxyType` for all Config module exports
- **Cell-Based Structure**: Preserving `#%% CELL XX` structure during transition
- **100% Functionality Preservation**: Mandatory requirement for all refactoring

### **Validation Requirements**
- **Comprehensive testing**: All 17 functions + new per-fly functions
- **File system operations**: Special validation for glob functions
- **Per-fly logic**: Validation of BASE_flyN pattern handling
- **Column-based validation**: Test individual column file access

## 📝 **Key Links**

- **Original File**: `Codes_Working/Config/path.py`
- **Pattern Examples**: `Codes/Config/experiment.py`, `Codes/Config/color.py`
- **QC Module**: `Codes_Before/BehaviorClassifier/_qc_error_flag.py`
- **Data Flow**: `.cursor/guides/project/data_flow.md`
- **Example Data**: `ExampleFiles/` directory

---

**This references file provides all relevant file references and links for the path.py refactoring project.**
