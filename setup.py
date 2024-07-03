# setup.py
from setuptools import setup, find_packages

setup(
    name="tenka",
    version="0.1",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'tenka = tenka.__main__:main'
        ]
    },
    # other metadata
)