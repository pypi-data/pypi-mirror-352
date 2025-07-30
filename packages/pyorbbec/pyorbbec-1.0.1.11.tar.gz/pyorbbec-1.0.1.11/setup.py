# ******************************************************************************
#  Copyright (c) 2024 Orbbec 3D Technology, Inc
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http:# www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# ******************************************************************************

import os
import shutil

from setuptools import setup, find_packages

requires = [
    'pybind11==2.11.0',
    'pybind11-global==2.11.0',
    'opencv-python',
    'wheel',
    'numpy<2.0',  # see https://github.com/orbbec/pyorbbecsdk/issues/47
    'av',         # for h264 decoding
    'pygame',     # for visualization
    'pynput',     # for keyboard input
]

setup(
    name="pyorbbec",
    version="1.0.1.11",
    description="Python interface to the Orbbec SDK.",
    long_description_content_type="text/markdown",
    author="orbbec",
    author_email="lijie@orbbec.com",
    url="https://orbbec.com.cn/",
    packages=find_packages(where="src", include=["pyorbbecsdk", "pyorbbecsdk.*"]),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=requires,
    license="Apache-2.0",
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
    ],
    package_data={
        'pyorbbecsdk': ['*.pyd', '*.dll', '*.lib', '*.xml'],  # 主包目录
    },
    include_package_data=True,  # 确保package_data被包含
)