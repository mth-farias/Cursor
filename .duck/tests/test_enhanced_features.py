#!/usr/bin/env python3
"""
🦆 Duck Enhanced Features Test Suite

Tests for the new enhanced CLI commands and advanced pattern engine.
"""

import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import Duck components
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from duck.core.patterns import PatternDiscoveryEngine, PatternRecommendation
from duck.core.analytics import DuckAnalytics, UsageEvent, PatternOutcome
from duck.cli.commands import (
    cmd_pattern, cmd_analyze, cmd_decision, cmd_memory, 
    cmd_performance, cmd_analytics
)


class TestPatternDiscovery(unittest.TestCase):
    """Test the advanced pattern discovery engine"""
    
    def setUp(self):
        self.discovery_engine = PatternDiscoveryEngine()
    
    def test_pattern_discovery_engine_initialization(self):
        """Test that the discovery engine initializes correctly"""
        self.assertIsNotNone(self.discovery_engine)
        self.assertIsNotNone(self.discovery_engine.pattern_signals)
        self.assertIn("Revolutionary Configuration Pattern", self.discovery_engine.pattern_signals)
    
    def test_file_analysis_basic(self):
        """Test basic file analysis functionality"""
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""#%% CELL 00 — HEADER
import numpy as np
import pathlib
from typing import Dict

#%% CELL 01 — CONSTANTS
CONFIG_VAR = "test"
SIZE_THRESHOLD = 200

#%% CELL 02 — FUNCTIONS
def test_function():
    return "test"

class TestClass:
    pass
""")
            temp_file = Path(f.name)
        
        try:
            analysis = self.discovery_engine._analyze_file(temp_file)
            
            # Check basic analysis results
            self.assertGreater(analysis['line_count'], 0)
            self.assertTrue(analysis['has_cell_structure'])
            self.assertGreater(analysis['import_count'], 0)
            self.assertGreater(analysis['function_count'], 0)
            self.assertGreater(analysis['class_count'], 0)
            self.assertIn('large_module', analysis['complexity_indicators'])
            
        finally:
            temp_file.unlink()
    
    def test_pattern_recommendation_generation(self):
        """Test pattern recommendation generation"""
        # Create a test file that should trigger configuration pattern
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""#%% CELL 00 — HEADER
import numpy as np
from typing import Dict

#%% CELL 01 — CONSTANTS
CONFIG_VAR = "test"

#%% CELL 02 — FUNCTIONS
def test_function():
    return "test"
""" * 50)  # Make it large enough to trigger size threshold
            temp_file = Path(f.name)
        
        try:
            recommendations = self.discovery_engine.discover_patterns(temp_file)
            
            # Should find at least one recommendation
            self.assertGreater(len(recommendations), 0)
            
            # Check recommendation structure
            rec = recommendations[0]
            self.assertIn('pattern_name', rec)
            self.assertIn('confidence', rec)
            self.assertIn('rationale', rec)
            self.assertIn('evidence', rec)
            self.assertIn('applicability_score', rec)
            self.assertIn('context_signals', rec)
            
            # Should recommend configuration pattern for this file
            config_recs = [r for r in recommendations if 'Configuration Pattern' in r['pattern_name']]
            self.assertGreater(len(config_recs), 0)
            
        finally:
            temp_file.unlink()
    
    def test_explain_recommendation(self):
        """Test recommendation explanation generation"""
        recommendation = PatternRecommendation(
            pattern_name="Test Pattern",
            confidence=85.0,
            rationale="Test rationale",
            evidence=["Evidence 1", "Evidence 2"],
            applicability_score=0.8,
            context_signals={"test_signal": True}
        )
        
        explanation = self.discovery_engine.explain_recommendation(recommendation)
        
        self.assertIn("Test Pattern", explanation)
        self.assertIn("85.0%", explanation)
        self.assertIn("Test rationale", explanation)
        self.assertIn("Evidence 1", explanation)


class TestAnalytics(unittest.TestCase):
    """Test the analytics and learning system"""
    
    def setUp(self):
        # Use temporary directory for analytics data
        self.temp_dir = tempfile.mkdtemp()
        self.analytics = DuckAnalytics()
        self.analytics.data_dir = Path(self.temp_dir)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_analytics_initialization(self):
        """Test analytics system initialization"""
        self.assertIsNotNone(self.analytics)
        self.assertIsNotNone(self.analytics.session_id)
        self.assertIsNotNone(self.analytics.start_time)
    
    def test_log_command_execution(self):
        """Test command execution logging"""
        event_id = self.analytics.log_command_execution(
            command="test_command",
            success=True,
            duration_ms=150,
            metadata={"test": "value"}
        )
        
        self.assertIsNotNone(event_id)
        
        # Check that event was logged
        usage_events = self.analytics._read_events("usage", self.analytics.start_time - timedelta(days=1))
        self.assertGreater(len(usage_events), 0)
        
        # Check event content
        event = usage_events[0]
        self.assertEqual(event['command'], 'test_command')
        self.assertTrue(event['success'])
        self.assertEqual(event['duration_ms'], 150)
    
    def test_log_pattern_application(self):
        """Test pattern application logging"""
        event_id = self.analytics.log_pattern_application(
            pattern_name="Test Pattern",
            module_name="test_module",
            success=True,
            line_reduction=60.5,
            preservation_rate=100.0,
            duration_ms=300
        )
        
        self.assertIsNotNone(event_id)
        
        # Check that event was logged
        pattern_events = self.analytics._read_events("patterns", self.analytics.start_time - timedelta(days=1))
        self.assertGreater(len(pattern_events), 0)
        
        # Check event content
        event = pattern_events[0]
        self.assertEqual(event['pattern_name'], 'Test Pattern')
        self.assertEqual(event['module_name'], 'test_module')
        self.assertTrue(event['success'])
        self.assertEqual(event['line_reduction'], 60.5)
        self.assertEqual(event['preservation_rate'], 100.0)
    
    def test_usage_summary_generation(self):
        """Test usage summary generation"""
        # Log some test events
        self.analytics.log_command_execution("test1", True, 100)
        self.analytics.log_command_execution("test2", True, 200)
        self.analytics.log_command_execution("test3", False, 50)
        
        summary = self.analytics.get_usage_summary(days=1)
        
        self.assertEqual(summary['total_commands'], 3)
        self.assertEqual(summary['successful_commands'], 2)
        self.assertAlmostEqual(summary['success_rate'], 66.67, places=1)
        self.assertAlmostEqual(summary['avg_execution_time_ms'], 116.67, places=1)
    
    def test_clear_analytics_data(self):
        """Test analytics data clearing"""
        # Log some data
        self.analytics.log_command_execution("test", True, 100)
        
        # Clear data
        success = self.analytics.clear_analytics_data()
        self.assertTrue(success)
        
        # Verify data is cleared
        usage_events = self.analytics._read_events("usage", self.analytics.start_time - timedelta(days=1))
        self.assertEqual(len(usage_events), 0)


class TestCLICommands(unittest.TestCase):
    """Test the enhanced CLI commands"""
    
    def test_pattern_suggest_command_args(self):
        """Test pattern suggest command argument handling"""
        # Mock argparse args
        class MockArgs:
            action = "suggest"
            path = "test_file.py"
        
        # Mock the file analysis to avoid file system dependencies
        with patch('duck.cli.commands.Path') as mock_path:
            mock_path.return_value.exists.return_value = True
            with patch('duck.cli.commands.PatternDiscoveryEngine') as mock_engine:
                mock_engine.return_value.discover_patterns.return_value = []
                
                # This should not raise an exception
                result = cmd_pattern(MockArgs())
                self.assertEqual(result, 0)
    
    def test_analyze_deps_command_args(self):
        """Test analyze deps command argument handling"""
        class MockArgs:
            target = "deps"
            tree = False
            module = None
        
        with patch('duck.cli.commands._analyze_dependencies') as mock_deps:
            mock_deps.return_value = {'success': True, 'dependencies': {}, 'tree_output': []}
            
            result = cmd_analyze(MockArgs())
            self.assertEqual(result, 0)
    
    def test_decision_log_command_args(self):
        """Test decision log command argument handling"""
        class MockArgs:
            action = "log"
            summary = False
        
        with patch('duck.cli.commands.create_duck') as mock_duck:
            mock_duck_instance = MagicMock()
            mock_duck_instance.decision_engine.decisions = []
            mock_duck.return_value = mock_duck_instance
            
            result = cmd_decision(MockArgs())
            self.assertEqual(result, 0)
    
    def test_memory_stats_command_args(self):
        """Test memory stats command argument handling"""
        class MockArgs:
            action = "stats"
        
        with patch('duck.cli.commands.create_duck') as mock_duck:
            mock_duck_instance = MagicMock()
            mock_duck_instance.memory_system.memory_threshold = 0.95
            mock_duck_instance.memory_system.core_memories = []
            mock_duck_instance.memory_system.pattern_library = []
            mock_duck_instance.memory_system.get_user_philosophy.return_value = {}
            mock_duck_instance.pattern_engine.get_high_confidence_patterns.return_value = []
            mock_duck.return_value = mock_duck_instance
            
            result = cmd_memory(MockArgs())
            self.assertEqual(result, 0)
    
    def test_analytics_report_command_args(self):
        """Test analytics report command argument handling"""
        class MockArgs:
            action = "report"
            days = 30
        
        with patch('duck.cli.commands.get_analytics') as mock_analytics:
            mock_analytics_instance = MagicMock()
            mock_report = MagicMock()
            mock_report.total_commands = 10
            mock_report.success_rate = 90.0
            mock_report.avg_execution_time = 150.0
            mock_report.top_patterns = []
            mock_report.decision_distribution = {}
            mock_report.learning_insights = []
            mock_analytics_instance.generate_comprehensive_report.return_value = mock_report
            mock_analytics.return_value = mock_analytics_instance
            
            result = cmd_analytics(MockArgs())
            self.assertEqual(result, 0)


class TestIntegration(unittest.TestCase):
    """Integration tests for the enhanced features"""
    
    def test_pattern_suggest_integration(self):
        """Test end-to-end pattern suggestion workflow"""
        # Create a realistic test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""#%% CELL 00 — HEADER & OVERVIEW
\"\"\"
Test configuration module for Duck pattern discovery testing.
\"\"\"

import numpy as np
from typing import Dict, List
from pathlib import Path

#%% CELL 01 — USER CONSTANTS
EXPERIMENT_NAME = "test_experiment"
FRAME_RATE = 30.0
ARENA_SIZE = (100, 100)

#%% CELL 02 — CONFIGURATION FUNCTIONS
def configure_experiment():
    \"\"\"Configure experiment parameters\"\"\"
    return {
        "name": EXPERIMENT_NAME,
        "frame_rate": FRAME_RATE,
        "arena_size": ARENA_SIZE
    }

def validate_config(config: Dict) -> bool:
    \"\"\"Validate configuration parameters\"\"\"
    return all(key in config for key in ["name", "frame_rate", "arena_size"])

#%% CELL 03 — MAIN CONFIGURATION
CONFIG = configure_experiment()
""")
            temp_file = Path(f.name)
        
        try:
            # Test pattern discovery
            discovery_engine = PatternDiscoveryEngine()
            recommendations = discovery_engine.discover_patterns(temp_file)
            
            # Should find configuration pattern recommendation
            self.assertGreater(len(recommendations), 0)
            
            config_recs = [r for r in recommendations if 'Configuration Pattern' in r['pattern_name']]
            if config_recs:
                rec = config_recs[0]
                self.assertGreater(rec['confidence'], 50)  # Should have decent confidence
                self.assertIn('cell_structure', rec['context_signals'])
                self.assertIn('CELL', str(rec['evidence']))
            
        finally:
            temp_file.unlink()


if __name__ == '__main__':
    # Import required modules for tests
    from datetime import timedelta
    
    # Run tests
    unittest.main(verbosity=2)
