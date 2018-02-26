# Sodalite: Exploration at the speed of thought

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
> - [sqlite](https://www.sqlite.org/index.html)


## Configuration
`sodalite` needs to get integrated into your favourite shell (supported: `bash`, `zsh`, `fish`).  

#### bash / zsh
Simply add following line to your `.bashrc` / `.zshrc`:

```bash
source /usr/share/sodalite/shell-integration.sh
```
The script will set up a keybinding which launches `sodalite`.
* Emacs keymap:     `Control + f`
* Vim keymap:       `f` in command (aka normal) mode

#### fish
Create the function `fish_user_key_bindings` in your 'config.fish' (if not already exists). 
Then, insert following line into the function:
```bash
source /usr/share/sodalite/shell-integration.fish
```

*If your favourite shell is not supported, feel free to open an issue.*

## Getting started
See [here](docs/index.md) for usage information.
## License
See [COPYING](COPYING)
