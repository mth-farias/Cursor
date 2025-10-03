# 🎯 **Decisions Log: Config/path.py Refactoring**

## 📋 **Power User Decision Tracking**

This file tracks all decisions made during the refactoring planning process. Each decision includes the rationale, alternatives considered, and impact.

### **🎯 Decision Categories**
- **✅ RESOLVED** - Decision made and implemented
- **🔄 PENDING** - Decision needed but not yet made
- **⚠️ BLOCKED** - Decision blocked by dependencies
- **🔄 REVISED** - Decision changed based on new information

### **📊 Decision Impact Matrix**
| Decision | Complexity | Risk | Timeline Impact | Dependencies |
|----------|------------|------|------------------|--------------|
| Scope Clarification | High | Medium | Major | None |
| Per-Fly Implementation | Very High | High | Major | Scope |
| Validation Strategy | Medium | Low | Minor | All decisions |
| Data Format | Low | Low | Minor | Per-Fly |
| Hybrid Approach | Medium | Low | Minor | Data Format |

## ✅ **DECIDED DECISIONS**

### **1. Scope Clarification** ✅ **RESOLVED**
- **Date**: 2024-10-02
- **Question**: Should we merge `BehaviorClassification` into `PostProcessing`?
- **Decision**: **YES** - Structural changes for per-fly organization
- **Rationale**: User wants to change file structure to be per-fly
- **Impact**: Major structural reorganization required

### **2. Per-Fly Implementation** ✅ **RESOLVED**
- **Date**: 2024-10-02
- **Question**: Are per-fly functions actually needed or theoretical?
- **Decision**: **ACTUAL NEED** - User wants to change file structure to be per-fly
- **Rationale**: User explicitly stated wanting per-fly organization
- **Impact**: New functions required for fly discovery and data access

### **3. Validation Strategy** ✅ **RESOLVED**
- **Date**: 2024-10-02
- **Question**: How to handle validation for big structural changes?
- **Decision**: **CAREFUL VALIDATION** - Need comprehensive testing for major changes
- **Rationale**: Big changes require careful testing to prevent bugs
- **Impact**: Extensive validation required throughout implementation

### **4. Timeline Priority** ✅ **RESOLVED**
- **Date**: 2024-10-02
- **Question**: Core refactoring first or per-fly capabilities together?
- **Decision**: **TOGETHER** - User wants to create thinktank file now
- **Rationale**: User wants comprehensive planning before implementation
- **Impact**: More complex initial planning, but better long-term results

### **5. Backward Compatibility** ✅ **RESOLVED**
- **Date**: 2024-10-02
- **Question**: How critical is backward compatibility?
- **Decision**: **NOT CRITICAL** - User is refactoring everything fresh, massive changes OK
- **Rationale**: User explicitly stated "we are refactoring everything fresh, so we can do massive changes now"
- **Impact**: Freedom to make major structural changes

### **6. Data Format** ✅ **RESOLVED**
- **Date**: 2024-10-02
- **Question**: What data format for individual column files?
- **Decision**: **CSV WITH HEADERS** - Professional standard, tool compatible, scientific format
- **Rationale**: User prefers CSV files with headers for individual column files
- **Impact**: Column-based files will use CSV format with headers

### **7. FrameIndex Handling** ✅ **RESOLVED**
- **Date**: 2024-10-02
- **Question**: How to handle different FrameIndex ranges between input and output data?
- **Decision**: **KEEP SEPARATE** - Input (0+) and output (299+) have different ranges due to cropping
- **Rationale**: Different data types have different FrameIndex ranges due to cropping logic
- **Impact**: Need to handle different FrameIndex ranges in path functions

### **8. QC Integration** ✅ **RESOLVED**
- **Date**: 2024-10-02
- **Question**: Should path.py handle FrameIndex validation?
- **Decision**: **NO** - path.py provides path access; QC module validates data consistency
- **Rationale**: Clear separation of concerns - path module for paths, QC module for validation
- **Impact**: FrameIndex validation stays in `BehaviorClassifier/_qc_error_flag.py`

### **9. Architectural Approach** ✅ **RESOLVED**
- **Date**: 2024-10-02
- **Question**: Which approach for memory efficiency and scalability?
- **Decision**: **HYBRID APPROACH** - Best of both worlds
- **Rationale**: 
  - Backward compatible with existing code
  - Memory efficient with `usecols=['Speed']` for selective loading
  - Gradual migration to column-based architecture
  - Long-term scalability for 1000+ flies
- **Impact**: Immediate memory solution + future scalability

### **10. Thinktank Organization** ✅ **RESOLVED**
- **Date**: 2024-10-02
- **Question**: How to organize thinktank documentation?
- **Decision**: **MULTIPLE FOCUSED FILES** - Split into specialized files
- **Rationale**: 
  - User is "control freak, crazy obsessive" - needs detailed tracking
  - 438 lines in single file is unwieldy
  - Better organization and maintainability
  - Clear separation of concerns
- **Impact**: Better documentation structure, easier to maintain

## 🤔 **PENDING DECISIONS**

### **1. Implementation Phases**
- **Question**: Should we implement in phases or all at once?
- **Status**: **DISCUSSION NEEDED**
- **Impact**: Affects implementation timeline and risk

### **2. Testing Strategy**
- **Question**: How comprehensive should testing be?
- **Status**: **DISCUSSION NEEDED**
- **Impact**: Affects implementation timeline and quality

### **3. Migration Strategy**
- **Question**: How to handle existing data during transition?
- **Status**: **DISCUSSION NEEDED**
- **Impact**: Affects data safety and user workflow

## 📝 **Decision Template**

For future decisions, use this template:

```markdown
### **X. Decision Name** ✅ **RESOLVED**
- **Date**: YYYY-MM-DD
- **Question**: What was the question?
- **Decision**: What was decided?
- **Rationale**: Why was this decision made?
- **Impact**: What are the consequences?
```

## 🔄 **Decision Review Process**

1. **Document Decision**: Add to this file with full context
2. **Update Impact**: Update affected files and plans
3. **Communicate**: Ensure all stakeholders understand
4. **Track**: Monitor implementation of decision
5. **Review**: Revisit if circumstances change

## 📊 **Power User Decision Summary**

### **✅ Critical Decisions Made (10)**
- **Scope**: Structural changes for per-fly organization
- **Per-Fly**: Actual need for BASE_flyN pattern
- **Validation**: Careful testing for major changes
- **Timeline**: Comprehensive planning before implementation
- **Compatibility**: Freedom for massive changes
- **Data Format**: CSV with headers for column files
- **FrameIndex**: Different ranges for input vs output data
- **Cropping**: Aligned to experiment onset with padding
- **QC Integration**: FrameIndex validation in _qc_error_flag.py
- **Hybrid Approach**: Best of both worlds for scalability

### **🎯 Decision Quality Metrics**
- **✅ 100% Resolved** - All critical decisions made
- **✅ Clear Rationale** - Each decision has documented reasoning
- **✅ Impact Assessed** - Consequences clearly identified
- **✅ Dependencies Mapped** - Decision relationships understood

### **🚀 Next Decision Points**
- **Implementation Strategy**: Which phase to start with?
- **Testing Approach**: Automated vs manual validation?
- **Migration Plan**: How to handle existing data?

---

**This decisions log ensures all decisions are properly tracked and documented for the path.py refactoring project.**
