#!/usr/bin/env python

"""The setup script."""

from typing import List
from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements: List[str] = []

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.read().split()

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest>=3', ]

setup(
    author="Alceu Rodrigues de Freitas Junior",
    author_email='glasswalk3r@yahoo.com.br',
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
    ],
    description="Easy interaction with AWS ECR to upload Docker images",
    entry_points={
        'console_scripts': [
            'awsecr=awsecr.cli:main',
        ],
    },
    install_requires=requirements,
    long_description=readme,
    include_package_data=True,
    keywords='awsecr',
    name='awsecr',
    packages=find_packages(include=['awsecr', 'awsecr.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/glasswalk3r/awsecr',
    version='0.1.0',
    zip_safe=False,
)
