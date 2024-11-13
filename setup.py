#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="pgauge",
    version="0.2",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'pgauge=pgauge.__main__:main',
        ],
    },
    install_requires=[
        'colorama',
    ],
    python_requires='>=3.8',
    author="Aleksandr Karpinskii",
    author_email="homm86@gmail.com",
    # description="",
    # url="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Operating System :: MacOS :: MacOS X",
    ],
)
