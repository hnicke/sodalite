import argparse
import logging
import os
import sys
import time

from core import dao, key
from core.entry import Entry
from util import environment

logger = logging.getLogger(__name__)


def _io_to_tty():
    global _old_stdin
    global _old_stdout
    _old_stdin = sys.stdin
    _old_stdout = sys.stdout
    sys.__stdin__ = sys.stdin = open('/dev/tty', 'r')
    sys.__stdout__ = sys.stdout = open('/dev/tty', 'w')
    logger.info('Starting sodalite')


def _io_to_std():
    sys.__stdin__ = sys.stdin = _old_stdin
    sys.__stdout__ = sys.stdout = _old_stdout


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--update-access", help='Persist an access to the current working directory and exit')
    # TODO adjust help
    args = parser.parse_args()
    if args.update_access:
        # make the update run as nicely as possible
        os.nice(20)
        if args.update_access.startswith("/"):
            args.update_access = args.update_access[1:]
            cwd = "/"
        else:
            cwd = os.getcwd()
        route = args.update_access.split("/")
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
        exit(0)

    try:
        _io_to_tty()
        from ui import app

        app.run()
        if environment.exit_cwd:
            sys.__stdout__ = sys.stdout = open('/dev/stdout', 'w')
            _io_to_std()
            print(environment.exit_cwd)
        logger.info("Shutting down")
    except KeyboardInterrupt as e:
        logger.info('Received SIGINT')
        exit(1)
