import logging
import calendar
import os
import re
import sys
import yaml
import requests
import subprocess
import json

import datetime
from datetime import date
import time
from time import gmtime, strftime

import shutil
from shutil import copyfile, rmtree

import tornado.ioloop
import tornado.web
import tornado.autoreload
from tornado.escape import json_decode, json_encode, url_escape

from threading import Timer
from pathlib import Path
from distutils.dir_util import copy_tree

from string import Template
from utils.bora_helper import load_data, bora_init


root = os.path.dirname(__file__)
BORA_VERSION = "2.0.0"
python_version = sys.version_info.major

# Plugins data
plugin_settings = {}
for filename in os.listdir(os.path.join(root, 'typedef')):
    plugin_settings[filename.split(".")[0]] = None

plugins_data = {
    "plugins": plugin_settings
}

settings_data = load_data("settings.yaml")
varname_data = load_data("varname.yaml")

bora_init()

###########################
#  Setup Plugins          #
###########################

# init :-> create fresh runtime_env folder
if os.path.isdir('./runtime_env'):
    rmtree("./runtime_env")
Path("./runtime_env").mkdir(parents=True, exist_ok=True)


# init :-> copy the plugins to the user space
for plugin in plugins_data["plugins"]:
    #print("copy: " + plugin)
    # load lambda.yaml
    copy_tree(
        "./bora/function/" + plugin,
        "./runtime_env/" + plugin
    )

### plugin :-> install
for plugin in plugins_data["plugins"]:
    #print("install: " + plugin)
    # load lambda.yaml
    
    with open("./bora/function/" + plugin + "/lambda.yaml" , 'r') as stream:
        try:
            lambda_data = yaml.load(stream, Loader=yaml.Loader)
            #print(lambda_data["install"])
            for item in lambda_data["install"]:
                if item:
                    os.system(item)
        except yaml.YAMLError as exc:
            print(exc)


### plugin :-> setup
for plugin in plugins_data["plugins"]:
    #print("setup: " + plugin)
    # load lambda.yaml
    
    # plugin
    shutil.copy("./bora/js_plugins/" +  plugin + ".js", "./bora/static/" + plugin + ".js")

    with open("./bora/function/" + plugin + "/lambda.yaml" , 'r') as stream:
        try:
            lambda_data = yaml.load(stream, Loader=yaml.Loader)
            #print(lambda_data["install"])
            #for item in lambda_data["javascript"]:
            #    if item:
            #        shutil.copy("./bora/js_plugins/" + item, "./bora/static/" + item)
            for item in lambda_data["setup"]:
                if item:
                    #cmd = item % (settings_data["plugins"][plugin]["function"])
                    cmd = item % (plugin)
                    os.system(cmd)    
        except yaml.YAMLError as exc:
            print(exc)

### plugin :-> run
for plugin in plugins_data["plugins"]:
    #print("run: " + plugin)
    # load lambda.yaml
    
    with open("./bora/function/" + plugin + "/lambda.yaml" , 'r') as stream:
        try:
            lambda_data = yaml.load(stream, Loader=yaml.Loader)
            #print(lambda_data["run"])
            for item in lambda_data["run"]:
                #print(item)
                if item:
                    #print("run?!")
                    os.system(item)
        except yaml.YAMLError as exc:
            print(exc)


def setup_custom_logger(name):
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    handler = logging.FileHandler('log.txt', mode='w')
    handler.setFormatter(formatter)
    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.addHandler(screen_handler)
    return logger

logger = setup_custom_logger('BORA')


class ListHandler(tornado.web.RequestHandler):
    def get(self):
        with open("./bora/cache.yaml", 'r') as stream:
            try:
                response = yaml.load(stream, Loader=yaml.Loader)
            except yaml.YAMLError as exc:
                print(exc)
        if response is None:
            response = {"error": "No data entry."}
        self.write(response)


class DesignerHandler(tornado.web.RequestHandler):
    def get(self):
        print("In designer mode.")
        with open("./bora/cache.yaml", 'r') as stream:
            try:
                cache_data = yaml.load(stream, Loader=yaml.Loader)
            except yaml.YAMLError as exc:
                print(exc)
        
        # check other data sources: rtsp or rest
        with open("style.yaml", 'r') as stream:
            try:
                style_data = yaml.load(stream, Loader=yaml.Loader)
            except yaml.YAMLError as exc:
                print(exc)
        

        
        # Prepare filtered varname_data
        #print(settings_data["plugins"])
        #print(list(settings_data["plugins"].keys()))
        #print(varname_data)
        
        varname_filter_data = {}
        for item in list(plugins_data["plugins"]):
            if not item in varname_data:
                continue
            varname_filter_data[item] = varname_data[item]

        # Prepare a list of sensor names from the filtered varname
        sensor_name_filter = []
        for key,item in varname_filter_data.items():
            #print(key, item)
            for grain in item.items():
                sensor_name_filter.append(grain[0])
        
        # Prepare filtered style_data
        style_filter_data = {}
        #print(style_data)
        for item in list(style_data.keys()):
            if item in sensor_name_filter:
                style_filter_data[item] = style_data[item]



        # Prepare typedef yaml
        typedef_data = {}
        for myitem in plugins_data["plugins"]:
            tmp_data = None
            with open("./bora/typedef/" + str(myitem) + ".yaml", 'r') as stream:
                try:
                    tmp_data = yaml.load(stream, Loader=yaml.Loader)
                except yaml.YAMLError as exc:
                    print(exc)
            typedef_data[myitem] = tmp_data


        data = {
            "cache": cache_data,
            "style": style_filter_data,
            "vardata": varname_filter_data,
            "typedef": typedef_data
        }

        data["title"] = settings_data["title"]
        data["version"] = BORA_VERSION
        
        r = json.dumps(data)
        loaded_r = json.loads(r)
        
        self.render('designer.html', data=loaded_r)


class VersionHandler(tornado.web.RequestHandler):
    def get(self):
        response = {
            "version": BORA_VERSION,
            "response": true,
            "http": "get",
            "action": "version",
            "time": str(datetime.datetime.now())
        }
        #print(response)
        self.write(response)


class BackupHandler(tornado.web.RequestHandler):
    def post(self):
        try:
            backup_dst = os.getcwd() + "/backup/"
            fname = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            os.makedirs(backup_dst + fname)
            copyfile("varname.yaml", backup_dst +
                fname + "/varname.yaml")
            copyfile("style.yaml", backup_dst +
                fname + "/style.yaml")
            res = True
        except:
            res = False

        response = {
            "response": res,
            "http": "post",
            "action": "backup",
            "time": str(datetime.datetime.now())
        }
        #print(response)
        self.write(response)


class SaveHandler(tornado.web.RequestHandler):

    def post(self):
        json_obj = json_decode(self.request.body)
        
        with open("style.yaml", 'wb') as output:
            output.write(yaml.safe_dump(json_obj,  encoding='utf-8',
                         allow_unicode=True, default_flow_style=False))
        response = {"success": "Data entry inserted."}


class StatusHandler(tornado.web.RequestHandler):

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")

    def options(self, *args):
        self.set_header("Access-Control-Allow-Methods", "*")
        self.set_header("Access-Control-Request-Credentials", "true")
        self.set_header("Access-Control-Allow-Private-Network", "true")
        self.set_header("Access-Control-Allow-Headers", "*")
        self.set_status(204)  # No Content

    def get(self):
        #print( "In status mode.")
        with open("style.yaml", 'r') as stream:
            try:
                style_data = yaml.load(stream, Loader=yaml.Loader)
            except yaml.YAMLError as exc:
                print(exc)

        if not os.path.isfile("./bora/cache.yaml"): 
            open("./bora/cache.yaml","wb")

        with open("./bora/cache.yaml", 'r') as vstream:
            try:
                cache_data = yaml.load(vstream, Loader=yaml.Loader)
            except yaml.YAMLError as exc:
                print(exc)

        print(varname_data)

        data = {
            "style": style_data,
            "cache": cache_data,
            "varname": varname_data
        }

        data["title"] = settings_data["title"]
        data["version"] = BORA_VERSION

        self.render('status.html', data=data)


class GetDataHandler(tornado.web.RequestHandler):
    def get(self):
        cache_data = None
        if not os.path.isfile("./bora/cache.yaml"): 
            #print( "BORA is loading data, please refresh the page again in a moment.")
            open("./bora/cache.yaml","wb")
        with open("./bora/cache.yaml", 'r') as stream:
            try:
                cache_data = yaml.load(stream, Loader=yaml.Loader)
            except yaml.YAMLError as exc:
                print(exc)
        if cache_data is None:
            cache_data = {}

        tmp_data = {}
        for data_source in cache_data:
            #print(data_source)
            if data_source == "time":
                tmp_data["time"] = cache_data["time"] 
            else:
                #print(data_source)
                for param in cache_data[data_source]:
                    #print(param)
                    tmp_data[param] = cache_data[data_source][param]
        self.write(tmp_data)


application = tornado.web.Application([
    (r"/version/?", VersionHandler), 
    (r"/list/?", ListHandler), # list sensors in cache
    (r"/backup/?", BackupHandler), # save the varname and style yamls into backup folder
    (r"/designer/?", DesignerHandler),
    (r"/", StatusHandler),
    (r"/save/?", SaveHandler), # save the style from frontend to backend yaml file
    (r"/getdata/?", GetDataHandler), # get data from cache file
], debug=True, static_path=os.path.join(root, 'static'),
    cookie_secret='L8LwECiNRxq2N0N2eGxx9MZlrpmuMEimlydNX/vt1LM=')


if __name__ == "__main__":
    application.listen(int(settings_data["port"]))
    tornado.autoreload.start()
    tornado.ioloop.IOLoop.instance().start()
