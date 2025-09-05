#!/usr/bin/env python3
"""
OpenAGI - Comprehensive AI Platform with Self-Testing Features
"""

from setuptools import setup, find_packages
import os

# Read the README file
current_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(current_dir, "README.md"), "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="openagi",
    version="1.0.0",
    author="VIIICORP",
    author_email="contact@viiicorp.com",
    description="Comprehensive OpenAGI platform with 30M+ Self Test AI features",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/VIIICORP/OpenAGI",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.5.0",
        "sqlalchemy>=2.0.0",
        "alembic>=1.13.0",
        "redis>=5.0.0",
        "celery>=5.3.0",
        "numpy>=1.24.0",
        "pandas>=2.1.0",
        "scikit-learn>=1.3.0",
        "torch>=2.1.0",
        "transformers>=4.35.0",
        "opencv-python>=4.8.0",
        "Pillow>=10.0.0",
        "requests>=2.31.0",
        "aiohttp>=3.9.0",
        "pytest>=7.4.0",
        "pytest-asyncio>=0.21.0",
        "pytest-cov>=4.1.0",
        "black>=23.9.0",
        "flake8>=6.1.0",
        "mypy>=1.6.0",
        "pre-commit>=3.5.0",
        "docker>=6.1.0",
        "prometheus-client>=0.19.0",
        "structlog>=23.2.0",
        "python-multipart>=0.0.6",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "python-dotenv>=1.0.0",
        "httpx>=0.25.0",
        "websockets>=12.0",
        "streamlit>=1.28.0",
        "gradio>=4.0.0",
        "matplotlib>=3.8.0",
        "seaborn>=0.13.0",
        "plotly>=5.17.0",
        "jupyter>=1.0.0",
        "notebook>=7.0.0",
    ],
    extras_require={
        "dev": [
            "pytest-xdist>=3.3.0",
            "coverage>=7.3.0",
            "bandit>=1.7.5",
            "safety>=2.3.0",
            "sphinx>=7.2.0",
            "sphinx-rtd-theme>=1.3.0",
        ],
        "gpu": [
            "torch[gpu]>=2.1.0",
            "tensorflow-gpu>=2.14.0",
        ],
        "cloud": [
            "boto3>=1.34.0",
            "google-cloud-storage>=2.10.0",
            "azure-storage-blob>=12.19.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "openagi=openagi.cli:main",
            "openagi-server=openagi.server:main",
            "openagi-worker=openagi.worker:main",
            "openagi-test=openagi.testing.runner:main",
        ],
    },
    include_package_data=True,
    package_data={
        "openagi": [
            "configs/*.yaml",
            "configs/*.json",
            "templates/*.html",
            "static/**/*",
            "models/*.json",
            "schemas/*.json",
        ],
    },
)