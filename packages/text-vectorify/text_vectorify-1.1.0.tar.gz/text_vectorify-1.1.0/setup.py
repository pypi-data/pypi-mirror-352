#!/usr/bin/env python3

from setuptools import setup, find_packages
from pathlib import Path

def read_file(file_path):
    return Path(file_path).read_text(encoding="utf-8").strip()

def get_version():
    init_file = Path("text_vectorify") / "__init__.py"
    content = read_file(init_file)
    for line in content.split('\n'):
        if line.startswith('__version__'):
            return line.split('=')[1].strip().strip('"').strip("'")
    raise RuntimeError("Unable to find version string.")

# Read version
version = get_version()

# Read README
long_description = read_file("README.md")

setup(
    name="text-vectorify",
    version=version,
    author="changyy",
    author_email="changyy.csie@gmail.com",
    description="A powerful and flexible Python tool for text vectorization with multiple embedding models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/changyy/py-text-vectorify",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
    ],
    extras_require={
        "openai": ["openai>=1.0.0"],
        "transformers": [
            "sentence-transformers>=2.0.0", 
            "transformers>=4.0.0", 
            "torch>=1.9.0"
        ],
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.0.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "mypy>=0.900",
            "isort>=5.0.0",
        ],
        "all": [
            "openai>=1.0.0",
            "sentence-transformers>=2.0.0", 
            "transformers>=4.0.0", 
            "torch>=1.9.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "text-vectorify=text_vectorify.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
