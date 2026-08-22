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
    version="2.0.0",
    author="FinOpsOptimizer Team",
    author_email="support@finopsoptimizer.com",
    description="Enterprise-grade cost optimization for multi-cloud environments",
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
    install_requires=[
        # core dependencies
    ],
    extras_require={
        'aws': ['boto3'],
        'azure': ['azure-mgmt-resource'],
        'gcp': ['google-cloud-resource-manager'],
        'oracle': [],
        'all': ['boto3', 'azure-mgmt-resource', 'google-cloud-resource-manager'],
        'agentops': ['fastapi>=0.100.0', 'uvicorn>=0.23.0', 'requests>=2.28.0'],
    },
    entry_points={
        "console_scripts": [
            "finops=cli:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "finops": ["*.yml", "*.yaml", "*.json"],
        "finops.agentops": ["static/*.html"],
    },
    keywords="finops, cloud, cost, optimization, aws, azure, gcp, cost-management",
    zip_safe=False,
) 