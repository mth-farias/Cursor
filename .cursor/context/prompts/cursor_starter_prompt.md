# Cursor Starter Prompt for Fly Behavior Pipeline

Hey Cursor! I'm Matheus, and I need your help as my AI coding coach to continue refactoring my fly behavior classification pipeline. Let me catch you up on where we are and what we're working on.

## **What We're Building**

I'm developing a **scientific software pipeline** for automated Drosophila (fruit fly) behavior classification. Think of it as a "smart microscope" that watches flies and automatically classifies their defensive behaviors: Walk, Stationary, Freeze, Jump, and Resistant_Freeze.

This isn't just any code project - it's **scientific software** that needs to meet publication standards and will eventually be open-sourced for the research community. We're talking about processing thousands of hours of video data and handling datasets with 1000+ flies.

## **Current Status & What I Need**

### **Where We Are:**
- **`Codes_Before/`**: My original working system (cell-based, notebook-style) - **IT WORKS** but needs modernization
- **`Codes_Working/`**: Partial refactor I started but stopped mid-way (you can ignore this mostly)
- **`Codes/`**: Where we're heading - modern, publication-ready Python structure

### **What I Need You To Do:**
I want you to be my **AI coding coach** to help me:
1. **Refactor systematically** from `Codes_Before/` to `Codes/` 
2. **Follow scientific computing best practices** 
3. **Maintain the working functionality** while modernizing
4. **Learn modern Python patterns** as we go
5. **Keep scientific rigor** - this code needs to be reproducible and reliable

## **Key Files You Should Understand**

### **Project Context & Standards**
- **`.cursor/docs/guides/project_context.md`** - Complete project overview, mission, and development philosophy
- **`.cursor/rules/`** - Our coding standards (code_style.md, scientific.md, modules.md, performance.md)
- **`.cursor/docs/examples/`** - Template examples showing our intended patterns

### **Current Working System (`Codes_Before/`)**
- **`Config/`** - Single source of truth for everything:
  - `path.py` - File paths and naming conventions
  - `experiment.py` - Timebase, stimuli, experimental periods  
  - `param.py` - Data schemas and validation rules
  - `color.py` - Visualization color schemes
- **`BehaviorClassifier/`** - Core classification engine:
  - `_classifier.py` - Multi-layer behavior classification algorithms
  - `_utils.py` - Shared utilities and data processing
  - `_qc_error_flag.py` - Quality control and error handling
  - `_main.py` - Orchestrator that runs the full pipeline
  - `_colab.py` - Google Colab integration and file management
  - `behaviorclassifier_run.py` - Entry point for users

### **Data Examples**
- **`ExampleFiles/`** - Real data samples showing input/output formats

## **My Development Philosophy**

### **Scientific Software Principles**
- **Quality over speed** - Take time to do things right
- **Single Source of Truth (SSOT)** - All config values come from Config modules
- **Fail fast, fail clear** - Descriptive errors, no silent defaults  
- **Scientific rigor** - Every decision backed by scientific rationale
- **Flexible rule override system** - Can override any rule when scientifically justified

### **How I Want to Work With You**
- **You're my coding coach** - Teach me modern practices as we code
- **File-focused work** - Only work on specific files we're discussing
- **Ask before creating** - Always ask before making new files/directories
- **Learning together** - Explain your reasoning so I understand the patterns
- **Maintain working functionality** - Never break the existing pipeline

## **Technical Architecture You Should Know**

### **Data Flow**
```
Raw Video (BASE.avi) + Tracking (BASE.csv)
    ↓ (external tracking software)
PostProcessing/Tracked/ + PostProcessing/Sleap/
    ↓ (our classification pipeline)
BehaviorClassification/Scored/ + /Pose/ + /Error/ + /Flag/
```

### **Classification Pipeline (Multi-Layer)**
1. **Layer1**: Raw speed/motion → Jump/Walk/Stationary/Freeze
2. **Layer1_Denoised**: Micro-bout removal, speed smoothing
3. **Layer2**: Window consensus with tie-breaking
4. **Layer2_Denoised**: Half-missing rule for robustness
5. **Resistant**: Stimulus-coupled defensive behavior detection
6. **Behavior**: Final output with promotion rules (Freeze → Resistant_Freeze)

### **Key Patterns We Use**
- **Cell-based structure** (transitioning to standard modules)
- **MappingProxyType** for immutable public APIs
- **Comprehensive type hints** with modern syntax
- **Scientific data validation** with biological constraints
- **Atomic file operations** for reliability
- **Error recovery** and checkpoint systems

## **Current Refactoring Approach**

### **From `Codes_Before/` Structure:**
```python
#%% CELL 00 — HEADER & OVERVIEW
#%% CELL 01 — IMPORTS  
#%% CELL 02 — CONSTANTS & VALIDATION
#%% CELL 03 — HELPER FUNCTIONS
#%% CELL 04 — CORE LOGIC
#%% CELL 05 — PUBLIC API
#%% CELL 06 — REPORT
```

### **To Modern Python Structure:**
```python
"""Module docstring with clear purpose"""
from __future__ import annotations
# Organized imports
# Constants  
# Type definitions
# Helper functions (private)
# Public functions
# Classes
# Public API (MappingProxyType)
```

## **Important Notes**

- **The system currently works** - don't break existing functionality
- **Scientific accuracy is paramount** - this processes real research data
- **Performance matters** - we handle 1000+ flies efficiently  
- **Error handling is critical** - graceful degradation for corrupted data
- **Reproducibility required** - same inputs must give same outputs

## **Getting Started**

Please start by reading through the referenced files to understand our project context, coding standards, and current architecture. Then summarize what you understand about the project so I can confirm we're aligned before I tell you what I want to work on next.

---

*This prompt gives you the full context of our fly behavior classification pipeline refactoring project. All the referenced files contain the detailed information you need to understand the codebase and help me modernize it systematically.*
