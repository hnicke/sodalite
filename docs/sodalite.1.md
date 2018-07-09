% SODALITE(1) Version 1.0 | User Commands

NAME
====
sodalite - terminal file navigator and launcher 

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

- set up a keybinding to launch sodalite which enables convenient navigation
- collect data about your navigation profile (e.g., by intercepting `cd` calls) in order to customize your view on the data. You can disable this by setting the variable SODALITE_CD_INTERCEPTION to *false* before sourcing the integration script.

**bash / zsh**

Add following line to your `.bashrc` / `.zshrc`:

```bash
source /usr/share/sodalite/shell-integration.sh
```
The script will set up a keybinding which launches `sodalite`.

* Emacs keymap:     `ctrl f`
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

Modi
----

Like in vim, there are different modi. In each mode, a different set of actions is available.

- `NAVIGATE`: navigate the file system
- `ASSIGN`: assign keys to files
- `OPERATE`: modify the file system

Global actions
--------------
Following general actions can be triggered everywhere in `sodalite`:

**exit (`ENTER`)**

:   Exit `sodalite`. Prints the current entry to `stdout`.

    In case `sodalite` was invoked with the provided shell integration key-bindings, will `cd` into current directory. If the current entry is not a directory but a file, will `cd` into the parent directory.

**abort (`ctrl c`)**

:   Exit `sodalite` without printing current directory to `stdout`.

**navigate_mode (`esc`)**

:   Enter navigate mode.

**assign_mode (`=`)**

:   Enter assign mode.

**operate_mode (` ` [space])**

:   Enter operate mode.

**filter (`/`)**

:   Focuses the filter bar on the bottom. Use regular expressions to filter displayed entries. The filtering is case-insensitive. Press `enter` to submit or `esc` to dismiss the filter.

**toggle_dotfiles  (`meta h`)**

:   Toggles visiblity of dotfiles.

**scroll_page_down (`ctrl f`)**

:   Scroll down one page.

**scroll_page_up (`ctrl b`)**

:   Scroll up one page.

**scroll_half_page_down (`ctrl d`)**

:   Scroll down half a page.

**scroll_half_page_up (`ctrl u`)**

:   Scroll up half a page.

`NAVIGATE` mode
-----------
`sodalite` automatically assigns keys to entries in order to enable quick navigation. For navigating to a specific entry, simply press its assigned key.
Valid values for keys are all letters of the alphabet (lower and upper case), so there are 52 different keys. For every directory, each key is unique. If there are more than 52 entries in a directory, some entries will end up having no key assigned to them. However, you can change this within the `ASSIGN` mode.

**go_to (`[a-zA-Z0-9]`)**

:   Navigate to the entry matching pressed key. Note: This function is not reassinable to another keybinding.

**go_to_home (`;`)**

:   Navigate to the `$HOME` directory.

**go_to_root (`,`)**

:   Navigate to the root directory.

**go_to_parent (`.`)**

:   Navigate to the parent directory. Does nothing if parent directory does not exist.

**go_to_previous (`ctrl h`)**

:   Navigate back in history one step. Does nothing if history does not contain a previous entry. Note: 'ctrl h' equals backslash in terminal emulators.

**go_to_next (`ctrl l`)**

:   Navigate forward in history. Does nothing if history does not contain a next entry.

**yank_current_path (`ctrl y`)**

:   Copy current entry's path to the system's clipboard.

`ASSIGN` mode
-----------
The `ASSIGN` mode is needed to assign a specific key to an entry. While in assign mode, the frame is displayed in green.
Assigning entries is accomplished within these steps:

1. Enter assign mode
2. Press a key associated with an entry or select an entry manually
3. Press the new key

If the newly assigned key is already assigned to another entry in the current directory, keys get swapped.

**select_next (`ctrl n`)**

:   Select next entry.

**select_previous (`ctrl p`)**

:   Select previous entry.

OPERATE mode
------------
The `OPERATE` mode allows for convenient file manipulation. While in operate mode, the frame is displayed in red.

**yank (`y`)**

: Yanks (i.e., copies) the entry associated with the next issued keypress to sodalite's buffer.

**paste (`p`)**

: Pastes the content of sodalite's buffer into the current directory.

**delete (`d`)**

: Moves the entry associated with the next issued keypress to sodalite's buffer.

**rename (`r`)**

: Renames specified entry.

Options
-------

**-h, -\-help**

:   Prints brief usage information.

**-v, -\-version**

:   Prints the current version number.

**-u, -\-update-access *target***

:   Simulates navigation to *target* (a relative or absolute path to a file or directory) without launching the UI. However, the database is updated regularly. Afterwards, quits. For example:

        sodalite -u .local/share/sodalite $HOME
        
    will store an access for each $HOME/.local, $HOME/.local/share and $HOME/.local/share/sodalite. 
    
    The purpose of this mode is to affect the entry ranking in a programmatical way. E.g., it is used in the shell integration where calls to *cd* are intercepted in order to gather information about the user's navigational preferences.


Configuration
=============
Upon startup, `sodalite` looks in following places for its configuration:

1. `$XDG_CONFIG_HOME/sodalite/sodalite.yml` (user specific configuration).
    If `$XDG_CONFIG_HOME` is not set, falls back to `$HOME/.config/sodalite/sodalite.yml`
2. `/etc/sodalite.yml` (system-wide configuration)

The configuration is written in [YAML](https://learnxinyminutes.com/docs/yaml/).

Example configuration
---------------------
```yml
keymap:
  filter: '/'
hooks:
  general:
  dir:
  plain_text:
    "e":
      action: './"$entry"'
      label: "execute"
    "o":
      action: 'vim "$entry"'
      label: "open with vim"
  custom:
    image:
      extensions: [png, jpg, bmp]
      hooks:
        "o":
          action: 'feh "$entry"'
          label: "open with feh"
``` 

**Customizing the default keymap**

```yaml
keymap:
  <built-in>: <keybinding>
```
If *built-in* matches the name of a built-in action, given *keybinding* is bound to this action (instead of its default binding).

**built-in**
:   (String, required) The name of a built-in function (e.g., `go_to_home`).
    
**keybinding**:
:   (String, required) The keybinding which is used to trigger the action. Use `ctrl a` and `meta a` to define the keys `Control a` and `Meta a`. Other special keys: `esc`, `enter`, `f1`

    
Action hooks
------------

It is possible to setup keybindings to trigger custom actions.
Note that keybindings defined in the configuration file will take precedence over the default keymap.

**Extended notation:**
```yaml
<keybinding>:
  action: <action>
  label: <label>
```
**Short notation:**
```yaml
<keybinding>: <action>
```

**action**

: (String, required) The action which is triggered by given keybinding. *action* is interpreted as a shell command and executed within a subshell. Use the variable `$entry` to reference the current entry. If given string ends with `#q`, `sodalite` will exit after command execution.
 
**label**

: (String, optional) Is used to represent the hook in the UI. Should be short and concise. If omitted, the hook will not be displayed in the UI.
 
**keybinding**

: (String, required) The keybinding which is used to trigger the action. Use `ctrl a` and `meta a` to define the keys `Control a` and `Meta a`. Other special keys: `esc`, `enter`, `f1`


The **hooks** declaration works like this:
```yaml
hooks:
  dir:
    <hook>
    ...
  file:
    <hook>
    ...
  plain_text:
    <hook>
    ...
  executable:
    <hook>
    ...
  custom:
    <name>:
      extensions: [<extension>, ...]
      hooks:
        <hook>
        ...
      ...
            
```

**dir**

: (optional) Declared hooks within this map are available whenever the current entry is a directory.

**file**

: (optional) Declared hooks within this map are available whenever the current entry is a file.

**plain_text**

: (optional) Declared hooks within this map are available whenever the current entry is a plain text file.

**executable**

: (optional) Declared hooks within this map are available whenever the current entry is executable.

**custom**

: (optional) Declare one or more custom hooks and attach them to one or multiple extensions, and repeat this if you want. This makes the hooks available whenever the current entry has one of its attached extension.



FILES
=====

*$XDG_CONFIG_HOME/sodalite/sodalite.conf*

:   Per-user default configuration file. If `$XDG_CONFIG_HOME` is not set, uses `$HOME/.config` instead. If file does not exist, fall back to global config file.

*/etc/sodalite.conf*

:   Global default configuration file. If file does not exists, fall back to example config file.

*/usr/share/sodalite/sodalite.conf*

:   Example config file.

*$XDG_DATA_HOME/sodalite/db.sqlite*

:   Database of sodalite. If `$XDG_DATA_HOME` is not set, uses `$HOME/.local/share`.

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

Heiko Nickerl <dev(at)heiko-nickerl.com>

<!--
SEE ALSO
========

**hi(1)**, **hello(3)**, **hello.conf(5)**
-->
