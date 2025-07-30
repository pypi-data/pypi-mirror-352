"""
Setup file for RefCatch package.
"""

from setuptools import setup, find_packages
import os

# Read the contents of README.md
with open(os.path.join(os.path.dirname(__file__), "README.md"), "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="refcatch",
    version="0.1.0",
    author="Mohammad Ahsan Khodami",
    author_email="ahsan.khodami@gmail.com",
    description="A package for processing academic references from plaintext files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AhsanKhodami/refcatch",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Text Processing :: Markup :: Markdown",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": [
            "refcatch=refcatch.cli:main",
        ],
    },
    package_data={
        "refcatch": ["*.md"],
    },
    include_package_data=True,
    zip_safe=False,
)
