# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
LONGDOC = """
log5
=====================

Output logs, documentation -

https://github.com/hailiang-wang/python-log5

"""

setup(
    name='log5',
    version='0.0.3',
    description='Output logs',
    long_description=LONGDOC,
    author='Hai Liang Wang',
    author_email='hailiang.hl.wang@gmail.com',
    url='https://github.com/hailiang-wang/python-log5',
    license="Chunsong Public License, version 1.0",
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Natural Language :: Chinese (Simplified)',
        'Natural Language :: Chinese (Traditional)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11'
    ],
    keywords='logging',
    packages=find_packages(),
    install_requires=[
        'env3>=0.0.3'
    ],
    package_data={
        'log5': [
            'LICENSE']})
