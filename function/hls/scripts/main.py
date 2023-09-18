import sys
import yaml
from string import Template
from function_helper import get_data, copy_template_to_status, copy_custom_code_to_js, copy_javascript_local_import_to_status


js_template_load_player = """
  var $key = document.getElementById('$key');
  if(Hls.isSupported()) {
    var hls = new Hls();
    hls.loadSource('$value');
    hls.attachMedia($key);
    hls.on(Hls.Events.MANIFEST_PARSED,function() {
      video.play();
    });
  }
  else if ($key.canPlayType('application/vnd.apple.mpegurl')) {
    $key.src = '$value';
    $key.addEventListener('canplay',function() {
      $key.play();
    });
  }

  $key.addEventListener("mousemove", function(e) {
    console.log($key.currentTime);
    console.log("Mouse-X: " + (e.clientX + window.pageXOffset));
    console.log("Mouse-Y: " + (e.clientY + window.pageYOffset));
    document.getElementById("position_x_input").value = e.clientX + window.pageXOffset - $key.parentNode.offsetLeft + 1;
    document.getElementById("position_y_input").value = e.clientY + window.pageYOffset - $key.parentNode.offsetTop + 1;
    e.preventDefault();
  }, false);
  
  $key.addEventListener("mousedown", function(e) {
    capture();
    e.preventDefault();
  }, false);

function capture() {
  var canvas = document.getElementById("canvas");
  var video = document.getElementById("$key");
  //var video = document.querySelector("$key");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas
    .getContext("2d")
    .drawImage(video, 0, 0, video.videoWidth, video.videoHeight);

  /** Code to merge image **/
  /** For instance, if I want to merge a play image on center of existing image **/
  const playImage = new Image();
  playImage.src = "path to image asset";
  playImage.onload = () => {
    const startX = video.videoWidth / 2 - playImage.width / 2;
    const startY = video.videoHeight / 2 - playImage.height / 2;
    canvas
      .getContext("2d")
      .drawImage(playImage, startX, startY, playImage.width, playImage.height);
    canvas.toBlob() = (blob) => {
      const img = new Image();
      img.src = window.URL.createObjectUrl(blob);
    };
  };
  /** End **/
}

"""

varname_data = get_data("varname.yaml")
style_data = get_data("style.yaml")


def main(arguments):
    
    plugin_type = arguments[0]
    copy_template_to_status(plugin_type)

    # This list the available variable names in style.yaml
    # Then it only appends variable names that are present in varname.yaml
    js_template_items = [] 
    for style_item in style_data:
        if not plugin_type in varname_data:
            continue
        if style_item in varname_data[plugin_type]:
            js_template_items.append(style_item)

    for item in js_template_items:
        copy_custom_code_to_js(
                plugin_type,
                item,
                varname_data[plugin_type][item]["source"],
                js_template_load_player)

    copy_javascript_local_import_to_status(plugin_type)

    #copy_javascript_external_import_to_status(plugin_type, "https://cdn.jsdelivr.net/npm/rtsp-relay@1.7.0/browser/index.js")
    #copy_javascript_external_import_to_status(plugin_type, "https://cdn.jsdelivr.net/gh/phoboslab/jsmpeg@b5799bf/jsmpeg.min.js")


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
