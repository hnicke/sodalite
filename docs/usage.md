# Sodalite: Usage

[####](####) Following general actions can be triggered everywhere in `sodalite`:

#### exit `ENTER`
Exit `sodalite`. Prints the current entry to `stdout`.

In case `sodalite` was invoked with the provided shell integration key-bindings, will `cd` into current directory. If the current entry is not a directoy but a file, will `cd` into the parent directory.

#### abort `C-c`
Exit `sodalite` without printing current directory to `stdout`.

#### normal_mode `ESC`
Enter normal mode.

#### filter `/`
Focuses the filter bar on the bottom. Use regular expressions to filter displayed entries. Case is ignored. Press `CR` to submit or `ESC` to dismiss the filter.

#### scroll_page_down `C-f`
Scroll down one page.

#### scroll_page_up `C-b`
Scroll up one page.

#### scroll_half_page_down `C-d`
Scroll down half a page.

#### scroll_half_page_down `C-u`
Scroll up half a page.

## Modi

Like in vim, there are different modi. In each mode, a different set of actions is available.

- `NORMAL`: navigate the file system
- `ASSIGN`: assign keys to files
- `OPERATE`: modify the file system 

---
### `NORMAL` mode
`sodalite` automatically assigns keys to entries in order to enable quick navigation. For navigating to a specifc entry, simply press its assigned key.
Valid values for keys are all letters of the alphabet (lower and upper case), so there are 52 different keys. For every directory, each key must be unique. If there are more than 52 entries in a directory, some entries will end up having no key assigned to them. However, you can change this in `ASSIGN` mode.


#### normal.go_to `[a-zA-Z]` 
Navigate to the entry matching pressed key.

#### normal.go_to_home ``[`~]``
Navigate to the `$HOME` directory.

#### normal.go_to_parent `.`
Navigate to the parent directory. Does nothing if parent directory does not exist.

#### normal.go_to_previous `C-h`
Navigate back in history one step. Does nothing if history does not contain a previous entry.

#### normal.go_to_next `C-l`
Navigate forward in history. Does nothing if history does not contain a next entry.


#### normal.assign_mode `=`
Enter assign mode.

---
### `ASSIGN` mode
The `ASSIGN` mode is useful if you want to assign a specific key to an entry. This is accomplished in two steps:
1. Press a key associated with an entry or select an entry manually
2. Press the new key

If the newly assigned key is already assigned to another entry in the current directory, keys get swapped.
Abort the process by pressing `Esc`.

#### assign.select_next `C-n`
Select next entry.

#### assign.select_previous `C-p`
Select previous entry.

---
### `OPERATE` mode

>This mode is **not yet implemented**.

The `OPERATE` mode allows to modify the file system.  Following built-in commands are included in this mode:

- pasting
- yanking
- deleting
- renaming
    
---
## Configuration

Upon startup, `sodalite` looks at following places for its configuration:
1. `$XDG_CONFIG_HOME/sodalite/sodalite.yml` (user specific configuration)
    - if `$XDG_CONFIG_HOME` is not set, falls back to `$HOME/.config/sodalite/sodalite.yml`
2. `/etc/sodalite.yml` (system-wide configuration)

The configuration is written in [YAML](https://learnxinyminutes.com/docs/yaml/).

#### Example configuration
```yml
keymap:
  "*": normal.toggle_bookmark
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

#### Customize the default keymap

> This feature is **not yet implemented**.

```yaml
keymap:
  <keybinding>: <built-in>
```
If <built-in> matches the name of a built-in action, given <keybinding> is bound to this action.
    
- **<keybinding>**: (String, required) The keybinding which is used to trigger the action. Use `C-a` and `M-A`to define the binding `Control-a` and `Meta-A`. Other special keys: `ESC`, `ENTER`, `F1`
- **<built-in>** (String, required) The name of a built-in function (e.g., `normal.toggle_bookmark`)
    
    
#### Action hooks
It is possible to define custom keybindings in order to trigger your own actions.
>Note: Keybindings defined in the configuration file will take precedence over the default keymap.

A hook is defined with following **syntax**:
###### Extended notation:
```yaml
<keybinding>:
  action: <action>
  label: <label>
```
###### Short notation:
```yaml
<keybinding>: <action>
```

- **<action>**: (String, required) The action which is triggered by given keybinding. <action> is interpreted as a shell command and executed within a subshell. Use `$entry` to reference the current entry. If given string ends with `#q`, `sodalite` will exit after command execution.
- **<label>**: (String, optional) Is used to represent the hook in the UI. Should be short and concise. If omitted, the hook will not be displayed in the UI.
- **<keybinding>**: [see above](#customize-the-default-keymap)

The **hooks** declaration works like this:
```yaml
hooks:
  dir:
    <hook>
    ...
  plain_text:
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

- **dir**: (optional) Declared hooks within this map are available whenever the current entry is a directory.
- **plain_text**: (optional) Declared hooks within this map are available whenever the current entry is a plain text file.
- **custom**: (optional) Declare one or more custom hooks and attach them to one or multiple extensions, and repeat this if you want. This makes the hooks available whenever the current entry has one of its attached extension.
