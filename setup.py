#!/usr/bin/env python3
"""
OpenAGI Platform Setup Configuration
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="openagi",
    version="1.0.0",
    author="VIIICORP",
    description="Comprehensive OpenAGI platform with 14,000+ AI features",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/VIIICORP/OpenAGI",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scikit-learn>=1.0.0",
        "tensorflow>=2.8.0",
        "torch>=1.11.0",
        "transformers>=4.15.0",
        "opencv-python>=4.5.0",
        "pillow>=8.3.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
        "requests>=2.26.0",
        "flask>=2.0.0",
        "fastapi>=0.70.0",
        "uvicorn>=0.15.0",
        "pyyaml>=6.0",
        "click>=8.0.0",
        "tqdm>=4.62.0",
        "joblib>=1.1.0",
        "nltk>=3.6.0",
        "spacy>=3.4.0",
        "librosa>=0.9.0",
        "soundfile>=0.10.0",
        "beautifulsoup4>=4.10.0",
        "selenium>=4.0.0",
        "plotly>=5.0.0",
        "streamlit>=1.10.0",
        "gradio>=3.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
        ],
        "gpu": [
            "tensorflow-gpu>=2.8.0",
            "torch[cuda]>=1.11.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "openagi=openagi.cli:main",
        ],
    },
)