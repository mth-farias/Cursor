# Development Workflow with Cursor

## Overview
This document describes the optimal workflow for developing the fly behavior pipeline using Cursor AI as a coding assistant.

## Session Management

### Starting a New Session
1. **Use the starter prompt**: `@.cursor/prompts/starter.md`
   - Provides complete project context
   - Sets up AI understanding of current state
   - References all key documentation

2. **Quick context for continuing work**: `@.cursor/prompts/new_session.md`
   - Faster setup for ongoing work
   - Points to current focus and next steps
   - Good for short sessions

3. **Check current status**: Always review `.cursor/logs/active/current_focus.md`
   - Understand what was last worked on
   - See current priorities and blockers
   - Plan session activities

### During Development Sessions

#### File-Focused Work
- **Work on specific files**: Focus on one module at a time
- **Reference working systems**: Use `Codes_Before/` and `Codes_Working/` as reference
- **Preserve functionality**: Never break existing pipeline
- **Document changes**: Update logs and plans as you work

#### AI Collaboration Patterns
```
1. ANALYZE → Study current code structure and functionality
2. PLAN → Design refactoring approach and architecture  
3. IMPLEMENT → Apply configuration pattern step by step
4. VALIDATE → Comprehensive testing and verification
5. DOCUMENT → Update logs, plans, and guides
```

### Ending Sessions
1. **Update current focus**: Modify `.cursor/logs/active/current_focus.md`
   - Mark completed tasks
   - Update current work status
   - Note any blockers or insights

2. **Use after-commit prompt**: `@.cursor/prompts/after_commit_update.md`
   - Update project state after commits
   - Plan next session priorities
   - Capture lessons learned

## Refactoring Workflow

### Phase 1: Analysis & Planning
```
1. Study target module (e.g., color.py)
   - Read Codes_Before/Config/color.py (original)
   - Read Codes_Working/Config/color.py (enhanced)
   - Understand all functionality and dependencies

2. Create detailed plan
   - Update .cursor/plans/config_[module].md
   - Map cell structure to target architecture
   - Identify challenges and solutions

3. Create validation baseline
   - Use .cursor/templates/validation_template.py
   - Capture complete current functionality
   - Save baseline for comparison
```

### Phase 2: Implementation
```
1. Create internal module structure
   - Create Codes/Config/_[module]/ directory
   - Implement __init__.py with configure() function
   - Create specialized modules (constants.py, utilities.py, etc.)

2. Apply configuration pattern
   - Keep user constants in main file
   - Move processing logic to internal modules
   - Implement clean configure() interface
   - Assemble immutable public API

3. Incremental testing
   - Test each internal module as created
   - Validate configure() function works
   - Test public API assembly
```

### Phase 3: Validation & Documentation
```
1. Comprehensive validation
   - Run validation script: python validate_[module]_refactor.py
   - Verify 100% functionality preservation
   - Test integration with other modules

2. Performance testing
   - Check import times
   - Verify memory usage
   - Test processing speed

3. Documentation
   - Create change log: .cursor/logs/completed/config_[module].md
   - Update current focus and next targets
   - Update architecture decisions if needed
```

## File Organization Workflow

### Working with .cursor Structure
```
.cursor/
├── rules/                    # Read these for coding standards
├── guides/                   # Reference for understanding project
├── examples/                 # Copy patterns from here
├── templates/                # Use for consistent processes
├── logs/                     # Update as you work
├── plans/                    # Follow and update plans
├── prompts/                  # Use for session management
└── validation/               # Store validation scripts and results
```

### Key Files to Update Regularly
- **Current focus**: `.cursor/logs/active/current_focus.md`
- **Next targets**: `.cursor/plans/next_targets.md`
- **Architecture decisions**: `.cursor/logs/decisions/architecture_decisions.md` (for major decisions)

## Code Quality Workflow

### Following Standards
1. **Read the rules**: Check `.cursor/rules/` for all coding standards
   - `code_style.mdc` - Formatting and naming
   - `scientific.mdc` - Scientific computing practices
   - `modules.mdc` - Module structure guidelines
   - `project_philosophy.mdc` - Core principles

2. **Use examples**: Reference `.cursor/examples/` for patterns
   - `configuration_pattern.py` - Main refactoring pattern
   - `immutable_api.py` - MappingProxyType usage
   - `cell_structure.py` - Cell-based organization

3. **Follow templates**: Use `.cursor/templates/` for consistency
   - `refactor_checklist.md` - Step-by-step process
   - `validation_template.py` - Comprehensive testing
   - `change_log_template.md` - Documentation format

### Quality Assurance Process
```
1. IMPLEMENT → Write code following patterns and standards
2. VALIDATE → Run comprehensive validation suite
3. DOCUMENT → Create detailed change logs
4. REVIEW → Check against quality criteria
5. COMMIT → Save work with descriptive messages
```

## Troubleshooting Workflow

### When Things Go Wrong
1. **Use troubleshooting prompt**: `@.cursor/prompts/troubleshooting.md`
   - Common issues and solutions
   - Debugging strategies
   - Recovery procedures

2. **Check working systems**: Verify reference systems intact
   - `Codes_Before/` should be unchanged
   - `Codes_Working/` should be unchanged
   - Only `Codes/` should have new changes

3. **Rollback if needed**: Use git to revert problematic changes
   ```bash
   git status
   git checkout HEAD~1 -- [specific_file]
   ```

### Emergency Procedures
- **Stop immediately** if validation fails
- **Don't proceed** until issues are resolved
- **Ask for help** with specific error messages
- **Preserve working systems** at all costs

## Collaboration Patterns

### Effective AI Collaboration
1. **Be specific**: Ask focused questions about specific files or functions
2. **Provide context**: Reference relevant files and current state
3. **Follow patterns**: Apply established configuration pattern consistently
4. **Validate thoroughly**: Test everything before proceeding

### Communication Style
- **Clear objectives**: State what you want to accomplish
- **Specific constraints**: Mention functionality preservation requirements
- **Reference materials**: Point to relevant guides and examples
- **Progress updates**: Share what's working and what's not

## Version Control Workflow

### Commit Strategy
```
1. Small, focused commits
   - One logical change per commit
   - Clear, descriptive commit messages
   - Include validation results

2. Commit message format:
   "refactor(config): apply configuration pattern to [module]
   
   - Move processing logic to _[module]/ package
   - Implement configure() function pattern
   - Preserve 100% functionality (validated)
   - Reduce main file from XXX to YYY lines"

3. After each commit:
   - Use after_commit_update.md prompt
   - Update project state files
   - Plan next session work
```

### Branch Strategy
- **Main branch**: Keep stable, working code
- **Feature branches**: For major refactoring work
- **Validation**: Always validate before merging

## Performance Optimization

### Development Efficiency
1. **Parallel tool calls**: Use multiple AI tool calls simultaneously when possible
2. **Batch operations**: Group related file operations together
3. **Focused sessions**: Work on one module at a time
4. **Template reuse**: Leverage templates for consistent processes

### Code Performance
1. **Import optimization**: Minimize import times
2. **Memory efficiency**: Monitor memory usage during refactoring
3. **Processing speed**: Maintain or improve processing performance
4. **Validation speed**: Optimize validation scripts for quick feedback

## Success Metrics

### Session Success
- ✅ **Clear progress**: Measurable advancement toward goals
- ✅ **Documentation updated**: Current state accurately reflected
- ✅ **Quality maintained**: Code quality standards met
- ✅ **Functionality preserved**: No regression in pipeline behavior

### Project Success
- ✅ **Refactoring completed**: All Config modules modernized
- ✅ **Pattern established**: Configuration architecture proven
- ✅ **Quality improved**: Better maintainability and readability
- ✅ **Scientific integrity**: 100% functionality preservation

This workflow ensures efficient, high-quality development while maintaining scientific rigor and code quality standards.
