# sodalite shell integration

# source that behaves like in bash
function _source {
  alias shopt=':'
  alias _expand=_bash_expand
  alias _complete=_bash_comp
  emulate -L sh
  setopt kshglob noshglob braceexpand
  builtin source "$@"
}

function sodalite-widget {
    _source sodalite < /dev/tty
    zle reset-prompt
    zle -K viins
}

shell=$(basename $SHELL)
if [ $shell = 'zsh' ]; then
    zle     -N      sodalite-widget
    bindkey -a 'f'  sodalite-widget
elif [ $shell = 'bash' ]; then
    bind -m vi-command '"f":"ddisource sodalite; tput cuu1; tput ed\n"'
    bind -m emacs '"\C-f":"\C-k\C-usource sodalite; tput cuu1; tput ed\n"'
fi
