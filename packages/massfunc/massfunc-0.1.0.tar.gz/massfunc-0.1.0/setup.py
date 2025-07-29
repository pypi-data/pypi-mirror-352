#!/usr/bin/env python3
"""Setup script for massfunc package."""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="massfunc",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python package for cosmological mass function calculations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SOYONAOC/massfunc",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.18.0",
        "scipy>=1.5.0",
        "astropy>=4.0",
        "matplotlib>=3.0.0",
        "sympy>=1.6.0",
        "joblib>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
            "numpydoc>=1.1",
        ],
    },
    project_urls={

    "Bug Reports": "https://github.com/SOYONAOC/MassFunction/issues",

    "Source": "https://github.com/SOYONAOC/MassFunction",
    
    },
)
