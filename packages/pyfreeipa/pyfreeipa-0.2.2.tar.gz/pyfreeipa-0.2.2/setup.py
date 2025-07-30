#!/usr/bin/env python

"""
Install module
"""

import setuptools

setuptools.setup(
    name="pyfreeipa",
    description="Python FreeIPA API interface",
    author="Aaron Hicks",
    author_email="aethylred@gmail.com",
    version="0.2.2",
    packages=setuptools.find_packages(),
    license='Apache 2.0',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'certifi',
        'chardet',
        'idna',
        'PyYAML',
        'requests',
        'typing',
        'urllib3',
    ]
)
