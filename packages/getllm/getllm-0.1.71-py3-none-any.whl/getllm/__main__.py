#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main entry point for the getllm package when run as a module.

This allows the package to be run directly with:
    python -m getllm
"""

import sys
from getllm.cli import main

if __name__ == "__main__":
    sys.exit(main())
