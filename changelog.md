# Changelog

## Unreleased
##### Features
- Execute files with `e` (default hook)
- Add OSX support
- Redesign user interface: 
    - Action hooks are now displayed on bottom
    - Applicition now is dynamically rezisable
    
    
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
