import logging
import os
import sys
import time
from pathlib import Path
from typing import Optional, TextIO

import click

from sodalite.core import dao, key
from sodalite.core.config import ConfigNotFound
from sodalite.core.entry import Entry
from sodalite.core.entryaccess import EntryAccess
from sodalite.core.entrywatcher import EntryWatcher
from sodalite.util import env, VERSION

logger = logging.getLogger(__name__)

_old_stdin: TextIO
_old_stdout: TextIO


def _io_to_tty() -> None:
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


def _io_to_std() -> None:
    global _old_stdin, _old_stdout
    sys.__stdin__ = sys.stdin = _old_stdin
    sys.__stdout__ = sys.stdout = _old_stdout


_CLICK_CONTEXT = dict(help_option_names=['-h', '--help'])

_entry_watcher: EntryWatcher


@click.command('sodalite', context_settings=_CLICK_CONTEXT)
@click.version_option(VERSION)
@click.argument('path', required=False, type=click.Path(exists=True, resolve_path=True))
@click.option('-u', '--update-access', help="Store access for given path in the database and quit")
def run(path: Optional[str], update_access: Optional[str]) -> None:
    """Opens the sodalite file navigator at given PATH"""
    if update_access:
        update(update_access)
    else:
        if not path:
            path = os.environ['PWD']
        path = path
        try:
            _io_to_tty()
            from sodalite.ui import graphics

            global _entry_watcher
            _entry_watcher = EntryWatcher()
            graphics.run(Path(path).absolute())

            if env.exit_cwd:
                sys.__stdout__ = sys.stdout = open('/dev/stdout', 'w')
                _io_to_std()
                print(str(env.exit_cwd))
            logger.debug("Shutting down")
        except KeyboardInterrupt:
            logger.debug('Received SIGINT - shutting down')
            exit(1)
        except ConfigNotFound as e:
            click.echo(e.msg, file=sys.stderr)
            exit(1)


def update(target: str) -> None:
    if target in ['.', '..']:
        # do nothing
        return
    target_path = Path(target)
    if not target_path.exists():
        logger.warning(f'Not updating target {target}: no such file or directory')
        exit(1)
    target_name = str(target_path)
    if target_name.startswith("/"):
        target_name = target_name[1:]
        cwd = Path("/")
    else:
        target_name = target_name
        cwd = Path.cwd()
    route = target_name.split("/")
    for segment in route:
        entry_path = cwd / segment
        if not dao.entry_exists(entry_path):
            old_entries = EntryAccess().retrieve_entry(cwd).children
            entry = Entry(entry_path)
            key.assign_keys({entry.path: entry}, {x.path: x for x in old_entries})
            dao.insert_entry(entry)
        now = int(time.time() * 1000)
        dao.insert_access(entry_path, now)
        logger.info(f"Update: access to '{entry_path}'")
        cwd = entry_path


def main():
    run(prog_name=env.PROGRAM_NAME)


if __name__ == "__main__":
    main()
