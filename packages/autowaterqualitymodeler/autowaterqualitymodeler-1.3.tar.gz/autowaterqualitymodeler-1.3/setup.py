#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
仅用于兼容旧版本pip的安装桥接文件。
对于现代Python包，推荐使用pyproject.toml。
"""

from setuptools import setup, find_packages

required = [
    "numpy>=1.20.0",
    "pandas>=1.3.0",
    "scipy>=1.7.0",
    "matplotlib>=3.4.0",
    "cryptography>=36.0.0",
    "openpyxl>=3.0.0",
    "scikit-learn>=1.0.0"
]

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="autowaterqualitymodeler",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    author="周元琦",
    author_email="zyq1034378361@gmail.com",
    description="一键式水质光谱建模工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(include=["autowaterqualitymodeler", "autowaterqualitymodeler.*"]),
    include_package_data=True,
    package_data={
        "autowaterqualitymodeler": ["config/*.json", "resources/*.xlsx", "resources/*.txt"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=required,
    entry_points={
        "console_scripts": [
            "autowaterquality=autowaterqualitymodeler.run:main",
        ],
    },
)
