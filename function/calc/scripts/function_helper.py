import yaml
from string import Template


def get_data(data_file):
    res = None
    with open(data_file, 'r') as stream:
        try:
            res = yaml.load(stream, Loader=yaml.Loader)
        except yaml.YAMLError as exc:
            print(exc)
    return res

def copy_template_to_status(plugin_type):
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

def copy_javascript_local_import_to_status(plugin_type):
    js_template_local = """<script src="{{ static_url("$key.js") }}"></script>"""

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