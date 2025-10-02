# Refactoring Checklist Template

## Pre-Refactoring ✅
- [ ] Read current file structure and functionality
- [ ] Identify user constants vs processing logic
- [ ] Plan internal module structure (_module/ package)
- [ ] Create validation baseline script
- [ ] Document current API and behavior

## During Refactoring ✅
- [ ] Create _module/ package structure
- [ ] Move processing logic to internal modules
- [ ] Implement configure() function pattern
- [ ] Preserve all user constants in main file
- [ ] Maintain identical public API (MappingProxyType)
- [ ] Follow cell-based organization in new modules

## Post-Refactoring ✅
- [ ] Run comprehensive validation script
- [ ] Verify 100% functionality preservation
- [ ] Test all function outputs match exactly
- [ ] Verify all imports work unchanged
- [ ] Create detailed change log
- [ ] Update documentation and guides

## Success Criteria ✅
- [ ] All constants identical values
- [ ] All functions produce same outputs
- [ ] All imports work unchanged
- [ ] Configuration pattern implemented cleanly
- [ ] Clean separation: user interface vs implementation
- [ ] Performance maintained or improved

## Files to Update After Success ✅
- [ ] Update `.cursor/logs/active/current_focus.md`
- [ ] Create change log in `.cursor/logs/completed/`
- [ ] Update `.cursor/plans/next_targets.md`
- [ ] Run `.cursor/prompts/after_commit_update.md`
