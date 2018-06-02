# Changelog

## Unreleased
##### Features
- Add filepreview with syntax highlighting
- In default configuration, Replace launcher hooks with one generic launcher hook which uses mimetypes
##### Bugfixes
- When batch-assigning new keys, non-hidden entries take precedence over hidden files again
- Entries without keys do not get displayed before entries with keys
- Fix crash when using `0-9` as hook key
- Disable control flow keys in sodalite. This means that keys like `ctrl-s` or `ctrl-z` do not lock the screen or pause the application and can therefore be used as hook keys
- Fix resizing after returning from hook
##### Misc
- Exchange ui library 'npyscreen' with 'urwid'. This enhances the user experience by increasing the startup performance and and fixing screen flickering.


## v0.8: April 16, 2018
##### Features
- Execute executables with `e` (default action hook)
- Add OSX support
- Redesign user interface: 
    - Entries are displayed in color (which depends on type and frequency)
    - Action hooks are now displayed at the bottom
    - Applicition now is dynamically resizable
- Yank path of current entry with `C-y`
##### Fixes
- When encountering problems (e.g., missing file or permission), notifications get emitted (and app does not crash)
    
    
## v0.7.1: March 14, 2018
Hotfix release.
####  Bugfixes
- Fix crash on startup in case certain directories were not existent #42
- Recursively delete obsolete database entries #48


## v0.7.0: February 27, 2018
Mostly internal refactoring.
##### Features
- Introduce 'go to previous' (`C-h`) and 'go to next' (`C-l`) commands
- Rename configuration file from `sodalite.conf` to `sodalite.yml`
- Action hooks can be made invisible when omitting the `label` property
- Hook action definitions now use `$entry` instead of `#f` to refer to current entry
- Add this changelog
- Add detailed [usage guide](docs/usage.md)
##### Bugfixes
- Fix 'go to parent' command (#15)

## v0.6.0: February 20, 2018
Initial release.
