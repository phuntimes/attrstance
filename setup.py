#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


packages = find_packages(
    exclude=["tests"]
)


# package_data = {}


install_requirements = [
    "attrs>=18.2",
]


setup_requirements = [
    "pytest>=3.8",
    "pytest-cov",
    "pytest-pep8",
    "pytest-mypy"
]


# extra_requirements = {}


classifiers = [
    "Development Status :: 2 - Pre-Alpha"
    "Intended Audience :: Developers"
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7"
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]


setup(
    name="attrstance",
    version="0.1.0",
    packages=packages,
    url="https://github.com/phuntimes/attrstance",
    license="MIT License",
    author="Sean McVeigh",
    author_email="spmcveigh@gmail.com",
    description="validators for isinstance and issubclass",
    install_requires=install_requirements,
    setup_requires=setup_requirements,
    # extras_require=extra_requirements,
    classifiers=classifiers,
)
