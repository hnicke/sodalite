import argparse
import logging
import os
import sys
import time

from core import dao, key
from core.entry import Entry
from util import environment

VERSION = 'sodalite v0.19.1'

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


def parse_arguments():
    parser = argparse.ArgumentParser(prog='sodalite', description='A terminal file navigator and launcher')
    parser.add_argument("path", nargs="?", help="the path to the current entry at startup. Defaults to $PWD")
    parser.add_argument("-v", "--version", action='store_true', help="print the version and exist")
    parser.add_argument("-u", "--update-access", metavar='target',
                        help='store access to given relative or absolute target in database and exit')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    if args.version:
        print(VERSION)
        exit(0)
    if args.path:
        if not os.path.exists(args.path):
            print(f"'{args.path}' does not exist, aborting", file=sys.stderr)
            exit(1)
    if not args.path:
        args.path = os.getcwd()
    args.path = os.path.abspath(args.path)

    if args.update_access:
        # make the update run as nicely as possible
        os.nice(20)
        if args.update_access.startswith("/"):
            args.update_access = args.update_access[1:]
            cwd = "/"
        else:
            cwd = args.path
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
        from ui import graphics

        graphics.run(args.path)

        if environment.exit_cwd:
            sys.__stdout__ = sys.stdout = open('/dev/stdout', 'w')
            _io_to_std()
            print(environment.exit_cwd)
        logger.info("Shutting down")
    except KeyboardInterrupt as e:
        logger.info('Received SIGINT - shutting down')
        exit(1)
