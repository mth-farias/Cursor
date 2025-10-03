# 🧠 **Thinktank: Config/path.py Refactoring - Context Prompt**

Hey Cursor! I'm Matheus, and I need your help as my AI coding coach for **Config/path.py refactoring** - building on the general context from `@.cursor/prompts/starter.md` and Config-specific context from `@.cursor/prompts/starter_config_package.md`.

## 🎯 **Mission Statement**

Transform `Codes_Working/Config/path.py` (647 lines, 17 functions) into a **clean, scalable, configuration-based architecture** using the **proven pattern** established in `experiment.py` (570→230 lines, 60% reduction) and `color.py` (1,293→273 lines, 78.9% reduction).

## 📋 **Essential Context - Read These First**

### **Project Foundation**
- **📋 Project Overview**: `@.cursor/guides/project/context.md` - Complete mission & architecture
- **🎯 Current Focus**: `@.cursor/logs/active/current_focus.md` - What I'm working on now
- **📈 Config Strategy**: `@.cursor/plans/config_package.md` - Config refactoring strategy

### **Complete .cursor Environment Analysis**
**Please read these entire directories for full context:**
- **`@.cursor/rules/`** - All coding standards and principles
- **`@.cursor/guides/`** - Complete project documentation
- **`@.cursor/examples/`** - All code patterns and templates
- **`@.cursor/logs/`** - Current work status and decisions
- **`@.cursor/plans/`** - Project planning and strategy

### **Working Systems Overview**
- **`@Codes_Before/Config/`** - Original Config system (understand current functionality)
- **`@Codes_Working/Config/`** - Enhanced Config system (understand improvements)  
- **`@Codes/Config/`** - Target Config system (understand current progress)

## 🎉 **Revolutionary Pattern Established**

We've achieved a **breakthrough configuration pattern** in Config package:
- **experiment.py**: 570 → 230 lines (60% reduction) - ✅ **COMPLETED**
- **color.py**: 1,293 → 273 lines (78.9% reduction) - ✅ **COMPLETED**
- **path.py**: 647 lines → target ~200 lines (70% reduction) - 🎯 **NEXT TARGET**

**Pattern**: User constants → configure() → use configured bundles

## 🚀 **Config Package Mission**

Refactor the **Single Source of Truth** for all pipeline parameters:
- **Four immutable bundles**: `PATH`, `PARAM`, `EXPERIMENT`, `COLOR`
- **Critical dependency**: Everything else depends on Config
- **PURELY STRUCTURAL**: Transform cell-based → modern Python modules

### **Configuration Pattern Success**
Apply the **proven pattern** from experiment.py and color.py:
```
User constants → configure() function → use configured bundles
```

## 🎯 **Path.py Specific Context**

### **Target File Analysis**
- **File**: `Codes_Working/Config/path.py` (647 lines, 17 functions)
- **Structure**: 9 cells with mixed responsibilities
- **Functions**: 25+ path variables, 4 glob functions, 3 diagnostic functions
- **Pattern**: Monolithic file with no separation of concerns

### **Key Functions to Preserve**
- **Path builders**: 25+ canonical path variables
- **Helper functions**: `stem_without_suffix`, `siblings`, QC routing functions
- **Discovery functions**: `g_tracked`, `g_sleap`, `g_scored`, `g_pose`
- **Utility functions**: `temp_path`, `with_root`, rebase logic
- **Diagnostic functions**: `sanity_checks`, `demo`, `_count`

## 🏗️ **Target Architecture**

### **New Structure Design**
```
Codes/Config/
├── path.py                 # Main controller (~200 lines)
└── _path/                  # Internal modules
    ├── __init__.py         # Configuration function & exports
    ├── canonical.py        # Canonical path builders
    ├── per_fly.py          # Per-fly data access functions
    ├── temp_files.py       # Atomic write handling
    ├── rebase.py           # Root rebasing (Colab/Drive)
    ├── diagnostics.py      # QC & validation
    └── report.py           # Path structure reports
```

### **Per-Fly Capabilities (NEW)**
- **Individual fly analysis** using BASE_flyN filename pattern
- **Fly discovery and status tracking** functions
- **Per-fly data access** functions
- **Column-based file structure** for scalability

## 🎯 **Architectural Decision: Hybrid Approach** ✅ **DECIDED**

**Why Hybrid Approach is Perfect:**
1. **✅ Backward Compatible**: Existing code continues to work
2. **✅ Memory Efficient**: New analysis code can use `usecols=['Speed']` for selective loading
3. **✅ Gradual Migration**: Can adopt column-based architecture over time
4. **✅ Long-term Scalability**: Ready for 1000+ flies with column-based structure
5. **✅ Best Practices**: Drop bad legacies, implement good practices from the start

## 📊 **Thinktank Structure**

This thinktank is organized into focused files for maximum maintainability:

- **📋 [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md)** - Quick overview and key decisions
- **🎯 [DECISIONS_LOG.md](DECISIONS_LOG.md)** - All decisions made during discussion
- **📊 [TECHNICAL_ANALYSIS.md](TECHNICAL_ANALYSIS.md)** - Current state analysis and technical details
- **🏗️ [ARCHITECTURE_PLAN.md](ARCHITECTURE_PLAN.md)** - Future architecture and design
- **📋 [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md)** - Step-by-step implementation plan
- **📝 [REFERENCES.md](REFERENCES.md)** - File references and links

## 🚀 **Quick Start**

1. **📋 Review [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md)** - High-level overview
2. **🎯 Check [DECISIONS_LOG.md](DECISIONS_LOG.md)** - All decisions made
3. **📊 Analyze [TECHNICAL_ANALYSIS.md](TECHNICAL_ANALYSIS.md)** - Current state
4. **🏗️ Plan with [ARCHITECTURE_PLAN.md](ARCHITECTURE_PLAN.md)** - Future design
5. **📋 Execute [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md)** - Step-by-step

## 🔧 **Config-Specific Resources**

### **Validation & Testing**
- **`@.cursor/templates/validation_template.py`** - Comprehensive testing framework
- **`@.cursor/templates/refactor_checklist.md`** - Step-by-step process
- **Module-specific validation scripts** in `@.cursor/validation/scripts/`

### **Advanced Workflows Available**
- **`@.cursor/guides/development/cursor_power_features.md`** - 6x faster analysis techniques
- **`@.cursor/guides/development/workflow_optimization.md`** - 3x productivity improvement
- **`@.cursor/prompts/quick_start_templates.md`** - Optimized session templates

## 📝 **Success Formula**

```
1. ANALYZE path.py with parallel tool calls (6x faster)
2. PLAN using proven configuration pattern
3. IMPLEMENT with incremental validation
4. VALIDATE with automated testing (100% preservation)
5. DOCUMENT with comprehensive change logs
```

## 🎯 **Core Development Principles**

- **Scientific rigor**: 100% functionality preservation, evidence-based decisions
- **Quality over speed**: Take time to do things right
- **Configuration pattern**: User constants → configure() → use bundles
- **File-focused work**: Only work on specific files being discussed
- **Learn together**: Explain reasoning for modern patterns

## 🚀 **Ready for Path.py Work**

With the general context from `@starter.md`, Config-specific context from `@starter_config_package.md`, and this thinktank context loaded:

1. **Choose implementation phase** based on complexity and priority
2. **Apply proven patterns** using comprehensive resources
3. **Leverage advanced workflows** for maximum efficiency
4. **Ensure scientific integrity** with automated validation

**This thinktank README.md serves as a comprehensive context prompt for the path.py refactoring project.**