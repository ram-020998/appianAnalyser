#!/usr/bin/env python3
"""
Simple runner for the Appian Analyzer
Usage: python3 analyze_appian.py <zip_file>
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from appian_analyzer.cli import main

if __name__ == "__main__":
    main()
