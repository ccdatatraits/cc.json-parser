#!/usr/bin/env python3
"""
Setup script for JSON Parser package.
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    with open('README.md', 'r', encoding='utf-8') as f:
        return f.read()

# Read version from __init__.py
def get_version():
    with open('__init__.py', 'r') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"\'')
    return '1.0.0'

setup(
    name='json-parser',
    version=get_version(),
    description='A robust, from-scratch JSON parser implementation in Python',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    author='JSON Parser Project',
    author_email='contact@example.com',
    url='https://github.com/username/json-parser',
    license='MIT',
    
    # Package configuration
    packages=find_packages(),
    py_modules=['json_parser', 'parser', 'lexer', 'test_suite'],
    
    # Requirements
    python_requires='>=3.7',
    install_requires=[
        # No external dependencies - uses only Python standard library
    ],
    
    # Optional dependencies for development
    extras_require={
        'dev': [
            'pytest>=6.0',
            'black>=21.0',
            'flake8>=3.8',
            'mypy>=0.800'
        ],
        'test': [
            'pytest>=6.0',
            'pytest-cov>=2.10'
        ]
    },
    
    # Entry points for command-line usage
    entry_points={
        'console_scripts': [
            'json-parser=json_parser:main',
            'jsonparse=json_parser:main',
        ],
    },
    
    # Package data
    include_package_data=True,
    package_data={
        '': ['*.json', '*.md', '*.txt'],
    },
    
    # Classification
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing',
        'Topic :: Utilities',
    ],
    
    # Keywords for PyPI search
    keywords='json parser validator cli library',
    
    # Project URLs
    project_urls={
        'Documentation': 'https://github.com/username/json-parser#readme',
        'Source': 'https://github.com/username/json-parser',
        'Tracker': 'https://github.com/username/json-parser/issues',
    },
)