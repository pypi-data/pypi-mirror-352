#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="llm-context-builder",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Export any project to a single text file optimized for LLM context",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/llm-context-builder",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Documentation",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "colorama>=0.4.0",
        "pathspec>=0.10.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
        "tokens": [
            "tiktoken>=0.4.0",  # For OpenAI token counting
        ]
    },
    entry_points={
        "console_scripts": [
            "export_project=llm_context_builder.main:cli",
            "llm-export=llm_context_builder.main:cli",
        ],
    },
    keywords="llm context export project documentation ai",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/llm-context-builder/issues",
        "Source": "https://github.com/yourusername/llm-context-builder",
        "Documentation": "https://github.com/yourusername/llm-context-builder#readme",
    },
)