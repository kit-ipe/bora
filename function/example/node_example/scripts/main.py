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


template = """
const $key = proxy({
  url: `$value`,
  verbose: false,
});

app.ws('/websocket-streaming/$key', $key);
"""

# js template for local static folder
js_template_local = """<script src="{{ static_url("$key.js") }}"></script>"""

# js template for local static folder
js_template_external = """<script src="$key"></script>"""

js_template_load_player = """
loadPlayer({
    url: 'ws://ipepdvcompute1.ipe.kit.edu:2000/$key/$value',
    canvas: document.getElementById('$value')
});
"""

print("Websocket Streaming ")

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
    print(arguments)
    
    plugin_type = arguments[0]

    print(plugin_type)

    with open("./runtime_env/websocket-streaming/scripts/index.js", "r") as f:
        contents = f.readlines()

    # clear stub section
    tmp_contents = []
    del_flag = False
    for num, line in enumerate(contents):
        if del_flag == False:
            tmp_contents.append(line)

        if "//** BORA START **//" in line:
            del_flag = True

        if "//** BORA END **//" in line:
            del_flag = False
            tmp_contents.append(line)
        
    contents = tmp_contents

    # stub code
    anchor = 0
    for num, line in enumerate(contents):
        if "//** BORA START **//" in line:
            anchor = num
            break
    anchor += 1

    for key, value in varname_data[plugin_type].items():
        print(anchor, value["source"])
        temp_obj = Template(template)
        contents.insert(
            anchor,
            temp_obj.substitute(
                key=key,
                value=value["source"]
            )
        )

    with open("./runtime_env/websocket-streaming/scripts/index.js", "w") as f:
        contents = "".join(contents)
        f.write(contents)
    #print("stub index.js")
    #print("stub status.html")

    
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
        if style_item in varname_data[plugin_type]:
            print(style_item)
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
        temp_obj = Template(js_template_load_player)
        status_js.insert(
            anchor,
            temp_obj.substitute(key="websocket-streaming", value=item))

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


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
