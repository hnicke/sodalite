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

if [ $shell = 'zsh' ]; then
    function sodalite-emacs-widget {
        setup_cleanup
        target=$(sodalite)
        if [ "$target" ]; then
            if [ -d "$target" ]; then 
                dirname=$target
            else
                dirname="$(dirname "$target")"
                RBUFFER=" $(basename "$target") $RBUFFER"
            fi
            builtin cd "$dirname"
        fi
        zle reset-prompt
    }

    function sodalite-vim-widget {
        sodalite-emacs-widget
        zle -K viins
    }


    zle     -N      sodalite-vim-widget
    zle     -N      sodalite-emacs-widget
    bindkey -M vicmd 'f'  sodalite-vim-widget
    bindkey -M emacs '^f' sodalite-emacs-widget
elif [ $shell = 'bash' ]; then
    function sodalite-bash {
        setup_cleanup
        target=$(sodalite)
        if [ "$target" ]; then
            if [ -d "$target" ]; then 
                dirname=$target
            else
                dirname="$(dirname $target)"
                before=${READLINE_LINE:0:$READLINE_POINT}
                insert=$(basename "$target")
                after=${READLINE_LINE:$READLINE_POINT}
                TMP_READLINE_LINE="$before $insert $after"
                TMP_READLINE_POINT=$((${#before}-1))
            fi
            builtin cd "$dirname"
        fi
        unset {target,dirname,before,insert,after}
    }
    bind -m vi-command -x '"\200": sodalite-bash'
    bind -m vi-command -x '"\201": tput cuu 2; tput ed; READLINE_LINE=$TMP_READLINE_LINE; READLINE_POINT=$TMP_READLINE_POINT; unset {TMP_READLINE_LINE,TMP_READLINE_POINT}'
    bind -m vi-command '"f": "\200 dd\C-m \e \201 i"'
    bind -m emacs '"\C-f":"\200 \C-u\C-m \201'
fi

if ! [ "$SODALITE_CD_INTERCEPTION" = 'false' ]; then
    function cd { 
        for last in $@; do true; done
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
        [[ "$argv[-1]" =~ ^(\.|\.\.)$ ]] ||
        (
            nohup sodalite --update-access "$last" &
        ) >/dev/null 2>&1
        builtin cd "$@"
    }
fi
