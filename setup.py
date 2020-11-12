from os import path
from setuptools import setup, find_packages

setup(
    name='s3-backup',
    version='0.2.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            's3_backup = s3_backup.__main__:main'
        ]
    })
