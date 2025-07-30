"""
Setup script for the unifyops-core package.
"""

from setuptools import setup, find_packages
import re

# Read version from __init__.py
with open("unifyops_core/__init__.py", "r") as f:
    version_match = re.search(r'^__version__ = ["\']([^"\']*)["\']', f.read(), re.M)
    if version_match:
        version = version_match.group(1)
    else:
        raise RuntimeError("Unable to find version string")

# Read long description from README.md
with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="unifyops-core",
    version=version,
    packages=find_packages(),
    include_package_data=True,
    description="Core utilities for UnifyOps Python projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="UnifyOps Team",
    author_email="admin@unifyops.com",
    url="https://github.com/unifyops/unifyops-core",
    python_requires=">=3.10",
    install_requires=[
        "pydantic>=2.4.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="unifyops, utilities, logging, exceptions",
) 