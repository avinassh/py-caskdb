#!/usr/bin/env python

from setuptools import setup, find_packages

with open("version.txt") as f:
    version = f.read().strip()

setup(
    name="cdbpie",
    version=version,
    author="Avinash Sajjanshetty",
    author_email="opensource@avi.im",
    packages=["cdbpie", "."],
    package_dir={"cdbpie": ""},
    include_package_data=True,
    test_suite="tests",
    url="https://github.com/avinassh/cdb/",
    license="MIT",
    description="Disk based Log Structured Hash Table Store",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
)
