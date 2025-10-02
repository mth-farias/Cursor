# Fly Behavior Pipeline - Project Context

## Project Team Declaration

### Our Mission
We are a **scientific software development team** dedicated to creating professional, open-source tools for behavioral neuroscience research. Our current mission is to **refactor and modernize** an existing fly behavior classification pipeline to meet publication standards and prepare it for open-source release.

### Current Status
- **Working Pipeline**: We have a functional system that successfully classifies fly behaviors
- **Code Quality**: The current code works but needs modernization for professional standards
- **Publication Goal**: We aim to publish this as a peer-reviewed scientific software package
- **Open Source Vision**: Make the tools freely available to the scientific community

### Our Refactoring Approach

#### Why We're Refactoring
1. **Publication Standards**: Scientific software must meet high quality standards for peer review
2. **Maintainability**: Current cell-based structure is difficult to maintain and extend
3. **Collaboration**: Standard Python modules enable better team development
4. **Performance**: Modern architecture will handle larger datasets efficiently
5. **Accessibility**: Better structure makes the code easier for others to use and contribute

#### How We're Using Cursor
**Cursor is our AI coding coach** that helps us:
- **Learn best practices** for modern Python development
- **Maintain consistency** across all code modules
- **Catch potential issues** before they become problems
- **Follow scientific computing standards** for reproducible research
- **Create professional documentation** and type hints
- **Implement proper testing** and quality assurance

#### Our Development Philosophy
- **Quality over speed**: We take time to do things right
- **Learning together**: Cursor teaches us modern practices as we code
- **Scientific rigor**: Every decision supports reproducible research
- **Community focus**: We build for the broader scientific community
- **Iterative improvement**: We refactor one module at a time, learning as we go
- **File-focused work**: Only work on the specific file being discussed, no unsolicited file creation
- **Flexible rules**: We can override any rule when scientifically justified, but always flag it clearly
- **Evidence-based decisions**: Every architectural choice is backed by scientific rationale

#### Team Structure
- **Lead Developer**: Matheus (project owner, scientific domain expert)
- **AI Coach**: Cursor (coding standards, best practices, quality assurance)
- **Future Contributors**: Open source community (after publication)

## What We're Building

This project is a **scientific software pipeline** for automatically classifying defensive behaviors in fruit flies (Drosophila). Think of it as a "smart microscope" that can watch a fly and tell you exactly what it's doing - whether it's walking, freezing, jumping, or showing other defensive responses.

## Why This Matters

### The Scientific Problem
Scientists studying animal behavior need to analyze thousands of hours of video footage to understand how animals respond to threats. Currently, this requires:
- **Manual observation** by trained researchers (extremely time-consuming)
- **Inconsistent results** between different observers
- **Limited scalability** for large datasets
- **High costs** for human labor

### Our Solution
We're building an **automated system** that can:
- **Watch videos** of fruit flies in experimental arenas
- **Track their movements** using computer vision
- **Classify behaviors** automatically (Walk, Stationary, Freeze, Jump, Resistant_Freeze)
- **Generate reports** with statistical analysis
- **Scale to thousands** of experiments

## How It Works

### The Complete Pipeline

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

### Technical Architecture

**Current System (Working but needs improvement):**
```
RawData/ (BASE.avi, BASE.csv) 
    ↓ (external tracking software)
PostProcessing/ (Tracked/, Sleap/, ArenaImage/, FlyVideo/, CropVideo/)
    ↓ (our classification pipeline)
BehaviorClassification/ (Scored/, Pose/, Error/, Flag/)
```

**New Proposed System (Better organized):**
```
PostProcessing/
├── fly1/
│   ├── arenaimg.png          # Image of the experimental arena
│   ├── flyvideo.avi          # Video of just this fly
│   ├── cropvideo.avi         # Cropped video for analysis
│   ├── tracked/              # Movement tracking data
│   │   ├── centroidX.csv     # X coordinates over time
│   │   ├── centroidY.csv     # Y coordinates over time
│   │   └── speed.csv         # Speed measurements
│   └── scored/               # Behavior classifications
│       ├── behavior.csv      # What the fly was doing
│       └── confidence.csv    # How certain we are
├── fly2/
│   └── ... (same structure)
```

### Data Structure Benefits
- **Per-fly organization**: All data for one fly in one folder
- **Single parameter files**: One CSV per parameter (centroidX, speed, etc.)
- **Scalable**: Easy to handle 1000+ flies
- **Efficient**: Only load the parameters you need
- **Scientific**: Matches how biologists think about individual animals

## The Scientific Context

### What We're Studying
- **Defensive behaviors** in fruit flies when they encounter threats
- **How flies respond** to visual stimuli (like looming objects)
- **Individual differences** in defensive strategies
- **Neural mechanisms** underlying these behaviors

### Why Fruit Flies?
- **Model organism** for neuroscience research
- **Simple nervous system** that's easier to understand
- **Genetic tools** available for manipulation
- **Fast reproduction** for large-scale studies

### The Behaviors We Classify
1. **Walk** - Normal movement around the arena
2. **Stationary** - Sitting still, not moving
3. **Freeze** - Sudden stop in response to threat
4. **Jump** - Quick escape movement
5. **Resistant_Freeze** - Prolonged defensive posture

## Technical Challenges We're Solving

### 1. Data Organization
**Problem**: Current system organizes files by type (all tracked files together, all scored files together)
**Solution**: New system organizes by individual fly, making it easier to analyze each animal's complete behavior

### 2. Code Structure
**Problem**: Current code uses "cells" (like Jupyter notebooks) which is hard to maintain
**Solution**: Convert to standard Python modules that are easier to understand and modify

### 3. Scalability
**Problem**: Current system struggles with large datasets (1000+ flies)
**Solution**: Optimize for performance and create efficient data structures

### 4. User Experience
**Problem**: Current system requires technical knowledge to use
**Solution**: Create simple Google Colab interface that anyone can use

## The Development Process

### Phase 1: Foundation (Completed ✅)
- ✅ **Working pipeline** - The basic system works
- ✅ **Core functionality** - Can classify behaviors
- ✅ **Comprehensive rules** - Modern coding standards with override system
- ✅ **Project context** - Clear understanding of goals and approach
- ✅ **Code organization** - Started restructuring for maintainability
- ✅ **Documentation** - Comprehensive guides and validation systems

### Rule Override System
We've implemented a **flexible rule system** that allows scientific overrides:
- **Complete flexibility**: Override any rule when scientifically justified
- **Clear flagging**: Use `# OVERRIDE: [reason]` comments
- **Scientific rationale**: Document why the rule was overridden
- **Categories**: TEMPORARY, SCIENTIFIC, PERFORMANCE, COMPATIBILITY, EXPERIMENTAL
- **Examples**: Loop instead of vectorization for complex biological logic

### Phase 2: Modernization (In Progress 🔄)
- ✅ **Convert to standard Python** - Successfully refactored `Config/experiment.py` from 570-line monolithic cell structure to modern modular architecture
- ✅ **Add type hints** - Complete type annotations with TypedDict schemas (`StimSpec`, `PeriodSpec`)
- ✅ **Comprehensive testing** - Validation framework with 100% functionality preservation verification
- ✅ **Scientific data validation** - Rigorous validation patterns for experimental parameters
- 🔄 **Modern packaging** - Use industry-standard tools (remaining config files)
- 🔄 **Performance monitoring** - Handle 1000+ flies efficiently
- 🔄 **Error recovery** - Robust scientific workflows

**Completed Work:**
- **experiment.py Refactoring**: Transformed from cell-based to modular architecture
  - `Codes/Config/experiment.py` - Main controller & user interface
  - `Codes/Config/_experiment/` - Internal processing modules (stimuli, periods, time, report)
  - Complete documentation: `.cursor/docs/guides/guide_config_experiment.md`
  - Validation system: `.cursor/validation/validate_experiment_refactor.py`
  - Change tracking: `.cursor/docs/guides/refactored/config_experiment_change_log.md`

### Phase 3: Enhancement (Future)
- 🔄 **New packages** - Add visualization, plotting, statistics
- 🔄 **Better interface** - Improve user experience
- 🔄 **Performance optimization** - Handle larger datasets
- 🔄 **Open source release** - Make available to scientific community

## Who Will Use This

### Primary Users
- **Neuroscientists** studying defensive behavior
- **Graduate students** learning behavioral analysis
- **Research labs** needing automated behavior analysis
- **Anyone** studying animal behavior

### User Experience
1. **Open Google Colab** (no installation needed)
2. **Input experiment parameters** (arena size, frame rate, etc.)
3. **Upload video data** to Google Drive
4. **Run the pipeline** (one click)
5. **Get results** with behavior classifications and statistics

## The Code Structure

### Current Organization
```
Codes_Before/          # Original working code (cell-based)
├── Config/           # Configuration settings
├── BehaviorClassifier/ # Main classification engine

Codes_Working/        # Partially refactored code
├── Config/         # Improved configuration
└── BehaviorClassifier/ # Some improvements

Codes/               # New modern structure (goal)
├── src/
│   └── fly_behavior/
│       ├── config/        # All configuration
│       ├── classification/ # Behavior analysis
│       ├── visualization/  # Video generation
│       ├── plotting/      # Data visualization
│       ├── statistics/    # Statistical analysis
│       └── colab/        # User interface
├── tests/           # Quality assurance
├── examples/        # Usage examples
└── docs/           # Documentation
```

## Key Design Decisions

### 1. Data Organization
**Decision**: Organize by individual fly instead of by file type
**Why**: Makes it easier to analyze complete behavior of each animal
**Impact**: Better for scientific analysis, easier to understand

### 2. Code Architecture
**Decision**: Move from cell-based to standard Python modules
**Why**: Easier to maintain, test, and collaborate on
**Impact**: More professional, easier for new developers

### 3. User Interface
**Decision**: Keep Google Colab as primary interface
**Why**: No installation required, accessible to all scientists
**Impact**: Broader adoption, easier for non-programmers

### 4. Open Source
**Decision**: Make the software freely available
**Why**: Accelerate scientific progress, build community
**Impact**: More users, better software, scientific advancement

## Enhanced Development Standards

### Scientific Computing Excellence
- **Data validation**: Rigorous validation of coordinates, stimuli, and biological data
- **Error recovery**: Graceful handling of corrupted files and missing data
- **Performance monitoring**: Memory profiling and progress tracking for large datasets
- **Reproducibility**: Complete parameter logging and random seed management
- **Documentation**: Scientific methodology and domain context in all code

### Modern Python Practices
- **Type hints**: Complete type annotations for all functions
- **Immutable APIs**: MappingProxyType for public interfaces
- **Vectorization**: NumPy/Pandas operations for performance
- **Testing**: Comprehensive test coverage with scientific validation
- **Packaging**: Modern Python package structure with proper dependencies

## Success Metrics

### Technical Success
- [x] **Code quality** - Config/experiment.py follows modern best practices (remaining files in progress)
- [ ] **Performance** - Can handle 1000+ flies efficiently
- [x] **Reliability** - Comprehensive testing ensures accuracy (experiment.py validated)
- [x] **Maintainability** - Easy for new developers to contribute (modular architecture established)
- [x] **Scientific rigor** - All decisions backed by scientific rationale
- [x] **Flexibility** - Rule override system enables scientific creativity

### Scientific Success
- [ ] **Accuracy** - Behavior classifications match expert judgments
- [ ] **Reproducibility** - Same results every time
- [ ] **Usability** - Scientists can use it without programming knowledge
- [ ] **Adoption** - Used by multiple research labs

### Community Success
- [ ] **Documentation** - Clear guides for users and developers
- [ ] **Examples** - Working examples for common use cases
- [ ] **Support** - Community helps each other
- [ ] **Growth** - More contributors and users over time

## The Big Picture

### Why This Project Matters
1. **Scientific Advancement** - Automates tedious manual work
2. **Reproducibility** - Standardized analysis across labs
3. **Accessibility** - Makes advanced analysis available to all
4. **Scalability** - Enables large-scale behavioral studies
5. **Open Science** - Freely available tools for the community

### Long-term Vision
- **Industry standard** for fly behavior analysis
- **Platform** for other behavioral studies
- **Educational tool** for teaching behavioral neuroscience
- **Foundation** for understanding defensive behaviors

## Next Steps

### Immediate (This Week) - Completed ✅
1. **Create comprehensive context** ✅
2. **Develop coding standards** ✅ - Rules for consistent code
3. **Plan module structure** ✅ - How to organize the code
4. **Start refactoring** ✅ - Successfully refactored Config/experiment.py

### Short-term (Next Month) - In Progress 🔄
1. **Refactor core modules** - ✅ Config/experiment.py complete, remaining Config files (color.py, param.py, path.py) next
2. **Add comprehensive testing** - ✅ Validation framework established for Config modules
3. **Improve documentation** - ✅ Comprehensive guides and change tracking system created
4. **Optimize performance** - Handle larger datasets

### Long-term (Next Year)
1. **Open source release** - Make available to community
2. **Add new features** - Visualization, statistics, plotting
3. **Build community** - Users and contributors
4. **Scientific validation** - Prove effectiveness in research

---

*This context file provides a complete understanding of the project's goals, challenges, and approach. It serves as a guide for developers, users, and stakeholders to understand what we're building and why it matters.*
