from pathlib import Path

import setuptools

setuptools.setup(
    name="sodalite",
    version="0.19.4",
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
