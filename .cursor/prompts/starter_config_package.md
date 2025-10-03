# Config Package Specific Context Setup

Hey Cursor! I need your help with **Config package refactoring** - building on the general context from `@.cursor/prompts/starter.md`.

## **Config-Specific Context - Read These**

### **Config Package Strategy & Plans**
- **`@.cursor/plans/config_package.md`** - Detailed Config refactoring strategy
- **`@.cursor/guides/refactoring/configuration_pattern_playbook.md`** - Step-by-step replication guide
- **`@.cursor/examples/experiment_breakthrough_pattern.py`** - Real success example

### **Config Working Systems Analysis**
**Please analyze these Config directories specifically:**
- **`@Codes_Before/Config/`** - Original Config system (understand current functionality)
- **`@Codes_Working/Config/`** - Enhanced Config system (understand improvements)  
- **`@Codes/Config/`** - Target Config system (understand current progress)

### **Config Success Reference**
- **`@.cursor/logs/completed/config_experiment.md`** - Successful experiment.py refactoring
- **`@.cursor/validation/scripts/validate_experiment_refactor.py`** - Working validation example

## **Config Package Mission**

Refactor the **Single Source of Truth** for all pipeline parameters:
- **Four immutable bundles**: `PATH`, `PARAM`, `EXPERIMENT`, `COLOR`
- **Critical dependency**: Everything else depends on Config
- **PURELY STRUCTURAL**: Transform cell-based → modern Python modules

### **Configuration Pattern Success**
Apply the **proven pattern** from experiment.py (570 → 230 lines):
```
User constants → configure() function → use configured bundles
```

## **Config Module Candidates**

### **Next Targets** (Choose Based on Priority)
- **`color.py`**: High complexity (689-1293 lines, matplotlib integration)
  - **Plan**: `@.cursor/plans/config_color_detailed.md`
  - **Validation**: `@.cursor/validation/scripts/validate_color_functionality.py`
- **`param.py`**: Highest complexity (714-917 lines, extensive validation)
  - **Plan**: `@.cursor/plans/config_param_strategy.md`
- **`path.py`**: Moderate complexity (647-692 lines, file system operations)
  - **Plan**: `@.cursor/plans/config_path_plan.md`

## **Config-Specific Resources**

### **Validation & Testing**
- **`@.cursor/templates/validation_template.py`** - Comprehensive testing framework
- **`@.cursor/templates/refactor_checklist.md`** - Step-by-step process
- **Module-specific validation scripts** in `@.cursor/validation/scripts/`

### **Advanced Workflows Available**
- **`@.cursor/guides/development/cursor_power_features.md`** - 6x faster analysis techniques
- **`@.cursor/guides/development/workflow_optimization.md`** - 3x productivity improvement
- **`@.cursor/prompts/quick_start_templates.md`** - Optimized session templates

## **Config Success Formula**

```
1. ANALYZE Config module with parallel tool calls (6x faster)
2. PLAN using proven configuration pattern
3. IMPLEMENT with incremental validation
4. VALIDATE with automated testing (100% preservation)
5. DOCUMENT with comprehensive change logs
```

## **Ready for Config Work**

With the general context from `@starter.md` and Config-specific context loaded:
1. **Choose target module** based on complexity and priority
2. **Apply proven patterns** using comprehensive resources
3. **Leverage advanced workflows** for maximum efficiency
4. **Ensure scientific integrity** with automated validation

**Which Config module should we tackle next?**