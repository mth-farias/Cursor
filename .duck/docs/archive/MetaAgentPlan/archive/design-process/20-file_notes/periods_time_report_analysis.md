# Time and Period Management Analysis

## Files Analyzed
- `Codes/Config/_experiment/periods.py`
- `Codes/Config/_experiment/time.py` 
- `Codes/Config/_experiment/report.py`

## Key Patterns Identified

### 1. **Period Validation and Enrichment Pattern** (`periods.py`)

**Architecture:**
- **CELL 02**: Period validation and enrichment logic
- **CELL 03**: Public API with immutable bundle creation
- **Input**: User-defined period specifications with durations
- **Processing**: Validates durations, computes frame counts, builds deterministic ordering arrays
- **Output**: Complete period bundle with derived structures

**Key Features:**
- Validates period durations are positive and finite
- Computes frame durations and cumulative timing
- Creates contiguous period boundaries (half-open intervals)
- Builds derived structures for fast period queries
- Uses `MappingProxyType` for immutable bundle export

**Validation Logic:**
```python
# Contiguity: next start == previous end
if not np.all(period_starts[1:] == period_ends_exclusive[:-1]):
    raise ValueError("Periods are not contiguous (gaps or overlaps detected).")

# Durations must be positive and strictly increasing
if not (np.all(period_dur_frames > 0) and np.all(np.diff(period_ends_exclusive) > 0)):
    raise ValueError("Invalid period durations or ordering.")
```

### 2. **Time Conversion and Query Pattern** (`time.py`)

**Architecture:**
- **CELL 02**: Time conversion functions
- **CELL 03**: Period query functions
- **CELL 04**: Public API with conditional bundle creation

**Key Features:**
- Seconds↔frames conversions with NumPy array support
- Fast period query functions using `np.searchsorted`
- Vectorized operations for performance
- Half-open interval semantics for period membership

**Time Conversion:**
```python
def seconds_to_frames(seconds) -> int | np.ndarray:
    arr = np.asarray(seconds)
    frames = np.rint(arr * frame_rate).astype(int)  # round to nearest int
    return int(frames) if np.isscalar(seconds) else frames
```

**Period Query:**
```python
def period_by_frame(frame: int) -> str:
    if frame < 0 or frame >= experiment_total_frames:
        return "OutOfRange"
    idx = int(np.searchsorted(period_ends_exclusive, frame, side="right"))
    return period_order[idx]
```

### 3. **Report Generation Pattern** (`report.py`)

**Architecture:**
- **CELL 02**: Report functions
- **CELL 03**: Public API with immutable bundle

**Key Features:**
- Human-readable summaries of experiment bundles
- Formatted display functions for periods and stimuli
- Clean separation between data and presentation logic
- Immutable bundle export pattern

**Report Structure:**
```python
def render_experiment_report(experiment_bundle: MappingProxyType) -> None:
    print("=== EXPERIMENT SUMMARY ===\n")
    print("Noise tolerance:", experiment_bundle["NOISE_TOLERANCE"], "frames")
    print("Frame rate:", experiment_bundle["FRAME_RATE"], "fps")
    # ... detailed period and stimulus information
```

## Integration with Configuration Pattern

### Bundle Composition
- Each module creates its own immutable bundle
- Main controller composes bundles into final EXPERIMENT bundle
- Clean dependency management through function parameters

### Validation Pipeline
- Input validation at module level
- Cross-module validation in main controller
- Comprehensive error reporting with specific messages

### Performance Optimization
- O(1) lookups using pre-computed arrays
- Vectorized operations with NumPy
- Efficient memory usage with immutable structures

## Duck Integration Insights

### 1. **Time Management Mastery**
Duck must understand:
- Frame-based time systems
- Conversion between time domains
- Efficient query patterns for temporal data

### 2. **Validation Patterns**
Duck should implement:
- Input validation with clear error messages
- Cross-module consistency checks
- Performance-optimized validation pipelines

### 3. **Report Generation**
Duck needs:
- Human-readable output formatting
- Structured data presentation
- Clean separation of logic and presentation

### 4. **Bundle Architecture**
Duck must master:
- Immutable bundle creation
- Conditional bundle composition
- Performance-optimized data structures

## Scientific Rigor Standards

### Validation Completeness
- All inputs validated for type and range
- Cross-module consistency enforced
- Clear error messages for debugging

### Performance Optimization
- O(1) lookup operations
- Vectorized computations
- Memory-efficient data structures

### Documentation Standards
- Clear function documentation
- Type hints throughout
- Comprehensive docstrings

## Pattern Recognition

### Time Domain Management
- **Pattern**: Frame-based time systems with conversion utilities
- **Evidence**: `seconds_to_frames`, `frames_to_seconds` functions
- **Architecture**: Centralized time conversion with experiment context

### Period Management
- **Pattern**: Contiguous period validation with derived structures
- **Evidence**: Period boundary computation and validation logic
- **Architecture**: Immutable period bundles with fast query support

### Report Generation
- **Pattern**: Human-readable data presentation
- **Evidence**: Formatted output functions and structured display
- **Architecture**: Clean separation of data and presentation logic

## Implementation Insights

### 1. **NumPy Integration**
- Extensive use of NumPy for performance
- Vectorized operations for efficiency
- Proper handling of scalar vs array inputs

### 2. **Error Handling**
- Specific error messages for debugging
- Validation at multiple levels
- Graceful handling of edge cases

### 3. **Memory Management**
- Immutable structures for data integrity
- Efficient array operations
- Minimal memory overhead

### 4. **API Design**
- Clean function interfaces
- Consistent parameter naming
- Logical function grouping

## Duck Development Priorities

### High Priority
1. **Time Management**: Master frame-based time systems
2. **Validation Patterns**: Implement comprehensive validation
3. **Bundle Architecture**: Understand immutable bundle patterns

### Medium Priority
1. **Report Generation**: Learn structured data presentation
2. **Performance Optimization**: Understand O(1) lookup patterns
3. **Error Handling**: Master specific error messaging

### Low Priority
1. **NumPy Integration**: Advanced vectorized operations
2. **Memory Management**: Optimization techniques
3. **API Design**: Interface consistency patterns
