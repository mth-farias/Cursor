# 📋 **Implementation Roadmap: Config/path.py Refactoring**

## 🎯 **Implementation Strategy**

This roadmap provides step-by-step implementation guidance for the path.py refactoring project, following the proven configuration pattern established in `experiment.py` and `color.py`.

## 🚀 **Phase 1: Configuration Pattern Application**

### **Step 1.1: Create `_path/` Package Structure**
```bash
# Create directory structure
mkdir -p Codes/Config/_path
```

**Files to create:**
- `_path/__init__.py` - Configuration function & exports
- `_path/canonical.py` - Canonical path builders
- `_path/per_fly.py` - Per-fly data access functions
- `_path/temp_files.py` - Atomic write handling
- `_path/rebase.py` - Root rebasing (Colab/Drive)
- `_path/diagnostics.py` - QC & validation
- `_path/report.py` - Path structure reports

### **Step 1.2: Implement `configure()` Function**
**File**: `_path/__init__.py`

```python
def configure() -> MappingProxyType:
    """Configure path module and return immutable PATH bundle."""
    # Implementation details...
    return MappingProxyType(path_bundle)
```

### **Step 1.3: Move Canonical Path Builders**
**File**: `_path/canonical.py`

**Functions to move:**
- All 25+ path variables from CELL 03
- Path builders for tracked, sleap, scored, pose
- Error and flag path builders
- Media file path builders

### **Step 1.4: Preserve All Existing Functions**
**Files**: Various `_path/*.py` files

**Functions to preserve:**
- **Helper functions**: `stem_without_suffix`, `siblings`, QC routing functions
- **Discovery functions**: `g_tracked`, `g_sleap`, `g_scored`, `g_pose`
- **Utility functions**: `temp_path`, `with_root`, rebase logic
- **Diagnostic functions**: `sanity_checks`, `demo`, `_count`

## 🚀 **Phase 2: Per-Fly Capabilities**

### **Step 2.1: Implement Per-Fly Functions**
**File**: `_path/per_fly.py`

**New functions to implement:**
```python
def get_fly_data_path(fly_id: str, data_type: str) -> Path:
    """Get path to specific data type directory for a fly."""

def get_fly_column_file(fly_id: str, data_type: str, column: str) -> Path:
    """Get path to specific column file for a fly."""

def discover_flies() -> list[str]:
    """Discover all fly IDs from BASE_flyN directories in PostProcessing."""

def get_fly_status(fly_id: str) -> str:
    """Get processing status for a fly by checking available data directories."""

def get_fly_data_types(fly_id: str) -> list[str]:
    """Get available data types for a specific fly."""

def get_fly_columns(fly_id: str, data_type: str) -> list[str]:
    """Get available columns for a specific fly's data type."""

def get_fly_media_files(fly_id: str) -> dict[str, Path]:
    """Get media files (images, videos) for a specific fly."""
```

### **Step 2.2: Add BASE_flyN Pattern Handling**
**File**: `_path/per_fly.py`

**Pattern handling:**
- BASE_flyN directory discovery
- Fly ID extraction and validation
- Per-fly path construction
- Status tracking logic

### **Step 2.3: Create Fly Discovery and Status Functions**
**File**: `_path/per_fly.py`

**Discovery functions:**
- Scan PostProcessing for BASE_flyN directories
- Extract fly IDs from directory names
- Validate fly ID format

**Status functions:**
- Check available data types per fly
- Determine processing status
- Identify missing or incomplete data

### **Step 2.4: Test Per-Fly Functionality**
**Validation required:**
- All new per-fly functions work correctly
- BASE_flyN pattern handling works
- Fly discovery and status tracking work
- Integration with existing canonical paths

## 🚀 **Phase 3: Structural Changes**

### **Step 3.1: Merge BehaviorClassification → PostProcessing**
**Files to update:**
- All path builders in `_path/canonical.py`
- Error and flag path builders
- QC routing functions

**Changes required:**
- Update path builders for merged structure
- Ensure backward compatibility
- Test all path functions

### **Step 3.2: Implement Column-Based File Structure**
**File**: `_path/canonical.py`

**New path builders:**
- Per-fly data type directories (tracked/, sleap/, scored/, pose/)
- Column file paths within data type directories
- Media file paths within fly directories

### **Step 3.3: Update Path Builders for New Structure**
**File**: `_path/canonical.py`

**Updates required:**
- All 25+ path variables updated for new structure
- Support both old and new structures (hybrid approach)
- Column-based file access functions
- Per-fly directory handling

### **Step 3.4: Test Structural Changes**
**Validation required:**
- All path builders work with new structure
- Backward compatibility maintained
- Column-based access functions work
- Per-fly directory handling works

## 🚀 **Phase 4: Integration & Validation**

### **Step 4.1: Transform Main path.py File**
**File**: `Codes_Working/Config/path.py`

**Target structure:**
```python
# User constants and configuration
# Single configure() function
# Clean public API
# Immutable PATH bundle
```

**Target size**: ~200 lines (70% reduction from 647 lines)

### **Step 4.2: Comprehensive Validation**
**Validation required:**
- All 17 existing functions work identically
- All path constants preserved exactly
- All glob functions return same results
- All helper functions maintain behavior
- New per-fly functions work correctly
- Structural changes work properly

### **Step 4.3: Test Per-Fly Capabilities**
**Testing required:**
- Fly discovery functions work with BASE_flyN pattern
- Per-fly data access functions implemented
- Status tracking and parameter discovery
- Integration with existing canonical paths

### **Step 4.4: Verify Structural Changes**
**Verification required:**
- BehaviorClassification merged into PostProcessing
- Column-based file structure implemented
- BASE_flyN pattern properly handled
- All path builders updated for new structure

## 🎯 **Success Criteria**

### **✅ Functionality Preservation**
- All 17 existing functions work identically
- All path constants preserved exactly
- All glob functions return same results
- All helper functions maintain behavior

### **✅ Configuration Pattern**
- Main file reduced to ~200 lines (70% reduction)
- Single `configure()` call handles complexity
- Clean separation of user interface vs implementation
- Immutable PATH bundle with MappingProxyType

### **✅ Per-Fly Capabilities**
- Fly discovery functions work with BASE_flyN pattern
- Per-fly data access functions implemented
- Status tracking and parameter discovery
- Integration with existing canonical paths

### **✅ Structural Changes**
- BehaviorClassification merged into PostProcessing
- Column-based file structure implemented
- BASE_flyN pattern properly handled
- All path builders updated for new structure

## 🔧 **Implementation Best Practices**

### **1. Incremental Development**
- Implement one phase at a time
- Test thoroughly after each phase
- Maintain backward compatibility throughout

### **2. Comprehensive Testing**
- Test all existing functions
- Test new per-fly functions
- Test structural changes
- Test integration points

### **3. Documentation**
- Document all new functions
- Update existing documentation
- Maintain clear separation of concerns

### **4. Version Control**
- Commit after each successful phase
- Tag major milestones
- Maintain rollback capability

## 📝 **Key References**

- **Original File**: `Codes_Working/Config/path.py`
- **Pattern Examples**: `Codes/Config/experiment.py`, `Codes/Config/color.py`
- **QC Module**: `Codes_Before/BehaviorClassifier/_qc_error_flag.py`
- **Data Flow**: `.cursor/guides/project/data_flow.md`
- **Example Data**: `ExampleFiles/` directory

## 🚀 **Next Steps**

1. **📋 Review [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md)** - High-level overview
2. **🎯 Check [DECISIONS_LOG.md](DECISIONS_LOG.md)** - All decisions made
3. **📊 Analyze [TECHNICAL_ANALYSIS.md](TECHNICAL_ANALYSIS.md)** - Current state
4. **🏗️ Plan with [ARCHITECTURE_PLAN.md](ARCHITECTURE_PLAN.md)** - Future design
5. **📋 Execute this roadmap** - Step-by-step implementation

---

**This implementation roadmap provides detailed step-by-step guidance for the path.py refactoring project.**
