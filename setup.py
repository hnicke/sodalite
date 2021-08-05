# -*- coding: utf-8 -*-
from pathlib import Path

import setuptools

from sodalite import util
from sodalite.util import env

setuptools.setup(
    name=env.PROGRAM_NAME,
    version=util.VERSION,
    author="Heiko Nickerl",
    author_email="dev@hnicke.de",
    description="Keyboard-driven terminal file navigator and launcher",
    license_files=('copyright',),
    python_requires='>=3.9',
    url='https://github.com/hnicke/sodalite',
    packages=setuptools.find_packages(exclude=("tests",)),
    include_package_data=True,
    package_data={
        "": ["*"],
    },
    long_description=Path('README.md').read_text(),
    install_requires=[
        'PyYAML',
        'Pygments',
        'binaryornot',
        'blinker',
        'click',
        'pyperclip',
        'urwid',
        'watchdog',
    ],
    extras_require={
        'dev': [
            'mypy==0.910',
            'lxml',  # mypy report generation
            'pytest',
            'pytest-mock',
            'flake8',
            'flake8-sfs',
            'commitizen',  # enforce conventional commit messages
            'python-semantic-release',

        ]
    },
    entry_points={
        'console_scripts': ['sodalite = sodalite.__main__:main']
    },
)
