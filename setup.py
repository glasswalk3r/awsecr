#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = ['boto3==1.20.16', 'docker==5.0.3', 'terminaltables==3.1.0',
                'colorama==0.4.4', 'boto3-stubs[ecr,sts]']
setup_requirements = ['pytest-runner', ]
test_requirements = ['pytest>=3', ]

setup(
    author="Alceu Rodrigues de Freitas Junior",
    author_email='arfreitas@cpan.org',
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
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
    version='0.4.0',
    zip_safe=False,
)
