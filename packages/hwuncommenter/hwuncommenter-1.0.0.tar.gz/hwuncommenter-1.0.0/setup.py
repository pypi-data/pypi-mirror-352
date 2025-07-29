#!/usr/bin/env python3

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

setup(
    name="hwuncommenter",
    version="1.0.0",
    author="MalikHw47",
    author_email="Help.malicorporation@gmail.com",
    description="Universal comment remover for any programming language",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/MalikHw47/hwuncommenter",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "HwUncommenter=hwuncommenter.main:main",
        ],
    },
    keywords="comment remover, code cleanup, source code, programming tools",
    project_urls={
        "Bug Reports": "https://github.com/MalikHw47/hwuncommenter/issues",
        "Source": "https://github.com/MalikHw47/hwuncommenter",
    },
)
