#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=7.0', 'requests>=2.0', 'python-dateutil>=2.8']

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="Tim G",
    author_email='timoguic@gmail.com',
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Python package to facilitate interaction with OC website.",
    entry_points={
        'console_scripts': [
            'oc_assistant=oc_assistant.cli:main',
        ],
    },
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='oc_assistant',
    name='oc_assistant',
    packages=find_packages(include=['oc_assistant', 'oc_assistant.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/timoguic/oc_assistant',
    version='0.1.0',
    zip_safe=False,
)
