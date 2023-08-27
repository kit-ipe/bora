"""
This script reads the varname.yaml for rtsp and 
register the rtsp links in the index.js with the 
endpoint being the key from the list.

Also, it stubs javascript codes in the status.html 
to load the rtsp streams

Usage: python main.py
"""
import sys
import yaml
from string import Template



# js template for local static folder
js_template_local = """<script src="{{ static_url("$key.js") }}"></script>"""

# js template for local static folder
js_template_external = """<script src="$key"></script>"""

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

#print("HLS Streaming ")

varname_data = None
with open("varname.yaml", 'r') as stream:
    try:
        varname_data = yaml.load(stream, Loader=yaml.Loader)
    except yaml.YAMLError as exc:
        print(exc)

style_data = None
with open("style.yaml", 'r') as stream:
    try:
        style_data = yaml.load(stream, Loader=yaml.Loader)
    except yaml.YAMLError as exc:
        print(exc)


def main(arguments):
    #print(arguments)
    
    plugin_type = arguments[0]

    #print(plugin_type)
    
    with open("./bora/status.html", "r") as f:
        contents = f.readlines()
     
    # stub code
    anchor = 0
    for num, line in enumerate(contents):
        if "<!-- BORA START -->" in line:
            anchor = num
            break
    anchor += 1

    ####
    with open("./bora/template/" + plugin_type + ".html", "r") as f:
        status_template_stub = f.readlines()
    
    for num, line in enumerate(status_template_stub):
        contents.insert(anchor+num, line)

    with open("./bora/status.html", "w") as f:
        contents = "".join(contents)
        f.write(contents)

    ### ASDF
    #for varname in varname_data[plugin_type]:
    #    print(varname)
    #print("check this")   


    js_template_items = [] 
    for style_item in style_data:
        if not plugin_type in varname_data:
            continue
        if style_item in varname_data[plugin_type]:
            #print(style_item)
            js_template_items.append(style_item)

    ### CANVAS
    with open("./bora/static/" + plugin_type + ".js", "r") as f:
        status_js = f.readlines()
    
    # stub code
    anchor = 0
    for num, line in enumerate(status_js):
        if "/** BORA-JS **/" in line:
            anchor = num
            break
    anchor += 1

    for item in js_template_items:
        #print(item)
        temp_obj = Template(js_template_load_player)
        status_js.insert(
            anchor,
            temp_obj.substitute(key=item, value=varname_data[plugin_type][item]["source"]))

    with open("./bora/static/" + plugin_type + ".js", "w") as f:
        status_js = "".join(status_js)
        f.write(status_js)

    ###
    with open("./bora/status.html", "r") as f:
        contents = f.readlines()

    # stub code
    anchor = 0
    for num, line in enumerate(contents):
        if "<!-- BORA-JS -->" in line:
            anchor = num
            break
    anchor += 1

    temp_obj = Template(js_template_local)
    contents.insert(
        anchor,
        temp_obj.substitute(key=plugin_type))

    with open("./bora/status.html", "w") as f:
        contents = "".join(contents)
        f.write(contents)

    """
    #### external JS TODO NTJ
    with open("./bora/status.html", "r") as f:
        contents = f.readlines()

    # stub code
    anchor = 0
    for num, line in enumerate(contents):
        if "<!-- BORA-JS -->" in line:
            anchor = num
            break
    anchor += 1
    
    temp_obj = Template(js_template_external)
    contents.insert(
        anchor,
        temp_obj.substitute(key="https://cdn.jsdelivr.net/npm/rtsp-relay@1.7.0/browser/index.js"))

    temp_obj = Template(js_template_external)
    contents.insert(
        anchor,
        temp_obj.substitute(key="https://cdn.jsdelivr.net/gh/phoboslab/jsmpeg@b5799bf/jsmpeg.min.js"))
    

    with open("./bora/status.html", "w") as f:
        contents = "".join(contents)
        f.write(contents)
    """

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
