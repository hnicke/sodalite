# Changelog

## Unreleased
##### Bugfix
- Fix rendering first line in file preview
##### Misc
- Improve file preview syntax highlighting

## v0.19.2: September 23, 2018
##### Misc
- Add untar hook for `.tar.gz` files to default config
- Redesign help screen
- Rename action 'toggle_dotfiles' to 'toggle_hidden_files'

## v0.19.1: September 21, 2018
##### Features
- Show help screen which displays the currently available actions and their associated keybindings.

## v0.18.3: September 21, 2018
##### Bugfixes
- Fixes scrolling in file preview

## v0.18.2: September 21, 2018
##### Bugfixes
- sodalite-open can now handle filenames with white spaces
## v0.18.1: August 27, 2018
##### Features
- Add shortcut to copy the current file content to clipboard (default: 'meta y')

## v0.17.2: July 16, 2018
##### Bugfixes
- Fixes cd-interception in zsh

## v0.17.1: July 16, 2018
##### Features
- Add mode indicator to easily see in which mode the app currently is
- Add operation mode: Yanking, pasting, deleting and renaming files is now possible
##### Bugfixes
- Fix crash when pressing `=` in file preview
##### Misc
- Change how to specify custom keybindings
- 'yank_to_clipboard' now belongs to mode 'global' (before: 'normal')
- Rename 'normal mode' to 'navigate mode'
- Rename 'edit mode' to 'operate mode'
- The actions for entering the different modes now belong to 'global' mode, i.e. they are accessible from everywhere

## v0.16.1: July 03, 2018
##### Features
- Add option to set up preferred file names via configuration file
- Improve shell integration: When exiting and current entry is a file, inserts the file name at the current cursor position in the command line
##### Bugfixes
- Fix cascading deletion of accesses whenever an entry is deleted from database 
- Fix scrolling

## v0.15.1: June 28, 2018
##### Bugfixes
- Fix custom keybindings for `normal.go_to_parent` and `normal.go_to_home`
- Fix the cd interception: Now only updates database if the actual `cd` was successful and the target was neither `.` nor `..`
- Fix the filepreview: Sometimes when the file content changed, the preview was not updated 
##### Misc
- Change default keybinding of `normal.go_to_home` to `;` and of `normal.go_to_root` to `,`

## v0.15.0: June 28, 2018
##### Features
- keys `0-9` can now be used as navigation keys

## v0.14.7: June 28, 2018
##### Bugfixes
- Sodalite-open now handles filenames which contain whitespaces

## v0.14.6: June 27, 2018
##### Bugfixes
- Fix shell integration for bash

## v0.14.5: June 27, 2018
##### Bugfixes
- Fix crash on startup when history file did not yet exist

## v0.14.4: June 26, 2018
##### Bugfixes
- Fix error in shell-integration when calling `cd` without path

## v0.14.3: June 26, 2018
##### Misc
- Enhance error handling in cd interception
##### Bugfixes
- Fix crash when starting sodalite and starting entry is not a directory
- Clear stale file previewing when viewing a non-previewable file

## v0.14.2: June 26, 2018
##### Misc
- Improve desktop entry
- Fix spelling in manpage

## v0.14.1: June 25, 2018
##### Bugfixes
- Fix crash when escaping input with '\' while filtering
- Update display correctly in case filter does not match anything

## v0.14.0: June 25, 2018
##### Features
- Filtering in file preview is now possible
##### Bugfixes
- Fix rendering of tabs in filepreview
- Sodalite-open now handles a broader array of desktop entries
##### Misc
- Do not supply compressed manpages

## v0.13.6: June 23, 2018
##### Bugfixes
- Manpage of sodalite is now parsable by lexgrog
##### Misc
- Add manpage for sodalite-open

## v0.13.5: June 23, 2018
##### Misc
- Instead of logging to /var/log/sodalite.log, now logging to the syslog socket /dev/log. When running systemd, you can now access the logs with `journalctl -ft sodalite`.

## v0.13.4: June 22,  2018
##### Misc
- Ditch install script in favour of a standardized Makefile

## v0.13.3: June 21, 2018
##### Bugfixes
- Instead of crashing, fail gracefully when yanking current path on systems without clipboard
- Fix handling of entries which contain special characters

## v0.13.2: June 20, 2018
##### Features
- Install documentation to general doc directory
##### Bugfixes
- Explicitly specify v3.6 as python version

## v0.13.1: June 20, 2018
##### Bugfixes
- Install compressed manpage
 
## v0.13.0: June 20, 2018
##### Features
- Add option to turn off cd interception
- Keybindings are now customizable
##### Bugfixes
- Fix mimetype launcher
- Fix outdated manpages 

## v0.12.0: June 19, 2018
##### Features
- Add man page
- A key gets automatically reassigned to a newer entry if the corresponding old entry is not used
##### Bugfixes
- Fix resolving of relative symlinks
- Child processes spawned with sodalite-open can now live further even if their parent process (sodalite and it's containing shell) stopped
- Fix mimelauncher crash when open file with whitespace in its name
- Fix that visiting big directories took forever
- Fix auto-assignment of keys for hidden entries
- Fix scrolling in assign mode

## v0.11.0: June 10, 2018
##### Features
- Use the concept of frecency instead of frequency for sorting entries. This results in a much better, more dynamic sorting strategy
- Enhanced shell-integration monitors shell navigation with `cd` commands. Collected data affects the frecency score of the related entries

## v0.10: June 06, 2018
##### Features
- Use key `0` to navigate to root directory
- Navigation history is remembered between sessions
##### Bugfixes
- Fix file launcher in graphics mode
- Fix broken assign mode

## v0.9.2: June 05: 2018
##### Bugfixes
- Fix shell integration
- Fix application freeze when returning from hook

## v0.9.1: June 05, 2018
##### Features
- Toggle visibility of dotfiles with `M-h`
##### Bugfixes
- Prevent race conditions while drawing to screen
- Make sodalite-open script (xdg-open wrapper) more robust
- Fix opening files when running headless
- Enhance shell integration when running headless

## v0.9: June 02, 2018
##### Features
- Add filepreview with syntax highlighting
- In default configuration, Replace launcher hooks with one generic launcher hook which uses mimetypes
- Automatically reflect external modifications of current entry
##### Bugfixes
- When batch-assigning new keys, non-hidden entries take precedence over hidden files again
- Entries without keys do not get displayed before entries with keys
- Fix crash when using `0-9` as hook key
- Disable control flow keys in sodalite. This means that keys like `ctrl-s` or `ctrl-z` do not lock the screen or pause the application and can therefore be used as hook keys
- Fix resizing after returning from hook
- Fix detection of whether a symlink is executable or not
##### Misc
- Exchange ui library 'npyscreen' with 'urwid'. This enhances the user experience by increasing the startup performance and fixing screen flickering.


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
