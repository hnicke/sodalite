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
                builtin cd "$dirname"
                zle accept-line
            else
                RBUFFER=" $target $RBUFFER"
                zle reset-prompt
            fi
        fi
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

    bind -x '"\e200": sodalite-bash'
    bind -x '"\e201": tput cuu 2; tput ed; READLINE_LINE=$TMP_READLINE_LINE; READLINE_POINT=$TMP_READLINE_POINT; unset {TMP_READLINE_LINE,TMP_READLINE_POINT}'
    bind -m vi-command '"f": "\e200 dd\C-m \e \e201 i"'
    bind -m emacs '"\C-f":"\e200 \C-u\C-m \e201"'

fi

if ! [ "$SODALITE_CD_INTERCEPTION" = 'false' ]; then
    function cd {
        (
            nohup nice --adjustment=20 sodalite --update-access "$@" &
        ) >/dev/null 2>&1
        builtin cd "$@"
    }
fi
