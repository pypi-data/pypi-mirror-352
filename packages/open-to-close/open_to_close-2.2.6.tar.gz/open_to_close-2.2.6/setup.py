#!/usr/bin/env python3
"""Setup script for open-to-close package."""

from setuptools import setup, find_packages

setup(
    name="open-to-close",
    version="2.2.6",
    description="Python wrapper for the Open To Close API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="John Perry",
    author_email="john@theperry.group",
    url="https://github.com/theperrygroup/open-to-close",
    license="MIT",
    packages=find_packages(exclude=["tests", "tests_disabled", "site"]),
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "responses>=0.23.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "isort>=5.12.0",
            "pylint>=2.17.0",
            "bandit>=1.7.0",
            "pre-commit>=3.0.0",
            "types-requests>=2.25.0",
            "mkdocs>=1.5.0",
            "mkdocs-material>=9.4.0",
            "mkdocs-include-markdown-plugin>=6.0.0",
            "mkdocs-minify-plugin>=0.7.0",
            "mike>=2.0.0",
        ]
    },
    keywords=["api", "wrapper", "open-to-close", "real-estate"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Typing :: Typed",
    ],
    project_urls={
        "Homepage": "https://github.com/theperrygroup/open-to-close",
        "Bug Reports": "https://github.com/theperrygroup/open-to-close/issues",
        "Source": "https://github.com/theperrygroup/open-to-close",
    },
    include_package_data=True,
    zip_safe=False,
) 