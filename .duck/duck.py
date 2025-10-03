#!/usr/bin/env python3
"""
🦆 Duck - Your Revolutionary Virtual Copy

Universal command-line interface for all Duck capabilities.

Usage:
    duck status                    Show Duck's current status
    duck pattern config <module>   Apply configuration pattern
    duck validate <module>         Validate refactored module
    duck organize cursor           Organize .cursor/ folder
    duck analyze repo              Systematic repository analysis
    duck help [command]            Show help for command

Author: Matheus (Scientific Software Development Master)
Phase: Phase 2 - Platform Integration
Version: 1.0.0-beta
"""

import sys
from duck.cli.commands import main

if __name__ == "__main__":
    sys.exit(main())