[![Check Action Status](https://github.com/hnicke/sodalite/workflows/Check/badge.svg)](https://github.com/hnicke/sodalite/actions/workflows/check.yaml)
![badge](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/hnicke/dfd1ab3f3a19522e0d2b0c94c409ba78/raw/sodalite-type-coverage.json)

# sodalite: Exploration at the speed of thought

## Yet another file explorer
Have you ever played [crawl](https://crawl.develz.org/)?
That's a terminal based roguelike dungeon crawler.  
What makes it stand out is it's extremely efficient menu navigation philsophy. 

![dcss inventar management](https://raw.githubusercontent.com/hnicke/sodalite/master/docs/images/crawl.png)

*Dungeon Crawl Stone Soup: For selecting an item, press it's automatically assigned key.*

After a while, the keys burn into one's muscle memory - using the game's interface feels extremely efficient.  
`sodalite` brings the same feature to your file system: Navigation at the speed of thought.

## Navigate the file system
When opening `sodalite`, you will see the listing of the current directory.   
Pressing one of the keys displayed in front of the entries will navigate there.

![directory pane](https://raw.githubusercontent.com/hnicke/sodalite/master/docs/images/sodalite-directory-pane.png)
![file preview](https://raw.githubusercontent.com/hnicke/sodalite/master/docs/images/sodalite-file-preview.png)

Assign the most intuitive and/or reachable keys to your most frequently used entries, and stick with this assignment. 
Once setup, and muscle memory kicks in, all directories will be reachable in a blink of an eye!

## Installation

#### Linux

##### Debian-based Distros (e.g., Ubuntu)
 ```bash
# add apt key and repository http://debian.hnicke.de/repo/
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 5B08767916BCFCE7
echo "deb [arch=amd64] http://debian.hnicke.de/repo/ unstable main" | sudo tee /etc/apt/sources.list.d/sodalite.list
sudo apt-get update

# install
sudo apt install sodalite
```

##### Arch Linux
AUR package [sodalite](https://aur.archlinux.org/packages/sodalite/):
```bash
yay -S sodalite
```


## Getting started
Check out the [manpage](https://github.com/hnicke/sodalite/blob/master/docs/sodalite.1.md) for detailed usage information.

## FAQ
##### The default 'open' hook doesn't work / launches weird programs :(
Most probably it is not sodalite's fault, but your mime default application list isn't configured correctly.
Run the following command to find the associated application for given file:
```bash
xdg-mime query default $(xdg-mime query filetype <file>)
```
In order to change the default application for a files mime type, run:
```bash
xdg-mime default <desktop> $(xdg-mime query filetype <file>)
```
Replace `<file>` with the file you're trying to open and `<desktop>` with name of the desktop entry file of your new default app. If you're not sure what's the name of the desktop entry of a specific app, look for it in `/usr/share/applications`.

Alternatively you can edit the mime app list manually: `$HOME/.config/mimeapps.list`

Or learn more about [mime](https://wiki.archlinux.org/index.php/XDG_MIME_Applications#mimeapps.list).


## Changelog
Don't miss out on what has changed: Read the [changelog](https://github.com/hnicke/sodalite/blob/master/CHANGELOG.md).

## Contributing
Do you want to contribute to the project? Check out the [developer guide](https://github.com/hnicke/sodalite/blob/master/docs/developer_guide.md).

## License
See [copyyright](https://github.com/hnicke/sodalite/blob/master/copyright).
