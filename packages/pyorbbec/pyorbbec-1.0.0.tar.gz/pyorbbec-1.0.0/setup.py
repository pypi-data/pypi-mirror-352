from setuptools import setup, find_packages

setup(
    name="pyorbbec",
    version="1.0.0",
    description="Your package description",
    author="alvisli",
    author_email="605633002@qq.com",
    url="https://orbbec.com.cn/",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "requests",  # 举例：你的依赖
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    package_data={
        'pyorbbec': ['*.pyd', '*.dll', '*.lib'],  # 主包目录
        'pyorbbec.extensions': ['*', '**/*'],  # 递归包含所有文件
    },
    include_package_data=True,  # 确保package_data被包含
)