#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = ['boto3==1.35.24', 'docker==7.1.0', 'terminaltables==3.1.10',
                'colorama==0.4.6', 'boto3-stubs[ecr,sts]==1.35.25']
setup_requirements = ['pytest-runner', ]
test_requirements = ['pytest>=3', ]

setup(
    author="Alceu Rodrigues de Freitas Junior",
    author_email='glasswalk3r@yahoo.com.br',
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    description="Easy interaction with AWS ECR from a CLI",
    entry_points={
        'console_scripts': [
            'awsecr=awsecr.cli:main',
        ],
    },
    install_requires=requirements,
    long_description=readme,
    long_description_content_type='text/markdown',
    include_package_data=True,
    keywords='awsecr',
    name='awsecr',
    packages=find_packages(include=['awsecr', 'awsecr.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/glasswalk3r/awsecr',
    version='0.5.4',
    zip_safe=False,
)
