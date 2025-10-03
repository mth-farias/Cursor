# Config param.py Strategic Refactoring Plan

## 🎯 **Mission: Apply Configuration Pattern to param.py + Metadata Management**

Transform param.py using the proven configuration pattern, while handling the extensive validation logic, complex schema definitions, and **adding metadata management capabilities**. This makes param.py the comprehensive parameter and metadata registry.

## 📊 **Module Analysis**

### **Current Structure Analysis**

```
Codes_Before/Config/param.py:    714 lines, 6 cells
Codes_Working/Config/param.py:   917 lines, 6 cells (enhanced version)
```

### **Complexity Assessment**

- **Highest complexity**: Extensive validation logic, schema definitions
- **Critical importance**: Schema definitions affect entire pipeline
- **Risk level**: High - central to data validation throughout system
- **Dependencies**: None (standalone metadata module)
- **Processing**: Schema validation, domain checking, registry assembly, **metadata management**

### **Cell Structure Analysis**

```
CELL 00: Header & Overview (25 lines)
CELL 01: Imports (10 lines)
CELL 02: Schema Definition (20 lines) - ParamSpec TypedDict
CELL 03: BASE Parameters (30 lines) - Hardware counters, GPIO
CELL 04: SHARED Parameters (50 lines) - FrameIndex, Stimuli channels
CELL 05: TRACKED Parameters (200+ lines) - Position, orientation, motion
CELL 06: SLEAP Parameters (100+ lines) - Body parts, pose estimation
CELL 07: POSE Parameters (100+ lines) - Pose-derived features
CELL 08: SCORED Parameters (100+ lines) - Behavior classifications
CELL 09: Registry Assembly & Validation (200+ lines) - Complex validation logic
```

## 🏗️ **Configuration Pattern Application**

### **Target Architecture**

```
Codes/Config/
├── param.py                     # Main controller & user interface (250 lines)
└── _param/                      # Internal processing modules
    ├── __init__.py             # Configuration function & exports (100 lines)
    ├── constants.py            # Validation constants and policies (100 lines)
    ├── schemas.py              # Parameter schema definitions (300 lines)
    ├── validation.py           # Schema validation logic (200 lines)
    ├── domains.py              # Domain checking and constraints (150 lines)
    ├── registry.py             # Registry assembly and processing (100 lines)
    ├── metadata.py             # Metadata management and QC status (150 lines)
    └── report.py               # Parameter documentation reports (80 lines)
```

### **User Constants (Stay in main param.py)**

```python
# From CELL 02-08 - All parameter definitions:
BASE = {
    "GPIO": {
        "label": "GPIO State",
        "tags": ["BASE"],
        "type": "int",
        # ... complete parameter spec
    },
    # ... all BASE parameters
}

SHARED = {
    "FrameIndex": {
        "label": "Frame Index", 
        # ... complete parameter spec
    },
    # ... all SHARED parameters
}

TRACKED = {
    # ... all TRACKED parameters
}

SLEAP = {
    # ... all SLEAP parameters  
}

POSE = {
    # ... all POSE parameters
}

SCORED = {
    # ... all SCORED parameters
}

# Validation policies and constraints
VALIDATION_POLICIES = {
    "strict_domain_checking": True,
    "allow_unknown_columns": False,
    # ... other validation policies
}

# Metadata management policies
METADATA_POLICIES = {
    "pipeline_version": "2.0",
    "status_tracking": True,
    "qc_reporting": True,
    # ... other metadata policies
}
```

### **Configuration Function Design**

```python
# _param/__init__.py
def configure(
    base_params,
    shared_params,
    tracked_params,
    sleap_params,
    pose_params,
    scored_params,
    validation_policies,
    metadata_policies
):
    """Configure all parameter modules with user definitions."""
    global _CONSTANTS, _SCHEMAS, _VALIDATION, _DOMAINS, _REGISTRY, _METADATA
    
    # Step 1: Create validation constants bundle
    constants_bundle = constants.create_constants_bundle(validation_policies)
    
    # Step 2: Create schema definitions bundle
    schemas_bundle = schemas.create_schemas_bundle(
        base_params, shared_params, tracked_params, 
        sleap_params, pose_params, scored_params
    )
    
    # Step 3: Create validation logic bundle (needs schemas and constants)
    validation_bundle = validation.create_validation_bundle(
        schemas_bundle, constants_bundle
    )
    
    # Step 4: Create domain checking bundle (needs schemas)
    domains_bundle = domains.create_domains_bundle(schemas_bundle)
    
    # Step 5: Create registry assembly bundle (needs all previous)
    registry_bundle = registry.create_registry_bundle(
        schemas_bundle, validation_bundle, domains_bundle
    )
    
    # Step 6: Create metadata management bundle (new!)
    metadata_bundle = metadata.create_metadata_bundle(metadata_policies)
    
    # Step 7: Update module-level variables
    _CONSTANTS = constants_bundle
    _SCHEMAS = schemas_bundle
    _VALIDATION = validation_bundle
    _DOMAINS = domains_bundle
    _REGISTRY = registry_bundle
    _METADATA = metadata_bundle
```

## 📋 **Detailed Implementation Plan**

### **Phase 1: Create Internal Module Structure**

#### **Step 1.1: Create _param/constants.py**

```python
# Move validation constants and policies:
- Validation policy definitions
- Domain checking constants
- Error message templates
- Type checking utilities

# Functions to create:
def create_constants_bundle(validation_policies):
    # Process validation policies and create constants
    return MappingProxyType({
        "VALIDATION_POLICIES": processed_policies,
        "ERROR_TEMPLATES": error_templates,
        "TYPE_VALIDATORS": type_validators,
        # ... other validation constants
    })
```

#### **Step 1.2: Create _param/schemas.py**

```python
# Move from CELL 03-08 processing:
- Parameter schema definitions
- ParamSpec TypedDict processing
- Schema organization by category
- Schema inheritance and composition

# NEW: Add parameter schema export function
def get_parameter_schemas() -> dict[str, list[str]]:
    """
    Get parameter schemas for all data types.
    This is called by path.py to get parameter lists.
    """
    try:
        # Try to get from refactored schemas
        return {
            "BASE": list(BASE.keys()),
            "TRACKED": list(TRACKED.keys()),
            "SCORED": list(SCORED.keys()),
            "SLEAP": list(SLEAP.keys()),
            "POSE": list(POSE.keys()),
        }
    except (NameError, AttributeError):
        # Fallback parameter lists (internal to param.py)
        return {
            "BASE": ["GPIO", "FrameID", "Timestamp"],
            "TRACKED": ["FrameIndex", "VisualStim", "Stim0", "Stim1", 
                       "NormalizedCentroidX", "NormalizedCentroidY", "PixelChange"],
            "SCORED": ["FrameIndex", "VisualStim", "Stim0", "Stim1",
                      "Position_X", "Position_Y", "Motion", 
                      "Speed", "Speed_Denoised",
                      "Layer1", "Layer1_Denoised", "Layer2", "Layer2_Denoised",
                      "Resistant", "Resistant_Denoised", "Behavior", "Behavior_Denoised"],
            "SLEAP": ["FrameIndex", "Head_Position_X", "Head_Position_Y", 
                     "Head_Confidence", "Thorax_Position_X", "Thorax_Position_Y"],
            "POSE": ["FrameIndex", "Orientation", "View", "View_X", "View_Y",
                    "Head_X", "Head_Y", "Thorax_X", "Thorax_Y", 
                    "Abdomen_X", "Abdomen_Y", "LeftWing_X", "LeftWing_Y", 
                    "RightWing_X", "RightWing_Y"]
        }

# Functions to create:
def create_schemas_bundle(base, shared, tracked, sleap, pose, scored):
    # Organize and process all parameter schemas
    return MappingProxyType({
        "BASE_SCHEMAS": processed_base_schemas,
        "SHARED_SCHEMAS": processed_shared_schemas,
        "TRACKED_SCHEMAS": processed_tracked_schemas,
        "SLEAP_SCHEMAS": processed_sleap_schemas,
        "POSE_SCHEMAS": processed_pose_schemas,
        "SCORED_SCHEMAS": processed_scored_schemas,
        "ALL_SCHEMAS": combined_schemas,
        "get_parameter_schemas": get_parameter_schemas,  # NEW!
        # ... other schema collections
    })
```

#### **Step 1.3: Create _param/validation.py**

```python
# Move from CELL 09 validation logic:
- Schema validation functions
- Type checking logic
- Domain validation
- Error reporting and formatting

# Functions to create:
def create_validation_bundle(schemas_bundle, constants_bundle):
    # Create all validation functions
    return MappingProxyType({
        "validate_schema": validation_function,
        "validate_types": type_validation_function,
        "validate_domains": domain_validation_function,
        "format_validation_errors": error_formatting_function,
        # ... other validation functions
    })
```

#### **Step 1.4: Create _param/domains.py**

```python
# Move domain checking logic:
- Domain constraint definitions
- Value range checking
- Categorical value validation
- Custom domain validators

# Functions to create:
def create_domains_bundle(schemas_bundle):
    # Create domain checking utilities
    return MappingProxyType({
        "check_domain_constraints": domain_checker,
        "validate_categorical_values": categorical_validator,
        "validate_continuous_ranges": range_validator,
        # ... other domain utilities
    })
```

#### **Step 1.5: Create _param/registry.py**

```python
# Move registry assembly logic:
- Parameter registry construction
- Schema merging and organization
- Registry validation and consistency checking
- Final registry assembly

# Functions to create:
def create_registry_bundle(schemas, validation, domains):
    # Assemble final parameter registry
    return MappingProxyType({
        "PARAM_REGISTRY": assembled_registry,
        "validate_registry": registry_validator,
        "get_schema_by_name": schema_lookup,
        # ... other registry utilities
    })
```

#### **Step 1.6: Create _param/metadata.py (NEW!)**

```python
# NEW: Metadata management for fly processing status and QC
- Fly processing status tracking
- QC error and flag report management
- Processing timestamps and pipeline versioning
- Metadata creation and update functions

# Functions to create:
def create_metadata_bundle(metadata_policies):
    """Create metadata management bundle."""
    
    def create_fly_metadata(fly_id: str, status: str = "processing") -> dict:
        """Create clean metadata structure for a fly."""
        return {
            "fly_id": f"fly{fly_id}",
            "status": status,  # "ok", "error", "flagged", "processing"
            "created_at": datetime.now().isoformat(),
            "pipeline_version": metadata_policies.get("pipeline_version", "2.0"),
            "processing_time_seconds": None,
            "data_folders": ["base", "tracked", "sleap", "scored", "pose"],
            "media_files": ["arenaimg.png", "flyvideo.avi", "cropvideo.avi"]
        }
    
    def update_fly_status(fly_id: str, status: str, **kwargs) -> None:
        """Update fly processing status and metadata."""
        # Implementation here - handles QC status updates
        # This would integrate with path.py for metadata file paths
        pass
    
    def generate_qc_reports() -> tuple[pd.DataFrame, pd.DataFrame]:
        """Generate QC reports from fly metadata."""
        # Implementation here - generates error and flag reports
        # This preserves the REPORT functionality from original system
        pass
    
    def load_fly_metadata(fly_id: str) -> dict:
        """Load fly processing metadata and QC status."""
        # Implementation here - loads from metadata.json files
        pass
    
    def get_fly_status(fly_id: str) -> str:
        """Get processing status: 'ok', 'error', or 'flagged'."""
        metadata = load_fly_metadata(fly_id)
        return metadata["status"]
    
    return MappingProxyType({
        "create_fly_metadata": create_fly_metadata,
        "update_fly_status": update_fly_status,
        "generate_qc_reports": generate_qc_reports,
        "load_fly_metadata": load_fly_metadata,
        "get_fly_status": get_fly_status,
    })
```

#### **Step 1.7: Create _param/report.py**

```python
# Move reporting logic:
- Parameter documentation generation
- Schema summary reports
- Validation status reports
- Human-readable parameter descriptions

# Functions to create:
def create_report_bundle():
    # Create reporting functions
    return MappingProxyType({
        "render_param_report": report_function,
        "generate_schema_summary": summary_function,
        "create_validation_report": validation_report,
        # ... other report functions
    })
```

### **Phase 2: Transform Main param.py File**

#### **Step 2.1: Clean Main File Structure**

```python
#%% CELL 00 — HEADER & OVERVIEW
"""
Clean overview focused on parameter registry, validation, and metadata management.
"""

#%% CELL 01 — IMPORTS & TYPES
from __future__ import annotations
import sys
from pathlib import Path
from types import MappingProxyType
from typing import TypedDict, Literal, Any

# Package path setup (for safe absolute imports)
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Config import _param

# Keep ParamSpec in main file for user reference
class ParamSpec(TypedDict, total=False):
    label: str
    tags: list[str]
    type: Literal["int","float","string","bool"]
    unit: str | None
    role: Literal["binary","categorical","continuous"]
    domain: list[Any] | None
    description: str

#%% CELL 02 — USER INPUT
"""
Authoritative parameter definitions and metadata policies. Edit these only.
"""
# All parameter definitions from original CELL 03-08
BASE = {...}
SHARED = {...}
TRACKED = {...}
SLEAP = {...}
POSE = {...}
SCORED = {...}

VALIDATION_POLICIES = {...}

# NEW: Metadata management policies
METADATA_POLICIES = {
    "pipeline_version": "2.0",
    "status_tracking": True,
    "qc_reporting": True,
    "auto_metadata_creation": True,
}

#%% CELL 03 — CONFIGURATION
"""
Single function call handles all parameter processing complexity and metadata setup.
"""
_param.configure(
    BASE,
    SHARED, 
    TRACKED,
    SLEAP,
    POSE,
    SCORED,
    VALIDATION_POLICIES,
    METADATA_POLICIES  # NEW!
)

#%% CELL 04 — PUBLIC API ASSEMBLY
"""
Clean assembly from configured bundles.
"""
_PUBLIC = {
    # User inputs
    "BASE": BASE,
    "SHARED": SHARED,
    "TRACKED": TRACKED,
    "SLEAP": SLEAP,
    "POSE": POSE,
    "SCORED": SCORED,
    "VALIDATION_POLICIES": VALIDATION_POLICIES,
    "METADATA_POLICIES": METADATA_POLICIES,  # NEW!
    
    # Processed results from internal modules
    **_param._SCHEMAS,
    **_param._VALIDATION,
    **_param._DOMAINS,
    **_param._REGISTRY,
    **_param._METADATA,  # NEW!
}

PARAM = MappingProxyType(_PUBLIC)
__all__ = ["PARAM", "ParamSpec"]

#%% CELL 05 — REPORT
if __name__ == "__main__":
    _param._REPORT["render_param_report"](PARAM)
```

### **Phase 3: Handle Special Considerations**

#### **Complex Validation Logic**

- **Challenge**: Extensive validation with complex interdependencies
- **Solution**: Isolate validation logic in _param/validation.py
- **Validation**: Test all validation scenarios and error conditions

#### **Schema Interdependencies**

- **Challenge**: Parameters reference each other across categories
- **Solution**: Handle dependencies in configure() function
- **Validation**: Test schema consistency and cross-references

#### **Critical System Importance**

- **Challenge**: Parameter definitions affect entire pipeline
- **Solution**: Comprehensive validation and testing
- **Validation**: Test with real data and edge cases

#### **Performance Considerations**

- **Challenge**: Validation logic must be fast for large datasets
- **Solution**: Optimize validation functions, maintain performance
- **Validation**: Benchmark validation performance

#### **Metadata Integration (NEW!)**

- **Challenge**: Metadata management must integrate with path.py
- **Solution**: Clean API between param.py and path.py
- **Validation**: Test metadata operations with path operations

## 🧪 **Validation Strategy**

### **Schema Validation**

```python
# Test all parameter schemas match exactly
def test_parameter_schemas():
    original_params = load_original_param_system()
    refactored_params = load_refactored_param_system()
    
    for category in ["BASE", "SHARED", "TRACKED", "SLEAP", "POSE", "SCORED"]:
        original_category = original_params[category]
        refactored_category = refactored_params[category]
        
        assert original_category == refactored_category
```

### **Validation Logic Testing**

```python
# Test validation functions work identically
def test_validation_functions():
    # Test with valid data
    # Test with invalid data
    # Test error message formatting
    # Test edge cases and boundary conditions
```

### **Registry Assembly Testing**

```python
# Test registry assembly produces identical results
def test_registry_assembly():
    # Test registry structure
    # Test schema lookup functions
    # Test validation integration
    # Test performance characteristics
```

### **Metadata Management Testing (NEW!)**

```python
# Test metadata operations
def test_metadata_operations():
    # Test metadata creation
    # Test status updates
    # Test QC report generation
    # Test integration with path operations
```

## ⚠️ **Risk Assessment & Mitigation**

### **Critical Risk Areas**

1. **Validation logic complexity**: Most complex validation in entire system

   - **Mitigation**: Extensive testing, incremental implementation, preserve exact logic

2. **Schema interdependencies**: Complex relationships between parameter categories

   - **Mitigation**: Map dependencies carefully, test all combinations

3. **System-wide impact**: Changes affect entire data pipeline

   - **Mitigation**: Comprehensive validation, test with real data

4. **Metadata integration**: New functionality must integrate cleanly

   - **Mitigation**: Clean API design, test integration points

### **High Risk Areas**

1. **Performance impact**: Validation must remain fast

   - **Mitigation**: Benchmark performance, optimize critical paths

2. **Error handling**: Complex error reporting and formatting

   - **Mitigation**: Test all error conditions, preserve error messages

### **Mitigation Strategies**

- **Incremental implementation**: Test each component before integration
- **Comprehensive validation**: Test with real data and edge cases
- **Performance monitoring**: Ensure no regression in validation speed
- **Exact logic preservation**: Maintain identical validation behavior
- **Clean API design**: Ensure metadata operations integrate smoothly

## 📊 **Success Metrics**

### **Target Outcomes**

- **Line reduction**: 917 → ~250 lines in main file (73% reduction)
- **Functionality preservation**: 100% (all schemas, validation, registry identical)
- **Performance maintenance**: No regression in validation speed
- **Error handling**: All error conditions and messages preserved
- **Schema integrity**: All parameter definitions exactly preserved
- **Metadata functionality**: Complete metadata management capabilities

### **Validation Criteria**

- [ ] All parameter schemas match exactly
- [ ] All validation functions produce identical results
- [ ] All error conditions and messages preserved
- [ ] Registry assembly produces identical structure
- [ ] Performance maintained or improved
- [ ] Integration with pipeline components works perfectly
- [ ] Metadata operations work correctly
- [ ] Integration with path.py is seamless

## 🎯 **Implementation Timeline**

### **Week 1: Deep Analysis & Risk Assessment**

- Comprehensive analysis of validation logic complexity
- Map all schema interdependencies and relationships
- Create detailed validation baseline and test data
- Assess performance requirements and benchmarks
- Design metadata integration with path.py

### **Week 2: Internal Module Creation**

- Create _param/ package structure with focus on validation preservation
- Implement constants.py and schemas.py with exact schema preservation
- Test schema processing and organization
- Implement get_parameter_schemas() function for path.py integration

### **Week 3: Validation Logic Implementation**

- Implement validation.py with exact logic preservation
- Implement domains.py with comprehensive domain checking
- Test all validation scenarios and error conditions
- Implement metadata.py with fly status and QC management

### **Week 4: Integration & Registry Assembly**

- Create configure() function with dependency handling
- Implement registry.py with exact assembly logic
- Transform main param.py file
- Test metadata integration with path operations

### **Week 5: Comprehensive Validation & Optimization**

- Comprehensive validation testing with real data
- Performance optimization and benchmarking
- Metadata operation testing and optimization
- Final validation and documentation

## 🏗️ **Architecture Benefits**

### **✅ What We've Added**

1. **Metadata management** - Fly processing status, QC reports, timestamps
2. **Parameter schema export** - Clean API for path.py integration
3. **QC report generation** - Preserves REPORT functionality from original system
4. **Processing status tracking** - Individual fly status management
5. **Pipeline versioning** - Version tracking for processing runs

### **✅ Architecture Improvements**

- **Logical organization** - All parameter-related functionality in param.py
- **Clean separation** - param.py for parameters/metadata, path.py for paths
- **Better maintainability** - Metadata management centralized
- **Scientific workflow support** - QC status tracking for individual flies

This plan treats param.py as the most critical and complex module, requiring the most careful implementation of the configuration pattern while preserving the extensive validation logic that is central to the entire pipeline's data integrity, and adding comprehensive metadata management capabilities.