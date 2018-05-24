"""Packaging settings."""
from setuptools import setup
setup(name='expostack',
    version = '1.0', 
    packages=['expostack'],
    install_requires = ['docopt'],
    entry_points = {
        'console_scripts': [
            'expostack = expostack.cli:main',
        ],
    }
)
