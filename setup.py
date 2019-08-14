#!/usr/bin/env python

import os
import sys

from setuptools import setup


if sys.argv[-1] == "publish":
    os.system("python setup.py sdist upload")
    sys.exit()

readme = open("README.rst").read()
doclink = """
Documentation
-------------

The full documentation is at http://tdam_api.rtfd.org."""

setup(
    name="tdam_api",
    version="0.1.0",
    description="A Python client for the TDAmeritrade Trading API",
    long_description=readme + "\n\n" + doclink + "\n\n",
    author="Jyoti Basu",
    author_email="jyotibasu@engineeredtrades.com",
    url="https://github.com/jbasu/tdam_api",
    packages=["tdam_api"],
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    package_dir={"tdam_api": "tdam_api"},
    include_package_data=True,
    install_requires=[],
    license="MIT",
    zip_safe=False,
    keywords="tdam_api tdameritrade api trading stocks options",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
)
