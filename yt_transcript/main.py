#!/usr/bin/env python3
"""Main entry point for the YouTube transcript RAG application."""

import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.cli import setup_argparse

def main():
    """Main entry point."""
    parser = setup_argparse()
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
