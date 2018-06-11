% SODALITE(1) Version 1.0 | User Commands

NAME
====

**sodalite** — terminal file navigator and launcher 

SYNOPSIS
========

| **sodalite** \[**-h**|**-v**|\[**-u** *target*] *path*]

DESCRIPTION
===========

Sodalite is a keyboard-driven terminal file navigator and launcher. It's designed to be the missing glue for those who use the shell as their daily driver and seek more speed and ease.

In a nutshell, sodalite assigns a key to each entry. Pressing a key navigates to the corresponding entry. 
The assignments are permanent but can be changed to your liking.

Next to fast navigation, sodalite brings file preview with syntax highlighting and a pluggable hook system.

Launch sodalite: sodalite \[*path*]  
If *path* is supplied, sodalite will start in given path.



Shell integration
-----------------

It's recommended to integrate sodalite into the shell. The integration does the following:

- set up a keybinding to launch sodalite wich enables convenient navigation
- collect data about your navigation profile (e.g., by intercepting `cd` calls) in order to customize your view on the data

**bash / zsh**

Add following line to your `.bashrc` / `.zshrc`:

```bash
source /usr/share/sodalite/shell-integration.sh
```
The script will set up a keybinding which launches `sodalite`.

* Emacs keymap:     `Control + f`
* Vim keymap:       `f` in command (aka normal) mode

**fish**

Add following to your fish.config:
```bash
source /usr/share/sodalite/shell-integration.fish

function fish_user_key_bindings
    bind \cf sodalite-widget
end
```
If the function `fish_user_key_bindings` already exists, only add its content to the function.


Options
-------

-h, -\-help

:   Prints brief usage information.

-v, -\-version

:   Prints the current version number.

-u, -\-update-access *target*

:   Simulates navigation to *target* (a relative or absolute path to a file or directory) without launching the UI. However, the database is updated regularly. Afterwards, quits. For example:

        sodalite -u .local/share/sodalite $HOME
        
    will store an access for each $HOME/.local, $HOME/.local/share and $HOME/.local/share/sodalite. 
    
    The purpose of this mode is to affect the entry ranking in a programmatical way. E.g., it is used in the shell integration where calls to *cd* are intercepted in order to gather information about the user's navigational preferences.

FILES
=====

*/etc/sodalite.yml*

:   Global default configuration file.

*$XDG_CONFIG_HOME/sodalite/sodalite.yml*

:   Per-user default configuration file. If `$XDG_CONFIG_HOME` is not set, uses `$HOME/.config`.

*$XDG_DATA_HOME/sodalite/db.sqlite*

:   Database of sodalite. If `$XDG_DATA_HOME` is not set, uses `$HOME/.local/share`.

*/var/log/sodalite.log*

:   The log.

<!-- 
ENVIRONMENT
===========

**DEFAULT_HELLO_DEDICATION**

:   The default dedication if none is given. Has the highest precedence
    if a dedication is not supplied on the command line.
-->
BUGS
====

Please report at https://github.com/hnicke/sodalite/issues.

AUTHOR
======

Heiko Nickerl <dev@heiko-nickerl.com>

<!--
SEE ALSO
========

**hi(1)**, **hello(3)**, **hello.conf(5)**<Paste>
-->
