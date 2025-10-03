@echo off
REM 🦆 Duck Universal Command Launcher for Windows
REM 
REM This batch file makes the duck command available system-wide.
REM 
REM Usage: duck <command> [options]
REM
REM Installation options:
REM   1. Add this directory to your PATH environment variable (current method)
REM   2. Use console script: pip install -e .duck (then run "duck" directly)
REM
REM Note: After installing as package, you can use "duck" command directly
REM       without this batch file. This file serves as fallback.

python "%~dp0.duck/duck.py" %*

