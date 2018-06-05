# sodalite shell integration

function headless_clear {
    [ $DISPLAY ] || clear
    # untrap
    trap - EXIT SIGTERM SIGINT
}

function setup_cleanup {
    trap headless_clear EXIT SIGTERM SIGINT
}

function sodalite-emacs-widget {
    setup_cleanup
    target="$(sodalite)"
    if [ $target ]; then
        [ -d "$target" ] || target="$(dirname $target)"
        cd "$target"
    fi
    zle reset-prompt
}

function sodalite-vim-widget {
    sodalite-emacs-widget
    zle -K viins
}

shell=$(ps -p $$ | tail -n1 | rev | cut -d" " -f1 | rev)
if [ $shell = 'zsh' ]; then
    zle     -N      sodalite-vim-widget
    zle     -N      sodalite-emacs-widget
    bindkey -M vicmd 'f'  sodalite-vim-widget
    bindkey -M emacs '^f' sodalite-emacs-widget
elif [ $shell = 'bash' ]; then
    bind -m vi-command '"f":"ddisetup_cleanup; cd $(sodalite); tput cuu1; tput ed\n"'
    bind -m emacs '"\C-f":"\C-k\C-usetup_cleanup; cd $(sodalite); tput cuu1; tput ed\n"'
fi
