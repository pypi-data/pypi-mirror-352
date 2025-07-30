from setuptools import setup, find_packages
import os
setup(
    name='dlt_utils_lib',
    version=os.getenv('TAG_VERSION'),
    packages=find_packages(),
    install_requires=[
        'pyspark',
        'delta-spark'
    ],
    extras_require={
        'dev': [
            'pytest',
        ],
    },
)