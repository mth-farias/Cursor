"""
🦆 Duck .cursor/ Folder Organizer

Uses Duck's intelligence to reorganize your .cursor/ folder from
8 directories (with redundancies) to 6 clean directories.

Current Structure (8 dirs + redundancies):
- docs/ (with examples, guides, prompts inside)
- examples/ (duplicate of docs/examples/)
- guides/ (overlap with docs/guides/)
- prompts/ (duplicate of docs/prompts/)
- logs/
- plans/
- templates/
- thinktank/
- validation/
- rules/

Target Structure (6 clean dirs):
- context/ (merge docs/, guides/, prompts/)
- workflows/ (merge logs/, plans/, templates/)
- reference/ (move examples/)
- thinktank/ (keep as-is)
- validation/ (keep as-is)
- rules/ (keep as-is)

Author: Matheus + Duck
Date: October 3, 2025
Status: Ready to Execute
"""

from pathlib import Path
from typing import Dict, List, Tuple
import shutil
from datetime import datetime

from ..core.system import create_duck


class CursorOrganizer:
    """Duck-powered .cursor/ folder organizer"""
    
    def __init__(self, cursor_dir: Path = None):
        self.duck = create_duck()
        from ..core.env import get_cursor_dir
        self.cursor_dir = cursor_dir or get_cursor_dir()
        from ..core.env import get_backup_dir
        self.backup_dir = get_backup_dir()
        
        # Migration plan based on your documented strategy
        self.migration_plan = {
            # New context/ directory
            "context": {
                "description": "All guides & prompts consolidated",
                "sources": [
                    ("docs/guides", "guides/refactored"),
                    ("docs/guides", "guides/general"),
                    ("docs/prompts", "prompts"),
                    ("guides/project", "project"),
                    ("guides/development", "development"),
                    ("guides/refactoring", "refactoring"),
                    ("prompts", "quick-reference"),
                ],
            },
            
            # New workflows/ directory
            "workflows": {
                "description": "Active work & templates",
                "sources": [
                    ("logs/active", "active"),
                    ("logs/completed", "completed"),
                    ("logs/decisions", "decisions"),
                    ("plans", "plans"),
                    ("templates", "templates"),
                    ("projects/current", "current-project"),
                ],
            },
            
            # New reference/ directory
            "reference": {
                "description": "Completed work & examples",
                "sources": [
                    ("examples", "patterns"),
                    ("docs/examples", "legacy-examples"),  # Keep separate for now
                ],
            },
            
            # Keep as-is directories
            "thinktank": {
                "description": "Project discussions (keep structure)",
                "sources": "keep",
            },
            
            "validation": {
                "description": "Testing tools (keep structure)",
                "sources": "keep",
            },
            
            "rules": {
                "description": "Coding standards (keep structure)",
                "sources": "keep",
            },
        }
    
    def analyze_current_structure(self) -> Dict[str, any]:
        """Analyze current .cursor/ structure and identify issues"""
        print("🦆 Duck: Analyzing current .cursor/ structure...")
        
        analysis = {
            "directories": [],
            "file_count": {},
            "redundancies": [],
            "total_files": 0,
        }
        
        # Count files in each directory
        for item in self.cursor_dir.iterdir():
            if item.is_dir():
                analysis["directories"].append(item.name)
                file_count = len(list(item.rglob("*.*")))
                analysis["file_count"][item.name] = file_count
                analysis["total_files"] += file_count
        
        # Identify redundancies (from your documented analysis)
        redundancies = [
            ("docs/examples", "examples", "Same content"),
            ("docs/guides", "guides", "Overlapping content"),
            ("docs/prompts", "prompts", "Similar content"),
        ]
        
        for source, target, reason in redundancies:
            source_path = self.cursor_dir / source
            target_path = self.cursor_dir / target
            if source_path.exists() and target_path.exists():
                analysis["redundancies"].append({
                    "source": source,
                    "target": target,
                    "reason": reason,
                })
        
        # Print analysis
        print(f"\n📊 Current Structure Analysis:")
        print(f"   Total directories: {len(analysis['directories'])}")
        print(f"   Total files: {analysis['total_files']}")
        print(f"\n📁 Directory sizes:")
        for dir_name, count in sorted(analysis["file_count"].items(), key=lambda x: x[1], reverse=True):
            print(f"   {dir_name}: {count} files")
        
        print(f"\n⚠️  Redundancies found: {len(analysis['redundancies'])}")
        for redundancy in analysis["redundancies"]:
            print(f"   {redundancy['source']} ↔ {redundancy['target']}: {redundancy['reason']}")
        
        return analysis
    
    def create_backup(self) -> Path:
        """Create complete backup before reorganization"""
        print(f"\n💾 Creating backup at {self.backup_dir}...")
        
        if self.backup_dir.exists():
            print(f"❌ Backup directory already exists: {self.backup_dir}")
            return None
        
        shutil.copytree(self.cursor_dir, self.backup_dir)
        print(f"✅ Backup created successfully")
        return self.backup_dir
    
    def preview_migration(self) -> Dict[str, List[str]]:
        """Preview what will be moved where"""
        print("\n🔍 Migration Preview:")
        print("=" * 60)
        
        preview = {}
        
        for target_dir, config in self.migration_plan.items():
            if config.get("sources") == "keep":
                print(f"\n📌 {target_dir}/ (KEEP AS-IS)")
                print(f"   {config['description']}")
                preview[target_dir] = ["Keep existing structure"]
            else:
                print(f"\n📂 {target_dir}/ (NEW)")
                print(f"   {config['description']}")
                print(f"   Sources:")
                moves = []
                for source, dest_subdir in config["sources"]:
                    source_path = self.cursor_dir / source
                    if source_path.exists():
                        file_count = len(list(source_path.rglob("*.*")))
                        print(f"      {source}/ → {target_dir}/{dest_subdir}/ ({file_count} files)")
                        moves.append(f"{source} → {target_dir}/{dest_subdir}")
                    else:
                        print(f"      {source}/ → {target_dir}/{dest_subdir}/ (NOT FOUND)")
                preview[target_dir] = moves
        
        print("=" * 60)
        return preview
    
    def execute_migration(self, dry_run: bool = True) -> bool:
        """Execute the migration plan"""
        if dry_run:
            print("\n🔄 DRY RUN MODE - No actual changes will be made")
            print("   Set dry_run=False to execute for real")
        else:
            print("\n🚀 EXECUTING MIGRATION...")
            
        success = True
        
        try:
            for target_dir, config in self.migration_plan.items():
                if config.get("sources") == "keep":
                    print(f"\n✅ {target_dir}/ - Keeping as-is")
                    continue
                
                target_path = self.cursor_dir / target_dir
                print(f"\n📂 Creating {target_dir}/...")
                
                if not dry_run:
                    target_path.mkdir(exist_ok=True)
                
                for source, dest_subdir in config["sources"]:
                    source_path = self.cursor_dir / source
                    dest_path = target_path / dest_subdir
                    
                    if not source_path.exists():
                        print(f"   ⚠️  {source}/ - Not found, skipping")
                        continue
                    
                    if not dry_run:
                        print(f"   📁 Moving {source}/ → {target_dir}/{dest_subdir}/")
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(source_path), str(dest_path))
                    else:
                        print(f"   [DRY RUN] Would move: {source}/ → {target_dir}/{dest_subdir}/")
            
            # Clean up old empty directories
            if not dry_run:
                print("\n🧹 Cleaning up empty directories...")
                old_dirs = ["docs", "logs", "plans", "projects"]
                for old_dir in old_dirs:
                    old_path = self.cursor_dir / old_dir
                    if old_path.exists() and not any(old_path.iterdir()):
                        print(f"   Removing empty: {old_dir}/")
                        old_path.rmdir()
            
            if dry_run:
                print("\n✅ Dry run complete - ready for actual execution")
            else:
                print("\n🎉 Migration complete!")
                
        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            success = False
        
        return success
    
    def generate_migration_report(self) -> str:
        """Generate report documenting the migration"""
        report = f"""# 🦆 Duck .cursor/ Reorganization Report

**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Duck Version**: {self.duck.version}
**Backup Location**: {self.backup_dir}

---

## 📊 Migration Summary

### Before (8 directories with redundancies)
"""
        
        for dir_name in ["docs", "examples", "guides", "prompts", "logs", "plans", "templates", "thinktank", "validation", "rules"]:
            dir_path = self.backup_dir / dir_name if self.backup_dir.exists() else self.cursor_dir / dir_name
            if dir_path.exists():
                file_count = len(list(dir_path.rglob("*.*")))
                report += f"- `{dir_name}/` - {file_count} files\n"
        
        report += """
### After (6 clean directories)
- `context/` - All guides & prompts consolidated
- `workflows/` - Active work & templates
- `reference/` - Completed work & examples
- `thinktank/` - Project discussions (unchanged)
- `validation/` - Testing tools (unchanged)
- `rules/` - Coding standards (unchanged)

---

## 📋 Migration Details

"""
        
        for target_dir, config in self.migration_plan.items():
            report += f"### {target_dir}/\n"
            report += f"**Purpose**: {config['description']}\n\n"
            
            if config.get("sources") == "keep":
                report += "**Status**: Kept as-is\n\n"
            else:
                report += "**Migrations**:\n"
                for source, dest_subdir in config["sources"]:
                    report += f"- `{source}/` → `{target_dir}/{dest_subdir}/`\n"
                report += "\n"
        
        report += """---

## ✅ Benefits

1. **Eliminated Redundancy**: No more docs/ vs top-level duplication
2. **Clear Organization**: Each directory has single clear purpose
3. **Better Navigation**: Easier to find what you need
4. **Maintainability**: Simpler structure to maintain

---

## 🔄 Rollback Instructions

If you need to restore the old structure:

```bash
# Remove new structure
rm -rf .cursor/

# Restore from backup
cp -r {backup_dir} .cursor/
```

---

*Organized by Duck 🦆*
"""
        
        return report


def main():
    """Main CLI for Duck .cursor/ organizer"""
    import sys
    
    print("🦆 Duck .cursor/ Folder Organizer")
    print("=" * 60)
    
    organizer = CursorOrganizer()
    
    # Step 1: Analyze current structure
    analysis = organizer.analyze_current_structure()
    
    # Step 2: Preview migration
    preview = organizer.preview_migration()
    
    # Step 3: Ask for confirmation
    print("\n" + "=" * 60)
    print("📋 Ready to reorganize .cursor/ folder")
    print("=" * 60)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--execute":
        # Create backup
        backup_path = organizer.create_backup()
        if not backup_path:
            print("❌ Failed to create backup. Aborting.")
            sys.exit(1)
        
        # Execute migration
        success = organizer.execute_migration(dry_run=False)
        
        if success:
            # Generate report
            report = organizer.generate_migration_report()
            report_path = Path(".cursor/REORGANIZATION_REPORT.md")
            report_path.write_text(report)
            print(f"\n📄 Report saved to: {report_path}")
            print(f"💾 Backup available at: {backup_path}")
        else:
            print("\n❌ Migration failed. Check backup at:", backup_path)
            sys.exit(1)
    else:
        # Dry run
        organizer.execute_migration(dry_run=True)
        print("\n" + "=" * 60)
        print("💡 To execute the migration for real:")
        print("   python duck_cursor_organizer.py --execute")
        print("=" * 60)


if __name__ == "__main__":
    main()

