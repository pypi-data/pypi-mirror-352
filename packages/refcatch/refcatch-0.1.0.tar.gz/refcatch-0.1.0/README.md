# RefCatch

A Python package for processing academic references from plaintext files. RefCatch extracts references from text files (markdown, txt, etc.), attempts to find their DOIs using the CrossRef API, and outputs the results.

## Installation

```bash
pip install refcatch
```

Or install directly from the repository:

```bash
git clone https://github.com/AhsanKhodami/refcatch.git
cd refcatch
pip install -e .
```

## Publishing to PyPI

To publish RefCatch to PyPI:

```bash
# Install build and twine
pip install build twine

# Build the package
python -m build

# Upload to PyPI (use --repository-url https://test.pypi.org/legacy/ for TestPyPI)
python -m twine upload dist/*
```

## Usage

### As a Python Package

```python
from refcatch import refcatch

# Basic usage
refcatch("path/to/references.md", "path/to/output.md")

# With all options
refcatch(
    input_file="path/to/references.md", 
    output_file="path/to/output.md",
    doi_file="path/to/dois.txt",  # Optional, will be auto-generated if not provided
    log=True  # Set to False to disable logging
)
```

### Command Line Interface

```bash
# Basic usage
refcatch references.md

# Specify output file
refcatch references.md -o output.md

# Specify DOI file and run silently
refcatch references.md -o output.md -d dois.txt --silent
```

## Example

Input file (references.md):
```
1.	Wong WL, Su X, Li X, et al. Global prevalence of age-related macular degeneration and disease burden projection for 2020 and 2040: a systematic review and meta-analysis. Lancet Glob Health. 2014;2(2):e106-116.
2.	Flaxman SR, Bourne RRA, Resnikoff S, et al. Global causes of blindness and distance vision impairment 1990-2020: a systematic review and meta-analysis. Lancet Glob Health. 2017;5(12):e1221-e1234.
```

Output file:
```
1.	Wong WL, Su X, Li X, et al. Global prevalence of age-related macular degeneration and disease burden projection for 2020 and 2040: a systematic review and meta-analysis. Lancet Glob Health. 2014;2(2):e106-116.
    DOI: 10.1016/S2214-109X(13)70145-1
2.	Flaxman SR, Bourne RRA, Resnikoff S, et al. Global causes of blindness and distance vision impairment 1990-2020: a systematic review and meta-analysis. Lancet Glob Health. 2017;5(12):e1221-e1234.
    DOI: 10.1016/S2214-109X(17)30393-5
```

## Features

- Extracts references from plaintext files
- Makes multiple attempts to find DOIs with different search strategies
- Outputs references with their DOIs
- Saves DOIs to a separate file
- Optional logging of the process
- Simple command-line interface

## License

MIT
