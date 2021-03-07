from pathlib import Path

import setuptools
from sodalite.util import env

setuptools.setup(
    name=env.PROGRAM_NAME,
    version=env.VERSION,
    author="Heiko Nickerl",
    author_email="dev@hnicke.de",
    description='Keyboard-driven terminal file navigator and launcher',
    license_files=('copyright',),
    url="https://github.com/hnicke/sodalite",
    packages=setuptools.find_packages(),
    long_description=Path('README.md').read_text(),
    install_requires=[
        'binaryornot',
        'click',
        'pygments',
        'pyperclip',
        'pyyaml',
        'urwid',
        'watchdog',
    ],
    extras_require={
        'dev': [
            'mypy',
            'pytest',
            'flake8',
        ]
    }
)
