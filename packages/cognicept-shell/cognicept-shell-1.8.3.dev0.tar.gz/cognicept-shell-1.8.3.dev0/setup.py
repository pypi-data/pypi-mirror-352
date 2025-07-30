#!/usr/bin/env python
import re
import ast

from setuptools import setup, find_packages


requires = ['python-dotenv==0.14.0',
            'urllib3>=1.25.4,<1.27 ; python_version < "3.10"',
            'urllib3>=2.0.7,!=2.2.0,<3 ; python_version >= "3.10"',
            'boto3>=1.14.0; python_version < "3.10"',
            'boto3>=1.30.0; python_version >= "3.10"',
            'docker==5.0.3 ; python_version < "3.10"',
            'docker==7.0.0 ; python_version >= "3.10"',
            'PyCryptodome >=3.9.8',
            'argcomplete>=1.12.3',
            'tabulate',
            'ping3',
            'PyJWT==1.7.1',
            'websocket-client==0.59.0',
            'paramiko>=2.4.2',
            'psutil',
            'ruamel.yaml',
            'pyaml']

with open("README.md") as readme_file:
    README = readme_file.read()

setup(
    name="cognicept-shell",
    version="1.8.3.dev0",
    description="Shell utility to configure Cognicept tools.",
    long_description_content_type="text/markdown",
    long_description=README,
    author="Jakub Tomasek",
    url="https://kabam.ai",
    packages=find_packages(),
    install_requires=requires,
    license="Apache License 2.0",
    entry_points={
        "console_scripts": ["cognicept=cogniceptshell.interface:main"],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Natural Language :: English",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.10",
    ],
)
