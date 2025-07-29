#!/usr/bin/env python3
"""
Setup script for the EasyGit CLI
"""

from setuptools import setup, find_packages

setup(
    name="git-simplified",
    version="1.0.0",
    description="A beginner-friendly Git CLI with colorful output",
    author="QinCai-rui",
    author_email="raymontqin_rui@outlook.com",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "easygit=easygit.__main__:main",
        ],
    },
    install_requires=[
        "colorama",
    ],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Version Control :: Git",
        "Operating System :: OS Independent",

    ],
)
