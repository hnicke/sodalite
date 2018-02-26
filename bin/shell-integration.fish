# sodalite integration into fish

function sodalite-widget 
  set target (sodalite)
  [ -d $target ] ;or set target (dirname $target)
  cd $target
  commandline -f repaint
end

bind \cf sodalite-widget
