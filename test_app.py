#!/usr/bin/env python3
"""
Test script to check application startup
"""

import os
import sys
from application import application

if __name__ == "__main__":
    print("Starting application test...")
    try:
        # Print information about the application
        print(f"Application routes: {[rule.rule for rule in application.url_map.iter_rules()]}")
        print("Application should be running correctly.")
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        import traceback
        traceback.print_exc() 