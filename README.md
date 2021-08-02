[![Check Action Status](https://github.com/hnicke/sodalite/workflows/Check/badge.svg)](https://github.com/hnicke/sodalite/actions/workflows/check.yaml)
![badge](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/hnicke/dfd1ab3f3a19522e0d2b0c94c409ba78/raw/sodalite-type-coverage.json)

# Sodalite: Exploration at the speed of thought

## Yet another file explorer
Have you ever played [crawl](https://crawl.develz.org/)?
That's a terminal based roguelike dungeon crawler.  
What makes it stand out is it's extremely efficient menu navigation philsophy. 

![dcss inventar management](docs/crawl.png)

*Dungeon Crawl Stone Soup: For selecting an item, press it's automatically assigned key.*

After a while, the keys burn into one's muscle memory - using the game's interface feels extremely efficient.  
`sodalite` brings the same feature to your file system: Navigation at the speed of thought.

## Navigate the file system
When opening `sodalite`, you will see the listing of the current directory.   
Pressing one of the keys displayed in front of the entries will navigate there.

![Sodalite](docs/sodalite.png)

Assign the most intuitive and/or reachable keys to your most frequently used entries, and stick with this assignment. 
Once setup, and muscle memory kicks in, all directories will be reachable in a blink of an eye!

## Installation

#### Linux

##### Arch Linux
AUR package [sodalite](https://aur.archlinux.org/packages/sodalite/) (stable release):
> `yaourt -S sodalite`

AUR package [sodalite-git](https://aur.archlinux.org/packages/sodalite-git/) (master branch):
> `yaourt -S sodalite-git`



#### OSX
1. Install [brew](https://brew.sh/):
> `/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"`
2. Install dependencies:
    1. python3: `brew install python3`
    2. other: `pip3 install -r requirements.txt`
3. run `sudo make install`

#### Manual Installation
In order to manually install `sodalite`, clone this repository, `cd` to the project root and execute:
```bash
sudo make prefix=/usr sysconfdir=/etc install
```
Replace the values for `prefix` and `sysconfdir` with the appropriate directories for your OS.

The project adheres to the [GNU Makefile Conventions](https://www.gnu.org/prep/standards/html_node/Makefile-Conventions.html#Makefile-Conventions). 
In case it doesn't it's considered a bug - please file a bug report.

> **Necessary dependencies**:  
> - [python3](https://www.python.org/downloads/release/python-364/)  (>=3.6)
> - [urwid](http://urwid.org)
> - [click](https://click.palletsprojects.com/en/7.x/)
> - [pygments](http://pygments.org)
> - [binaryornot](https://github.com/audreyr/binaryornot)
> - [PyYAML](https://github.com/yaml/pyyaml)
> - [pyperclip](https://github.com/asweigart/pyperclip)
> - [watchdog](https://github.com/gorakhargosh/watchdog)

## Getting started
Check out the [manpage](docs/sodalite.1.md) for detailed usage information.

## FAQ
##### The default 'open' hook doesn't work / launches weird programs :(
Most probably it is not sodalite's fault, but your mime default application list isn't configured correctly.
You could try this:
```bash
xdg-mime default <desktop> $(xdg-mime query filetype <file>)
```
Replace `<file>` with the file you're trying to open and `<desktop>` with name of the desktop entry file of your new default app. If you're not sure what's the name of the desktop entry of a specific app, look for it in `/usr/share/applications`.

Alternatively you can edit the mime app list manually: `$HOME/.config/mimeapps.list`

Or learn more about [mime](https://wiki.archlinux.org/index.php/XDG_MIME_Applications#mimeapps.list).


## Changelog
Don't miss out on what has changed: Read the [changelog](CHANGELOG.md).

## Contributing
Do you want to contribute to the project? Check out the [developer guide](docs/developer_guide.md).

## License
See [copyyright](copyright).
