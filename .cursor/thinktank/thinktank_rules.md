# 🧠 **Thinktank Rules & Guidelines**

## 🎯 **Purpose**

The thinktank is your **project discussion space** where we plan, analyze, and design before implementing. It follows the **Plan → Discuss → Design → Implement** methodology.

## 📋 **Standard Thinktank Structure**

### **Required Files:**
```
thinktank/[project-name]/
├── summary.md                    # Human-readable current state (REQUIRED)
├── decisions.md                  # All decisions made (REQUIRED)
├── architecture.md              # Technical design (REQUIRED)
├── implementation.md            # Implementation plan (REQUIRED)
└── references.md                # Links to all relevant files (OPTIONAL)
```

### **Optional Files:**
- `analysis.md` - Current state analysis
- `questions.md` - Open questions and discussions
- `examples.md` - Examples and patterns

## 🚀 **Thinktank Workflow**

### **Step 1: Plan (Project Setup)**
1. **Create thinktank directory** for the project
2. **Create summary.md** with project overview
3. **Create decisions.md** for decision tracking
4. **Define success criteria** and requirements

### **Step 2: Discuss (Decision Capture)**
1. **Capture all decisions** in decisions.md
2. **Document rationale** for each decision
3. **List alternatives considered** and why rejected
4. **Track impact** of each decision

### **Step 3: Design (Architecture)**
1. **Create architecture.md** with technical design
2. **Document file structure** and relationships
3. **Define interfaces** and dependencies
4. **Plan implementation phases**

### **Step 4: Implement (Execution)**
1. **Create implementation.md** with detailed steps
2. **Execute step-by-step** following the plan
3. **Validate each step** before proceeding
4. **Document lessons learned**

## 📊 **File Naming Convention**

### **Required:**
- **lowercase letters only** - No screaming capitals
- **descriptive names** - Clear what the file contains
- **consistent naming** - Same pattern across all thinktanks

### **Examples:**
- ✅ `summary.md` - Current state summary
- ✅ `decisions.md` - All decisions made
- ✅ `architecture.md` - Technical design
- ✅ `implementation.md` - Implementation plan
- ❌ `SUMMARY.md` - Screaming capitals
- ❌ `DECISIONS.md` - Screaming capitals
- ❌ `ARCHITECTURE.md` - Screaming capitals

## 🎯 **Content Guidelines**

### **summary.md Requirements:**
- **Human-readable** - Easy to understand for any human agent
- **Current state** - What's been done, what's in progress, what's planned
- **Key decisions** - Summary of major decisions made
- **Next steps** - Clear action items and timeline

### **decisions.md Requirements:**
- **Decision ID** - Unique identifier for each decision
- **Date** - When decision was made
- **Status** - Approved, Pending, Rejected
- **Rationale** - Why this decision was made
- **Alternatives** - What other options were considered
- **Impact** - What this decision affects

### **architecture.md Requirements:**
- **System overview** - High-level architecture
- **File structure** - Directory and file organization
- **Dependencies** - How components relate to each other
- **Interfaces** - How components interact

### **implementation.md Requirements:**
- **Step-by-step plan** - Detailed implementation steps
- **Timeline** - When each step should be completed
- **Validation** - How to test each step
- **Success criteria** - How to know when complete

## 🚨 **Quality Standards**

### **Documentation Quality:**
- **Clear and concise** - Easy to understand
- **Complete** - All necessary information included
- **Accurate** - Information is current and correct
- **Actionable** - Clear next steps and decisions

### **Decision Quality:**
- **Evidence-based** - Decisions backed by rationale
- **Alternatives considered** - Other options evaluated
- **Impact assessed** - Consequences understood
- **Reversible** - Can be changed if needed

### **Architecture Quality:**
- **Scalable** - Can grow with project needs
- **Maintainable** - Easy to update and modify
- **Testable** - Can be validated and verified
- **Documented** - Clear interfaces and dependencies

## 🔄 **Maintenance Guidelines**

### **Keep Files Updated:**
- **Update summary.md** after each major decision
- **Update decisions.md** whenever a decision is made
- **Update architecture.md** when design changes
- **Update implementation.md** as progress is made

### **Review Regularly:**
- **Weekly review** - Check if files are current
- **Decision review** - Validate decisions are still valid
- **Architecture review** - Ensure design is still appropriate
- **Implementation review** - Check progress against plan

## 🎓 **Best Practices**

### **Thinktank Management:**
- **Start with summary.md** - Always create this first
- **Capture decisions immediately** - Don't rely on memory
- **Document rationale** - Explain WHY, not just WHAT
- **Review decisions** - Validate choices before implementation

### **Collaboration:**
- **Share thinktank** - Make it accessible to collaborators
- **Document discussions** - Capture key points and decisions
- **Update regularly** - Keep information current
- **Ask questions** - Use thinktank to explore options

### **Learning:**
- **Reflect on decisions** - Learn from choices made
- **Document lessons** - Capture insights for future projects
- **Improve process** - Refine thinktank methodology over time
- **Share knowledge** - Help others learn from your experience

---

**These rules ensure consistent, high-quality thinktank discussions that lead to successful project implementations.**
