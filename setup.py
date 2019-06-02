# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'readme.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='lcls',
    version="1.0.3",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["sty", "ruamel.yaml"],
    entry_points = {
        'console_scripts': ['lcls=lcls:main'],
    },
    long_description=long_description,
    long_description_content_type='text/markdown',
    description="lc is ls but with colors and icons.",
    author='Pouya Eghbali',
    author_email='pouya.eghbali@yandex.com',
    url='https://github.com/pouya-eghbali/lc',
)