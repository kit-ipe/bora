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
from function_helper import get_data, copy_template_to_status


varname_data = get_data("varname.yaml")
style_data = get_data("style.yaml")


def main(arguments):
    
    plugin_type = arguments[0]
    copy_template_to_status(plugin_type)

    """
    with open("./bora/status.html", "r") as f:
        contents = f.readlines()
     
    # stub code
    anchor = 0
    for num, line in enumerate(contents):
        if "<!-- BORA START -->" in line:
            anchor = num
            break
    anchor += 1

    #### 01. LOAD PLUGIN TEMPLATE
    with open("./bora/template/" + plugin_type + ".html", "r") as f:
        status_template_stub = f.readlines()
    
    for num, line in enumerate(status_template_stub):
        contents.insert(anchor+num, line)

    with open("./bora/status.html", "w") as f:
        contents = "".join(contents)
        f.write(contents)
    """

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
