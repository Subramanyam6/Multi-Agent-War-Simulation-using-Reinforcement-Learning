#!/usr/bin/env python3
"""
Main entry point for running the Multi-Agent War Simulation with PyGame visualization
"""

import os
import sys

# Add the CodeBase directory to the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'CodeBase'))

# Import the main function from visualize_simulation.py in CodeBase
from CodeBase.visualize_simulation import main

if __name__ == '__main__':
    main() 