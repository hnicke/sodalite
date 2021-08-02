from pathlib import Path

import setuptools

from sodalite.util import env, VERSION

setuptools.setup(
    name=env.PROGRAM_NAME,
    version=VERSION,
    author="Heiko Nickerl",
    author_email="dev@hnicke.de",
    description='Keyboard-driven terminal file navigator and launcher',
    license_files=('copyright',),
    python_requires='>3.9.0',
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
        'blinker'
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
        ]
    }
)
