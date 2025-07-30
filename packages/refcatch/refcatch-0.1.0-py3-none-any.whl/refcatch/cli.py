"""
Command line interface for RefCatch.
"""

import argparse
import os
from .core import refcatch

def main():
    """
    Command line entry point for RefCatch.
    """
    parser = argparse.ArgumentParser(
        description="RefCatch - Extract references and find DOIs from plaintext files"
    )
    
    parser.add_argument(
        "input", 
        help="Path to input file containing references"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Path to output file (default: [input]_with_dois.[ext])"
    )
    
    parser.add_argument(
        "-d", "--doi-file",
        help="Path to save just the DOIs (default: [output]_dois.txt)"
    )
    
    parser.add_argument(
        "--silent",
        action="store_true",
        help="Run silently without logging progress"
    )
    
    args = parser.parse_args()
    
    # Set default output file if not provided
    if args.output is None:
        input_base = os.path.splitext(args.input)
        args.output = f"{input_base[0]}_with_dois{input_base[1]}"
    
    # Run the main function
    success, message, doi_count = refcatch(
        args.input, 
        args.output, 
        args.doi_file,
        log=not args.silent
    )
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
