import os, sys, json
from setuptools import find_packages, setup

with open("app/Readme.md", "r", encoding="utf-8") as f:
    long_description =  f.read()


setup(
    name = "memoryawarestruct",
    version="0.0.12",
    description="MemoryAwareStruct is a secure and protected data structure system with high-level protection against unauthorized modification.",
    package_dir={"": "app"},
    packages=find_packages(where="app", include=["memoryawarestruct", "test", "memoryawarestruct.*", "test.*"]),
    include_package_data=True,
    long_description= long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LcfherShell/MemoryAwareStruct",
    author="LcfherShell",
    author_email="",
    license="MIT",
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)