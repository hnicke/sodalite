# Sodalite: a quick file navigator

## Installation
* Arch Linux: AUR package [sodalite-git](https://aur.archlinux.org/packages/sodalite-git/)  

In order to manually install `sodalite`, clone this repository, `cd` to the project root and execute:
```bash
sudo ./install
````
For customization of the destination directories, consult [INSTALL](../INSTALL).
> **Dependencies**:  
> - [npyscreen](https://github.com/npcole/npyscreen)
> - [binaryornot](https://github.com/audreyr/binaryornot)


## Configuration
`sodalite` needs to get integrated into your favourite shell (supported: `bash`, `zsh`).  
Simply add following line to your `.bashrc` / `.zshrc`:

```bash
source /usr/share/sodalite/shell-integration.sh
```
The script will set up a keybinding which launches `sodalite`.
The keybinding depends on the active keymap of your shell. Therefore make sure to source the script after you set up your shell keymap.
* Emacs keymap:     `Control + f`
* Vim keymap:       `f` in command (aka normal) mode

*If your favourite shell is not supported, feel free to open an issue.*

## Getting started
See [here](docs/index.md) for usage information.
## License
See [COPYING](COPYING)
