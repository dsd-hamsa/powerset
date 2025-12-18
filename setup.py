#!/usr/bin/env python3
"""
Setup script for PowerTrack package installation.
Run with: python setup.py install
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="powerset",
    version="1.0.0",
    author="Joshua Hamsa",
    author_email="team@powerset.cx",
    description="Python package for AlsoEnergy PowerTrack solar monitoring platform automation.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/joshuahamsa/powerset",
    packages=find_packages(exclude=["scripts", "tests", "docs"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Monitoring",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.0.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
        ],
        "db": [
            "sqlite3",  # Built into Python
        ],
    },
    entry_points={
        "console_scripts": [
            "powerset-fetch-site-data=scripts.powertrack.fetch_site_data:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)