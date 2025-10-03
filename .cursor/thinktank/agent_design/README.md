# 🧠 **Thinktank: Agent Design System - Context Prompt**

## 🎯 **Mission Statement**

Design and implement a **reproducible agent design system** for Cursor AI that creates consistent, high-quality interactions across all scientific software development projects. This system will serve as the foundation for the `.cursor/` environment refactoring and future projects.

## 📋 **Project Goals**

### **Primary Objectives**
1. **Reproducible Agent Context** - Any new chat/agent can recreate the exact same working environment
2. **Modular File Architecture** - Split interaction rules into focused, reusable components
3. **Thinktank-First Workflow** - Plan → Discuss → Design → Implement methodology
4. **Scientific Software Standards** - Maintain rigor and quality across all interactions
5. **Power User Techniques** - Master advanced Cursor AI capabilities

### **Success Criteria**
- ✅ **New agents understand context in <5 minutes** (vs current ~15 minutes)
- ✅ **Consistent interaction patterns** across all projects
- ✅ **Easy maintenance** of rules and context files
- ✅ **Scalable to any scientific software project**
- ✅ **Perfect reproducibility** of working environments

## 🏗️ **Proposed Architecture**

### **File Structure Design**
```
.cursor/rules/
├── interaction-rules.mdc          # Core interaction rules (always referenced)
├── starter.md                     # General starter prompt template
├── context.md                     # Project-specific context
├── analysis-templates/            # Different analysis workflows
│   ├── general-scientific.md     # Any scientific software project
│   ├── config-specific.md        # Config package work
│   └── cursor-environment.md     # .cursor/ refactoring work
└── thinktank-workflow.md         # Thinktank methodology
```

### **Reference Strategy**
- **`@filename.md` syntax** for intuitive references
- **Fallback paths** for robustness
- **Explicit dependency tracking** in each file

## 🎓 **Design Principles**

### **1. Modularity**
- Each file has a single, clear responsibility
- Easy to update individual components
- Can be mixed and matched for different projects

### **2. Reproducibility**
- Explicit file references create clear dependencies
- Template-based structure provides consistent starting points
- All decisions and rationale captured in thinktank discussions

### **3. Scientific Rigor**
- Evidence-based decisions
- 100% functionality preservation requirements
- Publication-ready documentation standards

### **4. Power User Focus**
- Advanced Cursor AI techniques
- Efficient workflows and patterns
- Long-term maintainability

## 🚀 **Implementation Phases**

### **Phase 1: Thinktank Design** (Current)
- Analyze current interaction-rules.mdc
- Design modular file architecture
- Create thinktank discussion structure

### **Phase 2: File Creation**
- Create new modular files
- Implement reference system
- Test reproducibility

### **Phase 3: Validation**
- Test with new agent/chat
- Validate context understanding
- Refine based on results

### **Phase 4: Application**
- Apply to `.cursor/` refactoring project
- Document lessons learned
- Create templates for future projects

## 📚 **Key Questions to Resolve**

1. **File Reference Syntax** - Best approach for Cursor AI compatibility?
2. **Thinktank Structure** - Standardized vs flexible approach?
3. **Analysis Templates** - Checklist vs automated tool calls?
4. **Context Updates** - How to keep files synchronized?
5. **Project Adaptation** - How to customize for different projects?

## 🎯 **Next Steps**

1. **Complete thinktank discussion** of all design decisions
2. **Create modular file architecture** based on decisions
3. **Test reproducibility** with new agent
4. **Apply to `.cursor/` refactoring** as validation
5. **Document and template** for future projects

---

**This thinktank serves as the foundation for creating a world-class agent design system that ensures consistent, high-quality scientific software development across all projects.**
