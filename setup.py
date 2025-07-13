#!/usr/bin/env python3
"""
Setup script for FinOpsOptimizer.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="finopsoptimizer",
    version="1.0.0",
    author="FinOpsOptimizer Team",
    author_email="support@finopsoptimizer.com",
    description="A comprehensive multi-cloud cost optimization toolkit for AWS, Azure, and GCP",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/manikantesh/finopsoptimizer",
    project_urls={
        "Bug Tracker": "https://github.com/manikantesh/finopsoptimizer/issues",
        "Documentation": "https://docs.finopsoptimizer.com",
        "Source Code": "https://github.com/manikantesh/finopsoptimizer",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.3.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.3.0",
            "pre-commit>=3.0.0",
        ],
        "docs": [
            "mkdocs-material>=9.0.0",
            "mike>=1.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "finops=cli:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "finops": ["*.yml", "*.yaml", "*.json"],
    },
    keywords="finops, cloud, cost, optimization, aws, azure, gcp, cost-management",
    zip_safe=False,
) 