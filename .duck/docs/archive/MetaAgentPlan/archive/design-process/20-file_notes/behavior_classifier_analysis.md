# Behavior Classification System Analysis

## Files Analyzed
- `Codes_Before/BehaviorClassifier/_main.py`
- `Codes_Before/BehaviorClassifier/_classifier.py`

## Key Patterns Identified

### 1. **Orchestration Pattern** (`_main.py`)

**Architecture:**
- **CELL 01**: Imports and package shim
- **CELL 02**: Session setup and error codes
- **CELL 03**: Per-file conveyor (end-to-end processing)
- **CELL 04**: Session runner with progress tracking
- **CELL 05**: Public surface (zero-arg entry point)
- **CELL 06**: Read-only public surface

**Key Features:**
- Skinny orchestrator with no business rules
- Delegates to dedicated components
- Maintains session counters and summary
- Atomic file operations with error handling
- Progress tracking with real-time updates

**Processing Pipeline:**
```python
def _process_one(tracked_path: Path) -> tuple[str, str | None, int | None]:
    # 03.1 Load tracked CSV
    # 03.2 Clean stimuli (in place)
    # 03.3 Pre-flight QC (fatal)
    # 03.4 Minimal features
    # 03.5 Classification (all layers)
    # 03.6 Pose/SLEAP scoring
    # 03.7 Align/crop to experiment window
    # 03.8 Post-class QC flags (non-fatal)
    # 03.9 Publish Scored (atomic)
    # 03.10 Publish Pose (separate artifact)
```

### 2. **Classification Algorithm Pattern** (`_classifier.py`)

**Architecture:**
- **CELL 02**: Knobs and constants (user input)
- **CELL 03**: Internal helpers
- **CELL 04**: Layer 1 classification
- **CELL 05**: Layer 2 classification
- **CELL 06**: Resistant classification
- **CELL 07**: Final behavior publishers
- **CELL 08**: Public surface and execution guard

**Key Features:**
- Multi-layer classification pipeline
- Denoising and smoothing algorithms
- Resistant behavior detection
- Comprehensive validation and error handling
- Performance-optimized implementations

**Classification Pipeline:**
```python
# Layer 1: Raw kinematics → basic behaviors
df = BC_CLASSIFIER["classify_layer1"](df)
df = BC_CLASSIFIER["classify_layer1_denoised"](df)

# Layer 2: Local consensus → refined behaviors
df = BC_CLASSIFIER["classify_layer2"](df)
df = BC_CLASSIFIER["classify_layer2_denoised"](df)

# Resistant: Stimulus-coupled → specialized behaviors
df = BC_CLASSIFIER["classify_resistant_behaviors"](df)
df = BC_CLASSIFIER["classify_resistant_behaviors_denoised"](df)

# Final: Behavior domain mapping
df = BC_CLASSIFIER["classify_behavior"](df)
df = BC_CLASSIFIER["classify_behavior_denoised"](df)
```

## Advanced Algorithm Patterns

### 1. **Speed Smoothing with Guards**
```python
def _smooth_speed_centered_array_for_speed_denoise(
    speed_mm_per_s: np.ndarray,
    *,
    is_response: np.ndarray | None = None,
) -> np.ndarray:
    # High-speed guard: preserve jump-level speeds
    # Response window guard: avoid smoothing during stimuli
    # Only average non-guarded, non-NaN samples
```

### 2. **Micro-bout Deletion**
```python
def _classify_layer1_denoised_array(layer1_like_labels: np.ndarray) -> np.ndarray:
    # Delete short runs (≤ tolerance) of Walk/Stationary/Freeze
    # Preserve Jump bouts (never deleted)
    # Maintain temporal continuity
```

### 3. **Resistant Behavior Detection**
```python
def _label_resistant(layer2_like_labels: np.ndarray,
                     windows: list[tuple[int, int]]) -> np.ndarray:
    # Full-coverage criterion: stimulus window must fit inside bout
    # Priority system: Walk > Stationary > Freeze
    # Merge overlapping stimulus windows
```

### 4. **Bounded NaN Cleanup**
```python
def _fill_bounded_nan_bouts(behavior_labels: np.ndarray,
                           *,
                           response_windows: list[tuple[int, int]]) -> np.ndarray:
    # Only internal NaN runs (bounded by same label)
    # Length constraints and flank quality checks
    # Response window avoidance
```

## Integration with Configuration Pattern

### 1. **Registry Integration**
- Uses `EXPERIMENT` bundle for timebase and parameters
- Leverages `PATH` bundle for file operations
- Integrates with `PARAM` bundle for thresholds

### 2. **Bundle Composition**
- Creates immutable bundles for classification functions
- Maintains read-only access to configuration
- Clean separation of concerns

### 3. **Validation Pipeline**
- Pre-flight QC for fatal errors
- Post-classification QC for non-fatal flags
- Comprehensive error reporting

## Performance Optimization Patterns

### 1. **Vectorized Operations**
- NumPy-first approach for all computations
- Efficient array operations for large datasets
- Minimal Python loops

### 2. **Cumulative Sum Optimization**
```python
# O(1) window queries using cumulative sums
s = np.where(valid, speed, 0.0)
csum = np.cumsum(s)
ccount = np.cumsum(valid.astype(int))
```

### 3. **Searchsorted for Period Queries**
```python
# O(log n) period lookup using binary search
idx = np.searchsorted(period_ends_exclusive, frame, side="right")
```

### 4. **Memory Efficiency**
- In-place operations where possible
- Minimal data copying
- Efficient data structures

## Scientific Rigor Standards

### 1. **Validation Completeness**
- Input validation at every stage
- Cross-module consistency checks
- Comprehensive error messages

### 2. **Algorithm Transparency**
- Clear documentation of classification logic
- Explicit precedence rules
- Traceable decision paths

### 3. **Reproducibility**
- Deterministic algorithms
- Consistent random number generation
- Version-controlled parameters

### 4. **Performance Monitoring**
- Timing measurements
- Memory usage tracking
- Progress reporting

## Duck Integration Insights

### 1. **Algorithm Mastery**
Duck must understand:
- Multi-layer classification pipelines
- Denoising and smoothing techniques
- Resistant behavior detection
- Performance optimization patterns

### 2. **Orchestration Patterns**
Duck should implement:
- Skinny orchestrators with delegation
- Atomic file operations
- Progress tracking and reporting
- Error handling and recovery

### 3. **Validation Systems**
Duck needs:
- Pre-flight and post-classification QC
- Comprehensive error reporting
- Cross-module consistency checks
- Performance monitoring

### 4. **Bundle Architecture**
Duck must master:
- Immutable bundle creation
- Registry integration
- Clean separation of concerns
- Read-only access patterns

## Pattern Recognition

### 1. **Multi-Layer Classification**
- **Pattern**: Hierarchical classification with denoising
- **Evidence**: Layer1 → Layer2 → Resistant → Behavior pipeline
- **Architecture**: Progressive refinement with validation

### 2. **Guard-Based Processing**
- **Pattern**: Conditional processing based on data characteristics
- **Evidence**: High-speed guards, response window guards
- **Architecture**: Context-aware algorithm execution

### 3. **Atomic Operations**
- **Pattern**: All-or-nothing file operations
- **Evidence**: Atomic CSV writes, error recovery
- **Architecture**: Transaction-like processing

### 4. **Progress Tracking**
- **Pattern**: Real-time progress reporting
- **Evidence**: Progress bars, session summaries
- **Architecture**: User feedback during long operations

## Implementation Insights

### 1. **NumPy Integration**
- Extensive use of NumPy for performance
- Vectorized operations for efficiency
- Proper handling of edge cases

### 2. **Error Handling**
- Specific error codes and messages
- Graceful degradation
- Comprehensive logging

### 3. **Memory Management**
- Efficient data structures
- Minimal memory overhead
- In-place operations where possible

### 4. **API Design**
- Clean function interfaces
- Consistent parameter naming
- Logical function grouping

## Duck Development Priorities

### High Priority
1. **Algorithm Understanding**: Master classification pipelines
2. **Orchestration Patterns**: Learn delegation and coordination
3. **Validation Systems**: Implement comprehensive QC

### Medium Priority
1. **Performance Optimization**: Understand vectorized operations
2. **Error Handling**: Master specific error messaging
3. **Progress Tracking**: Learn real-time reporting

### Low Priority
1. **Advanced Algorithms**: Complex denoising techniques
2. **Memory Management**: Optimization strategies
3. **API Design**: Interface consistency patterns

## Scientific Excellence Features

### 1. **Reproducibility**
- Deterministic algorithms
- Version-controlled parameters
- Consistent random number generation

### 2. **Transparency**
- Clear documentation
- Traceable decision paths
- Explicit precedence rules

### 3. **Validation**
- Comprehensive input validation
- Cross-module consistency checks
- Performance monitoring

### 4. **Performance**
- Vectorized operations
- Efficient data structures
- Minimal memory overhead
