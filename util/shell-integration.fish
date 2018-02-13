# sodalite integration into fish

function sodalite-widget 
  cd (sodalite)
  commandline -f repaint
end

bind \cf sodalite-widget
