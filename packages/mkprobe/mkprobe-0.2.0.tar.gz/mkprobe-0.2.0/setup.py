#!/usr/bin/env python3

import setuptools
from mkprobe import info

setuptools.setup(
    name = 'mkprobe',
    version = info.VERSION,
    author = info.AUTHOR,
    author_email = info.CONTACT,
    description = info.SHORTDESC,
    long_description = open('README.md').read(),
    long_description_content_type = "text/markdown",
    url="https://github.com/bio2m/mkprobe",
    packages = setuptools.find_packages(),
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Natural Language :: English',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ],
    entry_points = {
        'console_scripts': [
            'mkprobe = mkprobe.main:main',
        ],
    },
    # ~ include_package_data = True,
    python_requires = ">=3.8",
    licence = "GPLv3"
)
