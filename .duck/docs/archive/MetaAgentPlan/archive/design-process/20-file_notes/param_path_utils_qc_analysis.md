# Parameter, Path, Utils, and QC System Analysis

## Files Analyzed
- `Codes_Before/Config/param.py`
- `Codes_Before/Config/path.py`
- `Codes_Before/BehaviorClassifier/_utils.py`
- `Codes_Before/BehaviorClassifier/_qc_error_flag.py`

## Key Patterns Identified

### 1. **Parameter Registry Pattern** (`param.py`)

**Architecture:**
- **CELL 02**: Schema definition with TypedDict
- **CELL 03-08**: Parameter registries by file type (BASE, SHARED, TRACKED, SLEAP, POSE, SCORED)
- **CELL 09**: Public API with immutable bundle creation

**Key Features:**
- Canonical registry of all CSV parameters across the pipeline
- Comprehensive metadata for each parameter (label, tags, type, unit, role, domain, description)
- Single source of truth for parameter documentation
- Validation of CSV columns at load time
- Generation of human-readable reports

**Parameter Schema:**
```python
class ParamSpec(TypedDict, total=False):
    label: str           # Human-readable name for reports/UI
    tags: list[str]      # Provenance tags (BASE, tracked, sleap, pose, scored, stimuli)
    type: Literal["int","float","string","bool"]  # Primitive storage type
    unit: str | None     # Physical/logical unit (frames, sec, mm, deg, px, etc.)
    role: Literal["binary","categorical","continuous"]  # Semantic role
    domain: list[Any] | None  # Legal values or [min,max] or None if unbounded
    description: str     # One-line explanation of the column
```

### 2. **Path Management System** (`path.py`)

**Architecture:**
- **CELL 02**: Root path definition and join helper
- **CELL 03-08**: Path constants and helper functions
- **CELL 09**: Public API with immutable bundle creation

**Key Features:**
- Canonical experiment folder map and filename API
- Single source of truth for folder names and file suffixes
- Pure path math (no filesystem I/O) for easy testing
- Stable names with clear constants
- Comprehensive folder tree declaration

**Path Structure:**
```
ExperimentalFolder/
├─ Codes/ (Config, BehaviorClassifier)
├─ Bonfly/ (Bonsai, FlyHigher-Protocol, FlyHigher-Tracker)
├─ RawData/ (BASE.avi, BASE.csv)
├─ PostProcessing/ (Tracked, Sleap, ArenaImage, FlyVideo, CropVideo)
└─ BehaviorClassification/ (Scored, Pose, Error, Flag)
```

### 3. **Shared Utilities Pattern** (`_utils.py`)

**Architecture:**
- **CELL 02**: Binary stimulus detection and processing
- **CELL 03**: Labels and runs utilities
- **CELL 04**: Motion processing
- **CELL 05**: Geometry and kinematics
- **CELL 06**: Pose view selection
- **CELL 07**: Alignment operations
- **CELL 08**: I/O primitives
- **CELL 09**: Public export

**Key Features:**
- Shared, policy-light mechanics for BehaviorClassifier modules
- Stateless helpers with minimal defaults from Config
- NumPy/Pandas-friendly surfaces
- Series in → Series out (index preserved)
- Centralized generic helpers without policy decisions

**Core Utilities:**
- **Stimulus Processing**: Detection mapping, onsets, pulse durations, cleaners
- **Label Management**: Prefix utilities, run-length iteration
- **Motion Analysis**: PixelChange → Motion conversion
- **Geometry**: Normalized coordinates ↔ mm conversion, speed calculation
- **Pose Selection**: View selection from confidence scores
- **Alignment**: Crop alignment arithmetic and slicing
- **I/O**: Atomic CSV writer with tmp → fsync → replace pattern

### 4. **Quality Control System** (`_qc_error_flag.py`)

**Architecture:**
- **CELL 02**: QC constants and thresholds
- **CELL 03-08**: Pre-flight error checks and post-classification flag checks
- **CELL 09**: Public API with immutable bundle creation

**Key Features:**
- Centralized Quality Control for the behavior pipeline
- Pre-flight errors (fatal, stop on first failure)
- Post-classification flags (non-fatal, log all)
- REPORT persistence and flagged dataframe saving
- Comprehensive validation with specific error codes

**Pre-flight Error Checks:**
1. **Schema/Readability**: Required columns present and readable
2. **Stimulus Count**: Expected onsets match observed
3. **Stimulus Duration**: Pulse durations within tolerance
4. **Timeline Alignment**: Cross-period consistency
5. **Centroid NaN Fraction**: Under threshold
6. **Pose Presence**: SLEAP file present when required
7. **Pose Length Match**: Tracked and SLEAP lengths match

**Post-classification Flag Checks:**
- **Baseline Exploration**: Too low activity
- **Behavior NaN Fraction**: Too high missing data
- **Pose View NaN Fraction**: Too high missing pose data

## Integration with Configuration Pattern

### 1. **Registry Integration**
- All modules use Config bundles (PATH, PARAM, EXPERIMENT)
- Read-only access through MappingProxyType
- Single source of truth for all configuration

### 2. **Validation Pipeline**
- Parameter validation at load time
- Path validation through canonical structure
- QC validation through comprehensive checks
- Error reporting with specific codes and metrics

### 3. **Bundle Architecture**
- Immutable bundles for all configuration
- Clean separation of concerns
- Comprehensive API exposure

## Advanced Patterns

### 1. **TypedDict Schema Pattern**
```python
class ParamSpec(TypedDict, total=False):
    # Comprehensive metadata for each parameter
    # Type safety with runtime validation
    # Extensible schema for future parameters
```

### 2. **Path Math Pattern**
```python
# Pure path operations without filesystem I/O
# Easy testing and validation
# Stable constants for all path operations
```

### 3. **Atomic Operations Pattern**
```python
# Atomic CSV writer: tmp → fsync → replace
# Ensures data integrity during writes
# Prevents partial file corruption
```

### 4. **Validation Pipeline Pattern**
```python
# Pre-flight: Fatal errors, stop on first failure
# Post-class: Non-fatal flags, log all
# Comprehensive error reporting with metrics
```

## Scientific Rigor Standards

### 1. **Parameter Documentation**
- Every parameter has comprehensive metadata
- Clear units, types, and semantic roles
- Bounded domains where applicable
- Human-readable descriptions

### 2. **Path Consistency**
- Canonical folder structure
- Stable naming conventions
- Clear separation of concerns
- Easy testing and validation

### 3. **Quality Assurance**
- Comprehensive validation at multiple levels
- Specific error codes and messages
- Metrics collection for debugging
- Graceful error handling

### 4. **Data Integrity**
- Atomic file operations
- Immutable configuration bundles
- Read-only access patterns
- Validation at every stage

## Duck Integration Insights

### 1. **Parameter Management Mastery**
Duck must understand:
- Comprehensive parameter metadata systems
- Type-safe schema definitions
- Validation and documentation patterns
- Registry-based configuration management

### 2. **Path Management Systems**
Duck should implement:
- Canonical folder structures
- Pure path math operations
- Stable naming conventions
- Easy testing and validation

### 3. **Utility Architecture**
Duck needs:
- Stateless helper functions
- Policy-light mechanics
- NumPy/Pandas-friendly surfaces
- Clean separation of concerns

### 4. **Quality Control Systems**
Duck must master:
- Multi-level validation pipelines
- Comprehensive error reporting
- Atomic operations
- Graceful error handling

## Pattern Recognition

### 1. **Registry-Based Configuration**
- **Pattern**: Centralized parameter registries with comprehensive metadata
- **Evidence**: `param.py` shows TypedDict schemas and parameter registries
- **Architecture**: Single source of truth with validation and documentation

### 2. **Path Math Systems**
- **Pattern**: Pure path operations without filesystem I/O
- **Evidence**: `path.py` demonstrates canonical folder structures and stable constants
- **Architecture**: Easy testing and validation with clear separation

### 3. **Utility Architecture**
- **Pattern**: Stateless helpers with policy-light mechanics
- **Evidence**: `_utils.py` shows shared utilities without policy decisions
- **Architecture**: Clean separation of concerns with NumPy/Pandas integration

### 4. **Quality Control Pipeline**
- **Pattern**: Multi-level validation with comprehensive error reporting
- **Evidence**: `_qc_error_flag.py` demonstrates pre-flight and post-class validation
- **Architecture**: Atomic operations with graceful error handling

## Implementation Insights

### 1. **Type Safety**
- Extensive use of TypedDict for schema definition
- Type hints throughout all modules
- Runtime validation with clear error messages

### 2. **Error Handling**
- Specific error codes and messages
- Comprehensive metrics collection
- Graceful degradation and recovery

### 3. **Performance Optimization**
- Pure path math for efficiency
- Stateless utilities for reusability
- Atomic operations for data integrity

### 4. **Documentation Standards**
- Comprehensive parameter metadata
- Clear function documentation
- Human-readable descriptions

## Duck Development Priorities

### High Priority
1. **Parameter Management**: Master registry-based configuration
2. **Path Systems**: Understand canonical folder structures
3. **Quality Control**: Implement comprehensive validation pipelines

### Medium Priority
1. **Utility Architecture**: Learn stateless helper patterns
2. **Type Safety**: Understand TypedDict schemas
3. **Error Handling**: Master specific error reporting

### Low Priority
1. **Performance Optimization**: Advanced path math techniques
2. **Documentation**: Comprehensive metadata systems
3. **Testing**: Validation and testing patterns

## Scientific Excellence Features

### 1. **Reproducibility**
- Canonical parameter definitions
- Stable path structures
- Comprehensive validation

### 2. **Transparency**
- Clear documentation
- Specific error messages
- Comprehensive metadata

### 3. **Validation**
- Multi-level validation pipelines
- Type safety throughout
- Runtime validation

### 4. **Performance**
- Pure path math operations
- Stateless utilities
- Atomic operations
