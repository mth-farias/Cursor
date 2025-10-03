# Config Package Refactoring Prompt

Hey Cursor! I'm Matheus, and I need your help refactoring the **Config package** of my fly behavior classification pipeline. 

## **Getting Started**

First, please read these to understand the context:
1. **`.cursor/docs/prompts/cursor_starter_prompt.md`** - Full project overview and my development philosophy
2. **`.cursor/docs/guides/guide_config_refactor.md`** - Detailed Config refactoring plan and constraints

## **What We're Doing Today**

I want to work on refactoring the Config package - the **Single Source of Truth** for all pipeline parameters. This package provides four immutable bundles (`PATH`, `PARAM`, `EXPERIMENT`, `COLOR`) that everything else depends on.

### **The Critical Rule: PRESERVE ALL FUNCTIONALITY**

This is **PURELY STRUCTURAL** refactoring:
- ✅ Transform cell-based organization → modern Python modules  
- ✅ Improve maintainability and testability
- ❌ **NO changes** to constants, functions, or behavior
- ❌ **NO breaking** of existing imports or APIs

I have two working reference systems:
- **`Codes_Before/Config/`** - Original working system (cell-based)
- **`Codes_Working/Config/`** - Enhanced working system (partially modernized)

Both work perfectly. We're just reorganizing the code structure.

### **The Goal**

Transform this cell-based structure:
```python
#%% CELL 00 — HEADER & OVERVIEW
#%% CELL 01 — CONSTANTS & USER INPUTS  
#%% CELL 02 — HELPER FUNCTIONS
#%% CELL 03 — CORE LOGIC
#%% CELL 04 — PUBLIC API
#%% CELL 05 — REPORTS
```

Into modern Python modules:
```
Config/
├── color.py          # User interface (imports from color/)
├── color/            # Logic modules
│   ├── constants.py  # CELL 01 content
│   ├── mapping.py    # CELL 02 content
│   └── ...
```

## **Progress Status**

### ✅ **COMPLETED: experiment.py Refactoring**

The `experiment.py` file has been successfully refactored from a 570-line monolithic cell-based structure into a modern modular architecture:

**New Structure:**
```
Codes/Config/
├── experiment.py              # Main controller & user interface
└── _experiment/               # Internal processing modules
    ├── __init__.py           # Module exports
    ├── stimuli.py            # Stimulus validation & enrichment (+ StimSpec TypedDict)
    ├── periods.py            # Period validation & enrichment (+ PeriodSpec TypedDict)
    ├── time.py               # Time conversion & query utilities
    └── report.py             # Report generation functions
```

**Documentation & Validation:**
- **Complete Guide**: `.cursor/docs/guides/guide_config_experiment.md`
- **Change Log**: `.cursor/docs/guides/refactored/config_experiment_change_log.md`
- **Validation Script**: `.cursor/validation/validate_experiment_refactor.py`

**Key Achievements:**
- ✅ 100% functionality preservation validated
- ✅ All original constants, functions, and behavior identical
- ✅ API compatibility maintained (`from Config import EXPERIMENT`)
- ✅ Modern Python architecture with proper type hints
- ✅ Comprehensive validation and documentation

## **What I Need From You**

For the **remaining config files** (color.py, param.py, path.py):

1. **Read the reference docs** I mentioned above
2. **Review the completed experiment.py refactoring** as a reference model
3. **Confirm your understanding** of:
   - The Config package's role as SSOT
   - The constraint to preserve ALL functionality
   - The cell-to-module transformation approach
4. **Look at the current working systems** in `Codes_Before/Config/` and `Codes_Working/Config/`
5. **Recommend which config file** we should tackle next (color.py, param.py, or path.py) and explain your reasoning
6. **Ask any questions** about the approach or constraints

Remember: We're not changing what the code does, just how it's organized. Every constant, function, and behavior must remain identical.
