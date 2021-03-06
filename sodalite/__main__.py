import logging
import os
import sys
import time
from pathlib import Path
from typing import Optional

import click

from sodalite.core import dao, key
from sodalite.core.entry import Entry
from sodalite.util import environment

PROGRAM_NAME = 'sodalite'
VERSION = f'0.19.2'

logger = logging.getLogger(__name__)


def _io_to_tty():
    global _old_stdin
    global _old_stdout
    _old_stdin = sys.stdin
    _old_stdout = sys.stdout
    try:
        sys.__stdin__ = sys.stdin = open('/dev/tty', 'r')
        sys.__stdout__ = sys.stdout = open('/dev/tty', 'w')
    except OSError:
        # when debugging the app, /dev/tty is not available
        pass


def _io_to_std():
    sys.__stdin__ = sys.stdin = _old_stdin
    sys.__stdout__ = sys.stdout = _old_stdout


_CLICK_CONTEXT = dict(help_option_names=['-h', '--help'])


@click.command('sodalite', context_settings=_CLICK_CONTEXT)
@click.version_option(VERSION)
@click.argument('path', required=False, type=click.Path(exists=True), default=Path.cwd())
@click.option('-u', '--update-access', type=click.Path(exists=True),
              help="Store access for given path in the database and quit")
def run(path: Path, update_access: Optional[Path]):
    """Opens the sodalite file navigator at given PATH"""
    if update_access:
        update(update_access)
    else:
        try:
            _io_to_tty()
            from sodalite.ui import graphics

            graphics.run(path)

            if environment.exit_cwd:
                sys.__stdout__ = sys.stdout = open('/dev/stdout', 'w')
                _io_to_std()
                print(environment.exit_cwd)
            logger.info("Shutting down")
        except KeyboardInterrupt as e:
            logger.info('Received SIGINT - shutting down')
            exit(1)


def update(target: Path):
    # make this update run without bothering the user
    os.nice(20)
    target_name = str(target)
    if target_name.startswith("/"):
        target_name = target_name[1:]
        cwd = "/"
    else:
        target_name = target_name
        cwd = str(Path.cwd())
    route = target_name.split("/")
    for segment in route:
        entry_path = os.path.join(cwd, segment)
        if not dao.entry_exists(entry_path):
            old_entries = dao.get_children(cwd)
            entry = Entry(entry_path)
            key.assign_keys({entry.path: entry}, old_entries)
            dao.insert_entry(entry)
        now = int(time.time() * 1000)
        dao.insert_access(entry_path, now)
        logger.info(f"Update: access to '{entry_path}'")
        cwd = entry_path


if __name__ == "__main__":
    run(prog_name=PROGRAM_NAME)
