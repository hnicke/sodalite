# sodalite integration into fish

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

bind \cf sodalite-widget
