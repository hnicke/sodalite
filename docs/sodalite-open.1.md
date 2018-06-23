% SODALITE-OPEN(1) Version 1.0 | User Commands

NAME
====
sodalite-open - opens a file according to the XDG Mime Applications specification

SYNOPSIS
========

| **sodalite-open** *file*

DESCRIPTION
===========

Like *xdg-open*, sodalite-open opens a file in the user's preferred application.

Differences to *xdg-open* are:

- sodalite-open will open graphical applications in the background.
- if launching fails with the default application, sodalite-open will not retry launching the file with other applications

BUGS
====

Please report at https://github.com/hnicke/sodalite/issues.

AUTHOR
======

Heiko Nickerl <dev(at)heiko-nickerl.com>

SEE ALSO
========

**xdg-open(1)**
