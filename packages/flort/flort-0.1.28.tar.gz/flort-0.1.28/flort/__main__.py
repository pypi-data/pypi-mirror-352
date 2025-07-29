#!/usr/bin/env python3
"""
Flort - Entry point module

This module serves as the main entry point when flort is executed as a module
using `python -m flort` or when installed as a console script.

The module simply imports and calls the main function from the CLI module,
ensuring consistent behavior regardless of how flort is invoked.
"""

from .cli import main

if __name__ == '__main__':
    main()