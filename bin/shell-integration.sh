# sodalite shell integration

shell=$(ps -p $$ | tail -n1 | rev | cut -d" " -f1 | rev)


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
    if [ "$target" ]; then
        [ -d "$target" ] || target="$(dirname $target)"
        builtin cd "$target"
    fi
    zle reset-prompt
}

function sodalite-vim-widget {
    sodalite-emacs-widget
    zle -K viins
}

if [ $shell = 'zsh' ]; then
    zle     -N      sodalite-vim-widget
    zle     -N      sodalite-emacs-widget
    bindkey -M vicmd 'f'  sodalite-vim-widget
    bindkey -M emacs '^f' sodalite-emacs-widget
elif [ $shell = 'bash' ]; then
    bind -m vi-command '"f":"ddi setup_cleanup; cd $(sodalite); tput cuu1; tput ed\n"'
    bind -m emacs '"\C-f":"\C-k\C-u setup_cleanup; cd $(sodalite); tput cuu1; tput ed\n"'
fi

if ! [ "$SODALITE_CD_INTERCEPTION" = 'false' ]; then
    function cd { 
        for last in $@; do true; done
        (
            nohup sodalite --update-access "$last" &
        ) >/dev/null 2>&1
        # catching the errors here, so user does not see an inconvenient error message
        if [ "$@" ]; then
            if ! [ -e "$last" ]; then
                echo "cd: no such file or directory: $last" > /dev/stderr
                return 1
            elif ! [ -d "$last" ]; then
                echo "cd: not a directory: $last" > /dev/stderr
                return 1
            elif ! [ -x "$last" ]; then
                echo "cd: permission denied: testing" > /dev/stderr
                return 1
            fi
        fi
        builtin cd "$@"
    }
fi
