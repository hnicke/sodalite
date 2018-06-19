# Developer Guide

This document is aimed towards developers who want to contribute to sodalite.

#### Building the man page
Please add the supplied pre-commit hook:
```bash
bin/hooks/symlink-hooks
```
This will translate the markdown man page to the groff manpage, and stage the resulting file everytime you commit.

#### Code formatting
The project is auto-formatted with PyCharm (default settings).

### Release Checklist
##### before
- update changelog
- update VERSION variable in main.py
- new Dependencies? Update readme!

##### after
- contact dev(at)heiko-nickerl.com and ask to update the aur packages
