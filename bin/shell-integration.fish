# sodalite integration into fish
#

function sodalite-widget 
  set target (sodalite)
  if [ "$target" ]
      if [ -d "$target" ] 
        cd "$target"
      else
        set cursor (commandline -C)
        commandline -i " $target "
        commandline -C "$cursor"
      end
      commandline -f repaint
  end
  if not [ "$DISPLAY" ]
    clear
  end
end

if not [ "$SODALITE_CD_INTERCEPTION" = 'false' ] 
    function cd
      if builtin cd $argv
        if not echo "$argv[-1]" | grep -qE '^(\.|\.\.)$'
            begin; nohup sodalite --update-access "$argv[-1]" "$OLDPWD" &; end >/dev/null 2>&1
        end
      end
    end
end
