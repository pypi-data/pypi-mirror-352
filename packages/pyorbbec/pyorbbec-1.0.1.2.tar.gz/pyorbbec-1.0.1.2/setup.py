#!/usr/bin/env python
import os
import sys

from setuptools import setup, find_packages
    
setup(
    name="pyorbbec",
    version="1.0.1.2",
    description="Python interface to the Orbbec SDK.",
    long_description_content_type="text/markdown",
    author="orbbec",
    author_email="lijie@orbbec.com",
    url="https://orbbec.com.cn/",
    packages=find_packages(where="src", include=["pyorbbecsdk", "pyorbbecsdk.*"]),
    package_dir={"": "src"},
    python_requires=">=3.8",
    license="Apache-2.0",
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
    ],
    package_data={
        'pyorbbecsdk': ['*.pyd', '*.dll', '*.lib'],  # 主包目录
    },
    include_package_data=True,  # 确保package_data被包含
)