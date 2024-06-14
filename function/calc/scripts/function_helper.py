import yaml


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