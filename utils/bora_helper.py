import os
import yaml
import shutil
from pathlib import Path

def load_data(data_file):
    res = None
    with open(data_file, 'r') as stream:
        try:
            res = yaml.load(stream, Loader=yaml.Loader)
        except yaml.YAMLError as exc:
            print(exc)
    return res

def bora_init():
    if os.path.isfile("./bora/designer.html"):
       os.remove("./bora/designer.html")
    shutil.copyfile("./bora/blueprint/designer.html", "./bora/designer.html")

    if os.path.isfile("./bora/status.html"):
       os.remove("./bora/status.html")
    shutil.copyfile("./bora/blueprint/status.html", "./bora/status.html")

    if os.path.isdir('./bora/static'):
        shutil.rmtree("./bora/static")
    Path("./bora/static").mkdir(parents=True, exist_ok=True)

    if os.path.isfile("./bora/static/background.png"):
       os.remove("./bora/static/background.png")
    shutil.copyfile("background.png", "./bora/static/background.png")

    # Providing the folder path
    origin_static = "./bora/blueprint/static/"
    target_static = "./bora/static/"

    # Fetching the list of all the files
    origin_static_files = os.listdir(origin_static)

    # Fetching all the files to directory
    for static_file in origin_static_files:
       shutil.copy(origin_static + static_file, target_static + static_file)


