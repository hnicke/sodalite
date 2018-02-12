# sodalite: a quick file navigator


### Usage
For efficient usage, sodalite needs to get integrated into your shell. 

#### bash


#### zsh
Add to `.zprofile`:
```bash
# make 'source' behave more like in bash
source() {
  alias shopt=':'
  alias _expand=_bash_expand
  alias _complete=_bash_comp
  emulate -L sh
  setopt kshglob noshglob braceexpand
  builtin source "$@"
}
alias .='source'
# add keybinding (ctrl+space)
# TODO add bindings for emacs mode
bindkey -as 'f' 'ddisource sodalite^M'
```

