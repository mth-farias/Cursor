"""
🦆 Duck Analytics & Learning System

Tracks usage patterns, performance metrics, and learning outcomes
to continuously improve Duck's capabilities.

Features:
- Usage event logging
- Performance metrics tracking
- Success rate analysis
- Adaptive threshold learning
- Decision outcome tracking

Author: Matheus (Scientific Software Development Master)
Date: October 3, 2025
Status: Phase 3 - Analytics & Learning
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, TypedDict
from dataclasses import dataclass, asdict
import uuid

from .env import get_project_root
from .system import create_duck, Duck


# ============================================================================
# ANALYTICS DATA SCHEMAS
# ============================================================================

class UsageEvent(TypedDict):
    """Schema for usage event logging"""
    event_id: str
    timestamp: str
    event_type: str  # command_executed, pattern_applied, validation_outcome, etc.
    command: str
    success: bool
    duration_ms: int
    metadata: Dict[str, Any]


class PerformanceMetrics(TypedDict):
    """Schema for performance metrics"""
    metric_name: str
    value: float
    unit: str
    context: Dict[str, Any]
    timestamp: str


class PatternOutcome(TypedDict):
    """Schema for pattern application outcomes"""
    pattern_name: str
    module_name: str
    success: bool
    line_reduction: Optional[float]
    preservation_rate: Optional[float]
    duration_ms: int
    timestamp: str


class DecisionOutcome(TypedDict):
    """Schema for decision tracking"""
    decision_id: str
    decision_type: str  # A, B, C, D
    confidence: float
    outcome: str  # success, failure, partial
    learning_value: float  # 0-1, how much this teaches us
    timestamp: str


@dataclass
class AnalyticsSummary:
    """Summary statistics for analytics"""
    total_commands: int
    success_rate: float
    avg_execution_time: float
    top_patterns: List[Dict[str, Any]]
    decision_distribution: Dict[str, int]
    performance_trends: Dict[str, List[float]]
    learning_insights: List[str]


# ============================================================================
# ANALYTICS ENGINE
# ============================================================================

class DuckAnalytics:
    """
    Duck's analytics and learning system.
    
    Tracks usage patterns, performance metrics, and outcomes to continuously
    improve Duck's capabilities through adaptive learning.
    """
    
    def __init__(self, duck: Optional[Duck] = None):
        self.duck = duck or create_duck()
        self.data_dir = self._setup_data_directory()
        self.session_id = str(uuid.uuid4())[:8]
        self.start_time = datetime.now()
    
    def _setup_data_directory(self) -> Path:
        """Setup analytics data directory"""
        project_root = get_project_root()
        data_dir = project_root / ".duck" / "data" / "analytics"
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir
    
    def log_command_execution(self, command: str, success: bool, 
                            duration_ms: int, metadata: Dict[str, Any] = None) -> str:
        """
        Log a command execution event.
        
        Args:
            command: The command that was executed
            success: Whether the command succeeded
            duration_ms: Execution time in milliseconds
            metadata: Additional context data
            
        Returns:
            Event ID for tracking
        """
        event_id = str(uuid.uuid4())
        event: UsageEvent = {
            "event_id": event_id,
            "timestamp": datetime.now().isoformat(),
            "event_type": "command_executed",
            "command": command,
            "success": success,
            "duration_ms": duration_ms,
            "metadata": metadata or {}
        }
        
        self._write_event("usage", event)
        return event_id
    
    def log_pattern_application(self, pattern_name: str, module_name: str,
                              success: bool, line_reduction: Optional[float] = None,
                              preservation_rate: Optional[float] = None,
                              duration_ms: int = 0) -> str:
        """
        Log a pattern application outcome.
        
        Args:
            pattern_name: Name of the pattern applied
            module_name: Name of the module refactored
            success: Whether the application succeeded
            line_reduction: Percentage reduction in lines (if applicable)
            preservation_rate: Percentage of functionality preserved
            duration_ms: Time taken for application
            
        Returns:
            Event ID for tracking
        """
        event_id = str(uuid.uuid4())
        outcome: PatternOutcome = {
            "pattern_name": pattern_name,
            "module_name": module_name,
            "success": success,
            "line_reduction": line_reduction,
            "preservation_rate": preservation_rate,
            "duration_ms": duration_ms,
            "timestamp": datetime.now().isoformat()
        }
        
        self._write_event("patterns", outcome)
        return event_id
    
    def log_decision_outcome(self, decision_id: str, decision_type: str,
                           confidence: float, outcome: str, learning_value: float = 0.5) -> str:
        """
        Log the outcome of a Duck decision.
        
        Args:
            decision_id: ID of the original decision
            decision_type: Type of decision (A, B, C, D)
            confidence: Original confidence score
            outcome: Result of the decision (success, failure, partial)
            learning_value: How much this outcome teaches us (0-1)
            
        Returns:
            Event ID for tracking
        """
        event_id = str(uuid.uuid4())
        outcome_data: DecisionOutcome = {
            "decision_id": decision_id,
            "decision_type": decision_type,
            "confidence": confidence,
            "outcome": outcome,
            "learning_value": learning_value,
            "timestamp": datetime.now().isoformat()
        }
        
        self._write_event("decisions", outcome_data)
        return event_id
    
    def log_performance_metric(self, metric_name: str, value: float, 
                             unit: str = "", context: Dict[str, Any] = None) -> str:
        """
        Log a performance metric.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            unit: Unit of measurement
            context: Additional context data
            
        Returns:
            Event ID for tracking
        """
        event_id = str(uuid.uuid4())
        metric: PerformanceMetrics = {
            "metric_name": metric_name,
            "value": value,
            "unit": unit,
            "context": context or {},
            "timestamp": datetime.now().isoformat()
        }
        
        self._write_event("performance", metric)
        return event_id
    
    def _write_event(self, category: str, event_data: Dict[str, Any]):
        """Write an event to the appropriate log file"""
        log_file = self.data_dir / f"{category}.jsonl"
        
        # Add session ID to event data
        event_data["session_id"] = self.session_id
        
        # Append to JSONL file
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event_data) + "\n")
    
    def get_usage_summary(self, days: int = 30) -> Dict[str, Any]:
        """
        Get usage summary for the specified period.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Summary statistics
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Read usage events
        usage_events = self._read_events("usage", cutoff_date)
        
        # Calculate statistics
        total_commands = len(usage_events)
        successful_commands = sum(1 for event in usage_events if event.get("success", False))
        success_rate = (successful_commands / total_commands * 100) if total_commands > 0 else 0
        
        # Average execution time
        durations = [event.get("duration_ms", 0) for event in usage_events]
        avg_execution_time = sum(durations) / len(durations) if durations else 0
        
        # Command frequency
        command_counts = {}
        for event in usage_events:
            command = event.get("command", "unknown")
            command_counts[command] = command_counts.get(command, 0) + 1
        
        return {
            "period_days": days,
            "total_commands": total_commands,
            "successful_commands": successful_commands,
            "success_rate": success_rate,
            "avg_execution_time_ms": avg_execution_time,
            "command_frequency": dict(sorted(command_counts.items(), key=lambda x: x[1], reverse=True)),
            "session_count": len(set(event.get("session_id") for event in usage_events))
        }
    
    def get_pattern_effectiveness(self, days: int = 30) -> Dict[str, Any]:
        """
        Get pattern effectiveness analysis.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Pattern effectiveness statistics
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Read pattern outcomes
        pattern_events = self._read_events("patterns", cutoff_date)
        
        # Group by pattern
        pattern_stats = {}
        for event in pattern_events:
            pattern_name = event.get("pattern_name", "unknown")
            if pattern_name not in pattern_stats:
                pattern_stats[pattern_name] = {
                    "total_applications": 0,
                    "successful_applications": 0,
                    "line_reductions": [],
                    "preservation_rates": [],
                    "avg_duration_ms": 0
                }
            
            stats = pattern_stats[pattern_name]
            stats["total_applications"] += 1
            
            if event.get("success", False):
                stats["successful_applications"] += 1
            
            if event.get("line_reduction") is not None:
                stats["line_reductions"].append(event["line_reduction"])
            
            if event.get("preservation_rate") is not None:
                stats["preservation_rates"].append(event["preservation_rate"])
        
        # Calculate effectiveness metrics
        for pattern_name, stats in pattern_stats.items():
            if stats["total_applications"] > 0:
                stats["success_rate"] = (stats["successful_applications"] / stats["total_applications"]) * 100
                stats["avg_line_reduction"] = sum(stats["line_reductions"]) / len(stats["line_reductions"]) if stats["line_reductions"] else 0
                stats["avg_preservation_rate"] = sum(stats["preservation_rates"]) / len(stats["preservation_rates"]) if stats["preservation_rates"] else 0
        
        return {
            "period_days": days,
            "total_patterns_used": len(pattern_stats),
            "pattern_effectiveness": pattern_stats,
            "top_patterns": sorted(pattern_stats.items(), key=lambda x: x[1]["total_applications"], reverse=True)[:5]
        }
    
    def get_decision_learning_insights(self, days: int = 30) -> Dict[str, Any]:
        """
        Get insights from decision outcomes for learning.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Decision learning insights
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Read decision outcomes
        decision_events = self._read_events("decisions", cutoff_date)
        
        # Analyze decision types and outcomes
        decision_analysis = {}
        for event in decision_events:
            decision_type = event.get("decision_type", "unknown")
            if decision_type not in decision_analysis:
                decision_analysis[decision_type] = {
                    "total_decisions": 0,
                    "successful_outcomes": 0,
                    "avg_confidence": 0,
                    "avg_learning_value": 0,
                    "confidence_scores": [],
                    "learning_values": []
                }
            
            analysis = decision_analysis[decision_type]
            analysis["total_decisions"] += 1
            analysis["confidence_scores"].append(event.get("confidence", 0))
            analysis["learning_values"].append(event.get("learning_value", 0))
            
            if event.get("outcome") == "success":
                analysis["successful_outcomes"] += 1
        
        # Calculate averages and insights
        insights = []
        for decision_type, analysis in decision_analysis.items():
            if analysis["total_decisions"] > 0:
                analysis["success_rate"] = (analysis["successful_outcomes"] / analysis["total_decisions"]) * 100
                analysis["avg_confidence"] = sum(analysis["confidence_scores"]) / len(analysis["confidence_scores"])
                analysis["avg_learning_value"] = sum(analysis["learning_values"]) / len(analysis["learning_values"])
                
                # Generate insights
                if analysis["success_rate"] > 80:
                    insights.append(f"Type {decision_type} decisions have high success rate ({analysis['success_rate']:.1f}%)")
                elif analysis["success_rate"] < 50:
                    insights.append(f"Type {decision_type} decisions need improvement (success rate: {analysis['success_rate']:.1f}%)")
        
        return {
            "period_days": days,
            "decision_analysis": decision_analysis,
            "insights": insights,
            "total_decisions_analyzed": len(decision_events)
        }
    
    def _read_events(self, category: str, cutoff_date: datetime) -> List[Dict[str, Any]]:
        """Read events from a category log file"""
        log_file = self.data_dir / f"{category}.jsonl"
        
        if not log_file.exists():
            return []
        
        events = []
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        event = json.loads(line.strip())
                        event_date = datetime.fromisoformat(event.get("timestamp", "1970-01-01T00:00:00"))
                        if event_date >= cutoff_date:
                            events.append(event)
                    except (json.JSONDecodeError, ValueError):
                        continue  # Skip malformed entries
        except Exception:
            pass  # Return empty list on error
        
        return events
    
    def generate_comprehensive_report(self, days: int = 30) -> AnalyticsSummary:
        """
        Generate a comprehensive analytics report.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Comprehensive analytics summary
        """
        usage_summary = self.get_usage_summary(days)
        pattern_effectiveness = self.get_pattern_effectiveness(days)
        decision_insights = self.get_decision_learning_insights(days)
        
        # Extract top patterns
        top_patterns = []
        for pattern_name, stats in pattern_effectiveness.get("pattern_effectiveness", {}).items():
            top_patterns.append({
                "pattern_name": pattern_name,
                "applications": stats["total_applications"],
                "success_rate": stats.get("success_rate", 0),
                "avg_line_reduction": stats.get("avg_line_reduction", 0)
            })
        
        # Sort by applications
        top_patterns.sort(key=lambda x: x["applications"], reverse=True)
        
        # Extract decision distribution
        decision_distribution = {}
        for decision_type, analysis in decision_insights.get("decision_analysis", {}).items():
            decision_distribution[decision_type] = analysis["total_decisions"]
        
        return AnalyticsSummary(
            total_commands=usage_summary["total_commands"],
            success_rate=usage_summary["success_rate"],
            avg_execution_time=usage_summary["avg_execution_time_ms"],
            top_patterns=top_patterns[:5],  # Top 5 patterns
            decision_distribution=decision_distribution,
            performance_trends={},  # TODO: Implement trend analysis
            learning_insights=decision_insights.get("insights", [])
        )
    
    def clear_analytics_data(self, days: int = None) -> bool:
        """
        Clear analytics data.
        
        Args:
            days: If specified, only clear data older than this many days
            
        Returns:
            True if successful
        """
        try:
            if days is None:
                # Clear all data
                for log_file in self.data_dir.glob("*.jsonl"):
                    log_file.unlink()
            else:
                # Clear data older than specified days
                cutoff_date = datetime.now() - timedelta(days=days)
                for log_file in self.data_dir.glob("*.jsonl"):
                    self._filter_events_file(log_file, cutoff_date)
            
            return True
        except Exception:
            return False
    
    def _filter_events_file(self, log_file: Path, cutoff_date: datetime):
        """Filter events in a file to keep only recent ones"""
        if not log_file.exists():
            return
        
        # Read all events
        recent_events = []
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    event = json.loads(line.strip())
                    event_date = datetime.fromisoformat(event.get("timestamp", "1970-01-01T00:00:00"))
                    if event_date >= cutoff_date:
                        recent_events.append(line.strip())
                except (json.JSONDecodeError, ValueError):
                    continue
        
        # Write back only recent events
        with open(log_file, "w", encoding="utf-8") as f:
            for line in recent_events:
                f.write(line + "\n")


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def get_analytics() -> DuckAnalytics:
    """Get Duck analytics instance"""
    return DuckAnalytics()


def log_command(command: str, success: bool, duration_ms: int, metadata: Dict[str, Any] = None) -> str:
    """Quick function to log a command execution"""
    analytics = get_analytics()
    return analytics.log_command_execution(command, success, duration_ms, metadata)


def log_pattern_outcome(pattern_name: str, module_name: str, success: bool, 
                       line_reduction: Optional[float] = None, 
                       preservation_rate: Optional[float] = None,
                       duration_ms: int = 0) -> str:
    """Quick function to log a pattern application outcome"""
    analytics = get_analytics()
    return analytics.log_pattern_application(pattern_name, module_name, success, 
                                           line_reduction, preservation_rate, duration_ms)


def generate_report(days: int = 30) -> AnalyticsSummary:
    """Quick function to generate analytics report"""
    analytics = get_analytics()
    return analytics.generate_comprehensive_report(days)
