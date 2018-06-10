# sodalite integration into fish
#

function cd
  begin; nohup sodalite --update-access "$argv[-1]" &; end >/dev/null 2>&1
  builtin cd $argv
end

function sodalite-widget 
  set target (sodalite)
  if [ $target ]
      [ -d $target ] ;or set target (dirname $target)
      cd $target
  end
  if not [ $DISPLAY ]
    clear
  end
  commandline -f repaint
end
