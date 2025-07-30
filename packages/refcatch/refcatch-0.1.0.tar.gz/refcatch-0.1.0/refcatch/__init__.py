"""
RefCatch - A package for processing academic references from plaintext files.

This package extracts references from plaintext files (markdown, txt, etc.),
attempts to find their DOIs, and outputs the results.
"""

from .core import refcatch

__version__ = "0.1.0"
__all__ = ["refcatch"]
