from setuptools import setup, find_packages

setup(
    name="betteryeah",
    version="0.2.23",
    packages=find_packages(),
    description="this package is design by betteryeah.this client is package that to enhance user ability",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author="ciqian",
    author_email="ciqian@bantouyan.com",
    install_requires=[
        # 依赖列表
    ],
    python_requires='>=3.10',  # 指定支持的最低Python版本
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
