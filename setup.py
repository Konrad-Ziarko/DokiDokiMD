#!/usr/bin/env python3
from os import walk
from os.path import dirname, abspath, join

from setuptools import setup

name = 'dokidokimd'

DIR = join(dirname(abspath(__file__)), name)
VERSION = '0.1.0'

with open(join(dirname(abspath(__file__)), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


def package_files(directory=DIR):
    paths = []
    for (path, directories, file_names) in walk(directory):
        for filename in file_names:
            paths.append(join('..', path, filename))
    return paths


setup(
    name=name,
    version=VERSION,
    description='Python manga downloader and PDF creator.',
    long_description=long_description,
    license='BSD 3-Clause',
    keywords='tui urwid python-manga-downloader python python3 manga manga-downloader',
    author='Konrad Ziarko',
    author_email='konrad.ziarko@protonmail.ch',
    url='https://github.com/Konrad-Ziarko/PyPractice',
    download_url='https://github.com/Konrad-Ziarko/DokiDokiMD/archive/v{0}.zip'.format(VERSION),
    packages=['dokidokimd'],
    package_data={'': package_files()},
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: BSD License',
    ],
    test_suite='tests',
    python_requires='>=3',
)