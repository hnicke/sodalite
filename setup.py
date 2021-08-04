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
    packages=setuptools.find_packages(),
    long_description=Path('README.md').read_text(),
    install_requires=[
        'PyYAML>=5.4.1,<6.0.0',
        'Pygments>=2.9.0,<3.0.0',
        'binaryornot>=0.4.4,<0.5.0',
        'blinker>=1.4,<2.0',
        'click>=8.0.1,<9.0.0',
        'pyperclip>=1.8.2,<2.0.0',
        'urwid>=2.1.2,<3.0.0',
        'watchdog>=2.1.3,<3.0.0'
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
