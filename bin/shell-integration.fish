# sodalite integration into fish
#

function sodalite-widget 
  set target (sodalite)
  if [ "$target" ]
      [ -d "$target" ] ;or set target (dirname "$target")
      cd $target
  end
  if not [ "$DISPLAY" ]
    clear
  end
  commandline -f repaint
end

if not [ "$SODALITE_CD_INTERCEPTION" = 'false' ] 
    function cd
      begin; nohup sodalite --update-access "$argv[-1]" &; end >/dev/null 2>&1
      # catching the errors here: so user does not see an inconvenient error message
      if not [ "$argv" ]
        # everythings alright
      else if not [ -e "$argv[-1]" ]
        echo "cd: no such file or directory: $argv[-1]" > /dev/stderr
      else if not [ -x "$argv[-1]" ]
        echo "cd: permission denied: $argv[-1]" > /dev/stderr
      end
      builtin cd $argv
    end
end
