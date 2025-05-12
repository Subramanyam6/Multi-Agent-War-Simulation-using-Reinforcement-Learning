#!/usr/bin/env python3
"""
Main entry point for running the Multi-Agent War Simulation

This script allows running the simulation from the project's root directory.
"""

import os
import sys

# Add the CodeBase directory to the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'CodeBase'))

# Import the main function from Run.py
from Run import main

if __name__ == '__main__':
    main() 