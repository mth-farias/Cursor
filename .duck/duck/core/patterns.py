"""
🦆 Duck Pattern Application Templates

Provides guided templates for applying Duck's 18 comprehensive patterns
to real-world development tasks.

Each pattern has:
- Application guidance
- Step-by-step process
- Success criteria
- Duck decision support

Author: Matheus (Scientific Software Development Master)
Date: October 3, 2025
Status: Phase 1 - Core Foundation
"""

from typing import Dict, List, Optional, Any, TypedDict
from pathlib import Path
from .system import create_duck, Duck
import re
import ast


# ============================================================================
# ADVANCED PATTERN DISCOVERY (Phase 2)
# ============================================================================

class PatternRecommendation(TypedDict):
    """Schema for pattern recommendations"""
    pattern_name: str
    confidence: float  # 0-100
    rationale: str
    evidence: List[str]
    applicability_score: float  # 0-1
    context_signals: Dict[str, Any]


class FileAnalysis(TypedDict):
    """Schema for file analysis results"""
    file_path: Path
    file_size: int
    line_count: int
    has_cell_structure: bool
    import_count: int
    function_count: int
    class_count: int
    complexity_indicators: List[str]
    structural_patterns: List[str]


class PatternDiscoveryEngine:
    """
    Advanced pattern discovery engine that analyzes code structure
    and suggests appropriate patterns with confidence scoring.
    """
    
    def __init__(self, duck: Optional[Duck] = None):
        self.duck = duck or create_duck()
        self.pattern_signals = self._build_pattern_signal_database()
    
    def _build_pattern_signal_database(self) -> Dict[str, Dict[str, Any]]:
        """Build database of signals that indicate pattern applicability"""
        return {
            "Revolutionary Configuration Pattern": {
                "file_size_threshold": 200,  # lines
                "cell_markers": ["CELL 00", "CELL 01", "CELL 02", "CELL 03", "CELL 04"],
                "complexity_indicators": ["large_module", "multiple_responsibilities", "configuration_data"],
                "import_patterns": ["typing", "pathlib", "numpy"],
                "structure_patterns": ["constants_section", "functions_section", "main_section"],
                "confidence_factors": {
                    "cell_structure": 0.85,
                    "large_size": 0.75,
                    "config_data": 0.80,
                    "multiple_imports": 0.70
                }
            },
            "Internal Module Architecture": {
                "import_count_threshold": 10,
                "complexity_indicators": ["complex_module", "multiple_dependencies"],
                "structure_patterns": ["monolithic_structure", "mixed_responsibilities"],
                "confidence_factors": {
                    "high_import_count": 0.80,
                    "complex_structure": 0.75,
                    "multiple_dependencies": 0.85
                }
            },
            "Scientific Rigor Standards": {
                "complexity_indicators": ["validation_required", "data_processing", "scientific_workflow"],
                "structure_patterns": ["data_validation", "error_handling", "documentation"],
                "confidence_factors": {
                    "validation_patterns": 0.90,
                    "error_handling": 0.85,
                    "documentation": 0.80
                }
            },
            "Power User Methodology": {
                "complexity_indicators": ["performance_critical", "batch_processing", "parallel_operations"],
                "structure_patterns": ["efficiency_patterns", "optimization_opportunities"],
                "confidence_factors": {
                    "performance_patterns": 0.85,
                    "batch_operations": 0.80,
                    "optimization_opportunities": 0.75
                }
            }
        }
    
    def discover_patterns(self, target_path: Path) -> List[PatternRecommendation]:
        """
        Analyze a file/module and discover applicable patterns.
        
        Args:
            target_path: Path to the file to analyze
            
        Returns:
            List of pattern recommendations with confidence scores
        """
        if not target_path.exists():
            return []
        
        # Analyze the file
        analysis = self._analyze_file(target_path)
        
        # Generate pattern recommendations
        recommendations = []
        for pattern_name, signals in self.pattern_signals.items():
            recommendation = self._evaluate_pattern_applicability(pattern_name, signals, analysis)
            if recommendation and recommendation['confidence'] > 50:  # Only return meaningful recommendations
                recommendations.append(recommendation)
        
        # Sort by confidence score
        recommendations.sort(key=lambda x: x['confidence'], reverse=True)
        
        return recommendations
    
    def _analyze_file(self, file_path: Path) -> FileAnalysis:
        """Analyze a file for structural patterns and complexity indicators"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            line_count = len(lines)
            
            # Check for cell structure
            has_cell_structure = any('CELL' in line for line in lines)
            
            # Count imports
            import_count = len([line for line in lines if line.strip().startswith(('import ', 'from '))])
            
            # Analyze AST for functions and classes
            try:
                tree = ast.parse(content)
                function_count = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])
                class_count = len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)])
            except:
                function_count = content.count('def ')
                class_count = content.count('class ')
            
            # Identify complexity indicators
            complexity_indicators = []
            if line_count > 200:
                complexity_indicators.append('large_module')
            if import_count > 10:
                complexity_indicators.append('multiple_dependencies')
            if function_count > 20:
                complexity_indicators.append('function_heavy')
            if 'validation' in content.lower() or 'validate' in content.lower():
                complexity_indicators.append('validation_required')
            if 'performance' in content.lower() or 'optimize' in content.lower():
                complexity_indicators.append('performance_critical')
            
            # Identify structural patterns
            structural_patterns = []
            if has_cell_structure:
                structural_patterns.append('cell_based_organization')
            if 'configure(' in content:
                structural_patterns.append('configuration_pattern')
            if 'MappingProxyType' in content:
                structural_patterns.append('immutable_bundles')
            if 'error' in content.lower() and 'except' in content.lower():
                structural_patterns.append('error_handling')
            
            return FileAnalysis(
                file_path=file_path,
                file_size=len(content),
                line_count=line_count,
                has_cell_structure=has_cell_structure,
                import_count=import_count,
                function_count=function_count,
                class_count=class_count,
                complexity_indicators=complexity_indicators,
                structural_patterns=structural_patterns
            )
            
        except Exception as e:
            # Return minimal analysis on error
            return FileAnalysis(
                file_path=file_path,
                file_size=0,
                line_count=0,
                has_cell_structure=False,
                import_count=0,
                function_count=0,
                class_count=0,
                complexity_indicators=[],
                structural_patterns=[]
            )
    
    def _evaluate_pattern_applicability(self, pattern_name: str, signals: Dict[str, Any], 
                                      analysis: FileAnalysis) -> Optional[PatternRecommendation]:
        """Evaluate how well a pattern applies to the analyzed file"""
        confidence_factors = signals.get('confidence_factors', {})
        evidence = []
        context_signals = {}
        
        # Calculate confidence based on signals
        total_confidence = 0.0
        signal_count = 0
        
        # Check file size signals
        if 'file_size_threshold' in signals:
            if analysis['line_count'] >= signals['file_size_threshold']:
                confidence = confidence_factors.get('large_size', 0.5)
                total_confidence += confidence
                signal_count += 1
                evidence.append(f"File size ({analysis['line_count']} lines) exceeds threshold")
                context_signals['large_file'] = True
        
        # Check cell structure signals
        if 'cell_markers' in signals and analysis['has_cell_structure']:
            confidence = confidence_factors.get('cell_structure', 0.5)
            total_confidence += confidence
            signal_count += 1
            evidence.append("File contains CELL structure markers")
            context_signals['cell_structure'] = True
        
        # Check import count signals
        if 'import_count_threshold' in signals:
            if analysis['import_count'] >= signals['import_count_threshold']:
                confidence = confidence_factors.get('high_import_count', 0.5)
                total_confidence += confidence
                signal_count += 1
                evidence.append(f"High import count ({analysis['import_count']})")
                context_signals['high_imports'] = True
        
        # Check complexity indicators
        for indicator in signals.get('complexity_indicators', []):
            if indicator in analysis['complexity_indicators']:
                confidence = confidence_factors.get(indicator, 0.5)
                total_confidence += confidence
                signal_count += 1
                evidence.append(f"Complexity indicator: {indicator}")
                context_signals[indicator] = True
        
        # Check structural patterns
        for pattern in signals.get('structure_patterns', []):
            if pattern in analysis['structural_patterns']:
                confidence = confidence_factors.get(pattern, 0.5)
                total_confidence += confidence
                signal_count += 1
                evidence.append(f"Structural pattern: {pattern}")
                context_signals[pattern] = True
        
        # Calculate final confidence (average of matched signals)
        if signal_count > 0:
            final_confidence = (total_confidence / signal_count) * 100
            applicability_score = min(1.0, signal_count / 3.0)  # Normalize by expected signal count
            
            # Generate rationale
            rationale = self._generate_rationale(pattern_name, evidence, final_confidence)
            
            return PatternRecommendation(
                pattern_name=pattern_name,
                confidence=final_confidence,
                rationale=rationale,
                evidence=evidence,
                applicability_score=applicability_score,
                context_signals=context_signals
            )
        
        return None
    
    def _generate_rationale(self, pattern_name: str, evidence: List[str], confidence: float) -> str:
        """Generate human-readable rationale for pattern recommendation"""
        if confidence >= 80:
            strength = "strong"
        elif confidence >= 60:
            strength = "moderate"
        else:
            strength = "weak"
        
        evidence_summary = ", ".join(evidence[:3])  # Limit to first 3 pieces of evidence
        
        return f"{strength.title()} match for {pattern_name} based on: {evidence_summary}"
    
    def explain_recommendation(self, recommendation: PatternRecommendation) -> str:
        """
        Generate detailed explanation of a pattern recommendation.
        
        Args:
            recommendation: Pattern recommendation to explain
            
        Returns:
            Detailed explanation string
        """
        explanation = f"""
🎯 Pattern Recommendation: {recommendation['pattern_name']}
📊 Confidence: {recommendation['confidence']:.1f}%
🎯 Applicability: {recommendation['applicability_score']:.1%}

💡 Rationale:
{recommendation['rationale']}

🔍 Evidence Found:
"""
        for evidence in recommendation['evidence']:
            explanation += f"   • {evidence}\n"
        
        explanation += f"""
📈 Context Signals:
"""
        for signal, value in recommendation['context_signals'].items():
            explanation += f"   • {signal}: {value}\n"
        
        return explanation.strip()


# ============================================================================
# PATTERN APPLICATION TEMPLATES
# ============================================================================

class PatternApplicator:
    """
    Duck-powered pattern application system.
    
    Guides users through systematic application of Duck's 18 patterns
    with confidence scoring and decision support.
    """
    
    def __init__(self, duck: Optional[Duck] = None):
        self.duck = duck or create_duck()
    
    def apply_configuration_pattern(self, module_name: str, 
                                    module_path: Path) -> Dict[str, Any]:
        """
        Apply Revolutionary Configuration Pattern to a module.
        
        This is Duck's signature pattern: 60-80% line reduction with
        100% functionality preservation.
        
        Args:
            module_name: Name of the module to refactor
            module_path: Path to the module file
        
        Returns:
            Implementation plan with 4-phase process
        """
        print(f"🦆 Duck: Applying Configuration Pattern to {module_name}")
        
        # Get pattern from Duck's library
        pattern = self.duck.pattern_engine.get_pattern(
            "Revolutionary Configuration Pattern"
        )
        
        if not pattern:
            return {"error": "Configuration pattern not found"}
        
        print(f"📚 Pattern Confidence: {pattern['confidence']:.1f}%")
        print(f"📖 Evidence: {', '.join(pattern['evidence'])}")
        
        # Make decision about applying pattern
        decision = self.duck.make_decision(
            title=f"Apply configuration pattern to {module_name}",
            evidence_count=2,  # experiment.py, color.py
            alignment_strength="strong",
            rationale="Proven pattern with 60-80% reduction, 100% preservation"
        )
        
        print(f"\n🎯 Decision: Type {decision['type']} ({decision['confidence']:.1f}% confidence)")
        
        # Build 4-phase implementation plan
        plan = {
            "module_name": module_name,
            "pattern": "Revolutionary Configuration Pattern",
            "confidence": pattern['confidence'],
            "decision": decision,
            "phases": self._build_configuration_phases(module_name),
            "expected_outcomes": {
                "line_reduction": "60-80%",
                "functionality_preservation": "100%",
                "validation_required": True,
                "production_ready": True,
            }
        }
        
        # Print implementation guide
        self._print_configuration_guide(plan)
        
        return plan
    
    def _build_configuration_phases(self, module_name: str) -> Dict[str, Dict]:
        """Build 4-phase configuration pattern implementation"""
        return {
            "phase_1": {
                "name": "Analysis & Planning",
                "tasks": [
                    f"Analyze {module_name} structure and cells",
                    "Map dependencies between components",
                    "Document current public API",
                    "Create module breakdown plan",
                ],
                "outputs": [
                    "Dependency map",
                    "API documentation",
                    "Refactoring plan",
                ],
                "duration": "1-2 hours",
            },
            "phase_2": {
                "name": "Create Internal Module Structure",
                "tasks": [
                    f"Create _{module_name}/ package",
                    f"Create _{module_name}/__init__.py with configure()",
                    "Create individual component modules",
                    "Implement create_*_bundle() functions",
                ],
                "outputs": [
                    f"_{module_name}/ directory structure",
                    "configure() function",
                    "Component bundle creators",
                ],
                "duration": "2-4 hours",
            },
            "phase_3": {
                "name": "Transform Main Module File",
                "tasks": [
                    "Keep only user constants in CELL 02",
                    "Add single configure() call in CELL 03",
                    "Clean up public API assembly in CELL 04",
                    "Implement proper imports and path setup",
                ],
                "outputs": [
                    f"Ultra-clean {module_name}.py",
                    "Single configure() call",
                    "Immutable bundle with MappingProxyType",
                ],
                "duration": "1-2 hours",
            },
            "phase_4": {
                "name": "Validation & Testing",
                "tasks": [
                    "Create comprehensive validation script",
                    "Test all constants match exactly",
                    "Test all functions produce identical outputs",
                    "Document results and create change log",
                ],
                "outputs": [
                    "Validation report (100% pass required)",
                    "Change log",
                    "Performance comparison",
                ],
                "duration": "1-2 hours",
            },
        }
    
    def _print_configuration_guide(self, plan: Dict[str, Any]):
        """Print implementation guide for configuration pattern"""
        print("\n" + "=" * 60)
        print(f"🦆 DUCK IMPLEMENTATION PLAN: {plan['module_name']}")
        print("=" * 60)
        
        print(f"\n📊 Expected Outcomes:")
        print(f"   Line Reduction: {plan['expected_outcomes']['line_reduction']}")
        print(f"   Preservation: {plan['expected_outcomes']['functionality_preservation']}")
        print(f"   Validation: {'Required' if plan['expected_outcomes']['validation_required'] else 'Optional'}")
        
        print(f"\n📋 4-Phase Implementation Process:")
        for phase_key, phase_data in plan['phases'].items():
            print(f"\n{phase_key.upper()}: {phase_data['name']}")
            print(f"Duration: {phase_data['duration']}")
            print("Tasks:")
            for i, task in enumerate(phase_data['tasks'], 1):
                print(f"  {i}. {task}")
            print("Outputs:")
            for output in phase_data['outputs']:
                print(f"  ✓ {output}")
        
        print("\n" + "=" * 60)
    
    def apply_systematic_analysis(self, repository_path: Path) -> Dict[str, Any]:
        """
        Apply Systematic Repository Analysis Protocol.
        
        Duck's mandatory 10-step repo scan before any work.
        
        Args:
            repository_path: Path to repository root
        
        Returns:
            Analysis checklist and results
        """
        print("🦆 Duck: Applying Systematic Repository Analysis")
        
        pattern = self.duck.pattern_engine.get_pattern(
            "Systematic Repository Analysis Protocol"
        )
        
        print(f"📚 Pattern Confidence: {pattern['confidence']:.1f}%")
        
        checklist = {
            "phase_1": "Foundation Layer",
            "steps": [
                {
                    "step": 1,
                    "name": "Scan .cursor/ directory structure",
                    "locations": [".cursor/"],
                    "completed": False
                },
                {
                    "step": 2,
                    "name": "Read all project guides",
                    "locations": [".cursor/guides/project/"],
                    "completed": False
                },
                {
                    "step": 3,
                    "name": "Review current focus and active work",
                    "locations": [".cursor/logs/active/"],
                    "completed": False
                },
                {
                    "step": 4,
                    "name": "Review architectural decisions",
                    "locations": [".cursor/logs/decisions/"],
                    "completed": False
                },
                {
                    "step": 5,
                    "name": "Read all coding rules",
                    "locations": [".cursor/rules/"],
                    "completed": False
                },
                {
                    "step": 6,
                    "name": "Review configuration pattern examples",
                    "locations": [".cursor/examples/", "Codes/Config/"],
                    "completed": False
                },
                {
                    "step": 7,
                    "name": "Read validation templates",
                    "locations": [".cursor/templates/", ".cursor/validation/"],
                    "completed": False
                },
                {
                    "step": 8,
                    "name": "Review completed work for patterns",
                    "locations": [".cursor/logs/completed/"],
                    "completed": False
                },
                {
                    "step": 9,
                    "name": "Check active thinktank discussions",
                    "locations": [".cursor/thinktank/"],
                    "completed": False
                },
                {
                    "step": 10,
                    "name": "Synthesize complete understanding",
                    "locations": ["All above"],
                    "completed": False
                },
            ],
            "duration": "10-15 minutes (with parallel processing)",
            "efficiency_gain": "6x faster than sequential",
        }
        
        print("\n📋 SYSTEMATIC REPOSITORY ANALYSIS CHECKLIST")
        print("=" * 60)
        for step_data in checklist['steps']:
            status = "✅" if step_data['completed'] else "⬜"
            print(f"{status} Step {step_data['step']}: {step_data['name']}")
            print(f"   Locations: {', '.join(step_data['locations'])}")
        print("=" * 60)
        
        return checklist
    
    def apply_power_user_techniques(self) -> Dict[str, Any]:
        """
        Apply Power User Methodology.
        
        Strategic context loading and parallel processing for 6x efficiency.
        
        Returns:
            Power user technique guide
        """
        print("🦆 Duck: Applying Power User Methodology")
        
        pattern = self.duck.pattern_engine.get_pattern(
            "Power User Methodology"
        )
        
        techniques = {
            "pattern": "Power User Methodology",
            "confidence": pattern['confidence'],
            "efficiency_gain": "6x faster analysis, 3x overall productivity",
            
            "strategic_context_loading": {
                "layer_1": {
                    "name": "Foundation",
                    "files": [
                        ".cursor/guides/project/context.md",
                        ".cursor/logs/active/current_focus.md",
                        ".cursor/plans/next_targets.md",
                    ],
                    "parallel": True,
                },
                "layer_2": {
                    "name": "Strategy",
                    "files": [
                        ".cursor/guides/refactoring/playbook.md",
                        ".cursor/examples/breakthrough_pattern.py",
                        ".cursor/logs/decisions/architecture_decisions.md",
                    ],
                    "parallel": True,
                },
                "layer_3": {
                    "name": "Implementation",
                    "files": [
                        "current_work_files",
                        ".cursor/templates/validation_template.py",
                        ".cursor/rules/scientific.mdc",
                    ],
                    "parallel": True,
                },
                "layer_4": {
                    "name": "Validation",
                    "files": [
                        "original_system_files",
                        "refactored_system_files",
                        ".cursor/prompts/before_commit_validation.md",
                    ],
                    "parallel": True,
                },
            },
            
            "parallel_processing": {
                "technique": "Load all independent files simultaneously",
                "benefit": "6x faster than sequential loading",
                "example": "Load 6 files in parallel instead of 1 at a time",
            },
            
            "incremental_validation": {
                "technique": "Validate after each major change",
                "benefit": "Catch issues early, reduce debugging time",
                "process": "Component change → Immediate validation → Continue",
            },
        }
        
        print("\n⚡ POWER USER TECHNIQUES")
        print("=" * 60)
        print(f"Efficiency Gain: {techniques['efficiency_gain']}")
        print("\n📚 Strategic Context Loading (4 Layers):")
        for layer_key, layer_data in techniques['strategic_context_loading'].items():
            print(f"\n  {layer_data['name']}:")
            for file_path in layer_data['files']:
                print(f"    - {file_path}")
            if layer_data['parallel']:
                print(f"    ⚡ Load in parallel!")
        print("=" * 60)
        
        return techniques
    
    def get_pattern_recommendation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get Duck's recommendation for which pattern to apply.
        
        Args:
            context: Context dictionary with task information
        
        Returns:
            Pattern recommendation with confidence
        """
        task_type = context.get('task_type', 'unknown')
        complexity = context.get('complexity', 'moderate')
        
        recommendations = []
        
        # Configuration pattern for refactoring
        if task_type == 'refactoring':
            recommendations.append({
                "pattern": "Revolutionary Configuration Pattern",
                "confidence": 95.0,
                "rationale": "Proven pattern for module refactoring",
            })
        
        # Systematic analysis for new work
        if context.get('new_session', False):
            recommendations.append({
                "pattern": "Systematic Repository Analysis Protocol",
                "confidence": 98.0,
                "rationale": "Mandatory before starting any work",
            })
        
        # Thinktank for complex tasks
        if complexity in ['complex', 'very_complex']:
            recommendations.append({
                "pattern": "Thinktank Methodology",
                "confidence": 91.0,
                "rationale": "Complex task requires structured planning",
            })
        
        # Scientific rigor always applies
        recommendations.append({
            "pattern": "Scientific Rigor Standards",
            "confidence": 97.0,
            "rationale": "100% functionality preservation required",
        })
        
        return {
            "context": context,
            "recommendations": recommendations,
            "top_pattern": recommendations[0] if recommendations else None,
        }


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def apply_configuration_pattern(module_name: str, module_path: str) -> Dict[str, Any]:
    """
    Quick function to apply configuration pattern.
    
    Example:
        >>> plan = apply_configuration_pattern("path", "Codes_Working/Config/path.py")
    """
    applicator = PatternApplicator()
    return applicator.apply_configuration_pattern(module_name, Path(module_path))


def analyze_repository(repo_path: str = ".") -> Dict[str, Any]:
    """
    Quick function to run systematic repository analysis.
    
    Example:
        >>> checklist = analyze_repository()
    """
    applicator = PatternApplicator()
    return applicator.apply_systematic_analysis(Path(repo_path))


def get_power_user_guide() -> Dict[str, Any]:
    """
    Quick function to get power user techniques guide.
    
    Example:
        >>> guide = get_power_user_guide()
    """
    applicator = PatternApplicator()
    return applicator.apply_power_user_techniques()


# ============================================================================
# MAIN CLI
# ============================================================================

def main():
    """Command-line interface for Duck pattern application"""
    import sys
    
    if len(sys.argv) < 2:
        print("""
🦆 Duck Pattern Application Templates

Usage:
    python duck_patterns.py config <module_name>
    python duck_patterns.py analyze
    python duck_patterns.py poweruser
    
Examples:
    # Apply configuration pattern
    python duck_patterns.py config path
    
    # Run systematic repository analysis
    python duck_patterns.py analyze
    
    # Get power user techniques guide
    python duck_patterns.py poweruser
""")
        sys.exit(1)
    
    command = sys.argv[1]
    applicator = PatternApplicator()
    
    if command == "config":
        if len(sys.argv) < 3:
            print("❌ Usage: python duck_patterns.py config <module_name>")
            sys.exit(1)
        
        module_name = sys.argv[2]
        module_path = Path(f"Codes_Working/Config/{module_name}.py")
        applicator.apply_configuration_pattern(module_name, module_path)
        
    elif command == "analyze":
        applicator.apply_systematic_analysis(Path("."))
        
    elif command == "poweruser":
        applicator.apply_power_user_techniques()
        
    else:
        print(f"❌ Unknown command: {command}")
        print("   Valid commands: config, analyze, poweruser")
        sys.exit(1)


if __name__ == "__main__":
    main()

