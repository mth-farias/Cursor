# Technical Data Flow & Pipeline Architecture

## Overview
This document describes the complete technical data flow through the fly behavior classification pipeline, from raw video input to final behavior classifications and analysis.

## High-Level Pipeline Flow

```
1. EXPERIMENT SETUP
   User opens Google Colab → Inputs experimental parameters → System downloads code

2. DATA COLLECTION  
   Raw video (BASE.avi) + tracking data (BASE.csv) → External software processes

3. BEHAVIOR CLASSIFICATION
   Our pipeline analyzes the data → Produces behavior classifications

4. RESULTS & ANALYSIS
   Scored behaviors + statistical analysis → Scientific insights
```

## Detailed Technical Flow

### Phase 1: Raw Data Collection
```
ExperimentalFolder/
├── RawData/
│   ├── BASE.avi                    # Raw video from cameras
│   └── BASE.csv                    # Hardware timing and GPIO signals
```

**Data Sources:**
- **Video**: Multi-camera setup recording fly behavior in arena
- **Timing**: Hardware clock synchronization and stimulus markers
- **GPIO**: Digital signals marking stimulus onset/offset

### Phase 2: External Processing (Not Our Code)
```
RawData/ → External Tracking Software → PostProcessing/
```

**External Tools Process:**
- **Video tracking**: Extract fly positions from video
- **Pose estimation**: SLEAP body-part detection
- **Arena calibration**: Convert pixels to millimeters
- **Video segmentation**: Create per-fly video clips

**Outputs:**
```
PostProcessing/
├── Tracked/                        # Movement tracking data
│   └── BASE_flyN_tracked.csv      # Centroid positions, motion proxy
├── Sleap/                          # Body-part pose data  
│   └── BASE_flyN_sleap.csv        # Head, thorax, wings, confidence
├── ArenaImage/                     # Arena reference images
│   └── BASE_flyN_arenaimg.png     # Calibrated arena view
├── FlyVideo/                       # Per-fly video clips
│   └── BASE_flyN_flyvideo.avi     # Individual fly behavior
└── CropVideo/                      # Cropped analysis videos
    └── BASE_flyN_cropvideo.avi    # Zoomed view for analysis
```

### Phase 3: Our Classification Pipeline

#### Input Data Processing
```python
# Config modules provide all parameters
from Config import PATH, PARAM, EXPERIMENT, COLOR

# Load and validate input data
tracked_data = load_csv(PATH["pTracked"] / f"{base}_fly{n}_tracked.csv")
validate_data(tracked_data, PARAM["tracked_schema"])
```

#### Multi-Layer Classification Engine

**Layer 1: Raw Classification**
```python
# BehaviorClassifier/_classifier.py
speed = compute_speed(positions, EXPERIMENT["FRAME_RATE"])
motion = detect_motion(pixel_change, thresholds)
layer1 = classify_raw_behavior(speed, motion)
# Output: Jump, Walk, Stationary, Freeze (frame-by-frame)
```

**Layer 1 Denoised: Micro-bout Removal**
```python
layer1_denoised = remove_micro_bouts(layer1, min_duration=3_frames)
# Removes brief spurious classifications, preserves jumps
```

**Layer 2: Window Consensus**
```python
layer2 = window_consensus(layer1_denoised, window=5_frames)
# Smooths classifications using majority vote in sliding window
```

**Layer 2 Denoised: Half-Missing Rule**
```python
layer2_denoised = apply_half_missing_rule(layer2)
# Robust consensus that handles missing/uncertain data
```

**Resistant Behavior Detection**
```python
resistant = detect_resistant_behavior(layer2_denoised, stimulus_windows)
# Identifies stimulus-coupled defensive responses
```

**Final Behavior Mapping**
```python
behavior = map_final_behavior(layer2_denoised, resistant)
# Promotes Freeze → Resistant_Freeze when appropriate
# Output: Jump, Walk, Stationary, Freeze, Resistant_Freeze
```

#### Output Generation
```
BehaviorClassification/
├── Scored/                         # Main behavior outputs
│   └── BASE_flyN_scored.csv       # Complete behavioral analysis
├── Pose/                           # Pose-based analysis (if enabled)
│   └── BASE_flyN_pose.csv         # Orientation and body-part data
├── Error/                          # Quality control
│   ├── REPORT_ERROR.csv           # Error summary
│   └── Tracked/BASE_flyN_tracked.csv  # Problematic input data
└── Flag/                           # Flagged results
    ├── REPORT_FLAG.csv            # Flag summary  
    └── Scored/BASE_flyN_scored.csv   # Flagged outputs
```

## Data Schemas & Validation

### Input Data Validation
```python
# PARAM module defines all column schemas
BASE_SCHEMA = PARAM["BASE"]        # GPIO, FrameID, Timestamp
TRACKED_SCHEMA = PARAM["TRACKED"]  # Positions, PixelChange
SLEAP_SCHEMA = PARAM["SLEAP"]      # Body parts, confidence scores

# Validation ensures data quality
validate_columns(data, schema)
validate_domains(data, schema)  
validate_temporal_consistency(data)
```

### Output Data Structure
```python
# scored.csv contains complete behavioral analysis
SCORED_COLUMNS = {
    "FrameIndex": "Reference frame number",
    "Position_X": "X coordinate (mm)",
    "Position_Y": "Y coordinate (mm)", 
    "Speed": "Instantaneous speed (mm/s)",
    "Motion": "Binary motion flag",
    "Layer1": "Raw classification",
    "Layer1_Denoised": "Micro-bout removed",
    "Layer2": "Window consensus", 
    "Layer2_Denoised": "Half-missing rule",
    "Resistant": "Stimulus-coupled response",
    "Behavior": "Final behavior label",
    "Behavior_Denoised": "Final with gap-filling"
}
```

## Configuration & Parameters

### Single Source of Truth (SSOT)
All pipeline parameters come from Config modules:

```python
# Timing and experimental structure
EXPERIMENT = {
    "FRAME_RATE": 60,                    # Video frame rate
    "EXPERIMENTAL_PERIODS": {...},       # Baseline, Stimulation, Recovery
    "STIMULI": {...},                    # Visual stimuli definitions
}

# File paths and naming
PATH = {
    "pTracked": Path("PostProcessing/Tracked/"),
    "pScored": Path("BehaviorClassification/Scored/"),
    # ... all file locations
}

# Data validation schemas  
PARAM = {
    "Position_X": {"type": "float", "unit": "mm", ...},
    "Speed": {"type": "float", "unit": "mm/s", ...},
    # ... all column definitions
}

# Visualization and colors
COLOR = {
    "Jump": "#8E44AD",                   # Behavior colors
    "Walk": "#EF6060", 
    "cmap_motion_speed": colormap_obj,   # Speed colormaps
    # ... all visualization settings
}
```

### Parameter Flow
```
User edits Config modules → configure() functions → Immutable bundles → Pipeline usage
```

## Quality Control & Error Handling

### Multi-Level Validation
1. **Input validation**: Schema compliance, domain checking
2. **Processing validation**: Intermediate result sanity checks  
3. **Output validation**: Final result consistency
4. **Integration validation**: Cross-module compatibility

### Error Recovery
```python
# Graceful degradation for corrupted data
try:
    result = process_fly_data(fly_id)
except ValidationError as e:
    log_error(fly_id, e)
    copy_to_error_folder(input_files)
    continue_with_next_fly()
```

### Quality Flags
```python
# Automatic quality assessment
flags = assess_data_quality(scored_data)
if flags:
    copy_to_flag_folder(scored_data, flags)
    generate_flag_report(flags)
```

## Performance Considerations

### Large Dataset Handling (1000+ flies)
- **Memory management**: Process flies individually, not in batch
- **Progress tracking**: Log processing milestones
- **Checkpoint system**: Save intermediate results for recovery
- **Parallel processing**: Multiple flies can be processed simultaneously

### Optimization Strategies
- **Vectorized operations**: NumPy/Pandas for speed calculations
- **Efficient data structures**: Appropriate dtypes for memory efficiency
- **Lazy loading**: Only load needed data columns
- **Caching**: Reuse expensive computations when possible

## Integration Points

### Google Colab Interface
```python
# User-friendly interface hides complexity
def run_behavior_analysis(
    experiment_folder: str,
    frame_rate: int = 60,
    pose_scoring: bool = True
) -> str:
    """One-click behavior analysis."""
    # Configure pipeline
    # Process all flies
    # Generate reports
    # Return results summary
```

### External Tool Integration
- **Input validation**: Ensure external tools produce expected formats
- **Version compatibility**: Handle different tracking software versions
- **Error detection**: Identify corrupted external processing results
- **Format conversion**: Standardize data from different sources

## Future Architecture (Proposed)

### Per-Fly Organization
```
PostProcessing/
├── fly1/
│   ├── arenaimg.png              # Arena image
│   ├── flyvideo.avi              # Fly video
│   ├── tracked/
│   │   ├── centroidX.csv         # X coordinates
│   │   ├── centroidY.csv         # Y coordinates  
│   │   └── speed.csv             # Speed data
│   └── scored/
│       ├── behavior.csv          # Behavior classifications
│       └── confidence.csv        # Classification confidence
├── fly2/
│   └── ... (same structure)
```

**Benefits:**
- **Per-fly organization**: All data for one animal in one folder
- **Single parameter files**: One CSV per measurement type
- **Scalable**: Easy to handle 1000+ flies
- **Efficient**: Only load needed parameters
- **Scientific**: Matches biological thinking about individual animals

---

This data flow architecture ensures robust, scalable processing of fly behavior data while maintaining scientific rigor and reproducibility.
