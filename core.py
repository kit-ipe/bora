from parser import Factory
import re
import redis
import logging
import calendar
import os
import re
import sys
import yaml
import requests
import subprocess
import json

#import datetime
from datetime import date, datetime
import time
from time import gmtime, strftime
from time import strptime

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
from collections.abc import Iterable
from threading import Thread, Event


root = os.path.dirname(__file__)
BORA_VERSION = "2.0.0"


# Plugins data
plugin_settings = {}
for filename in os.listdir(os.path.join(root, 'typedef')):
    plugin_settings[filename.split(".")[0]] = None

plugins_data = {
    "plugins": plugin_settings
}

timer_queue = []
settings_data = load_data("settings.yaml")
varname_data = load_data("varname.yaml")
# Style might change dynamically, so we need to load it every time
#style_data = load_data("style.yaml")


bora_init()

# init redis connection
if "redis" in settings_data:
    if settings_data["redis"]:
        if settings_data["redis"]["host"] and settings_data["redis"]["port"]:
            try:
                r = redis.Redis(
                    host=settings_data["redis"]["host"],
                    port=settings_data["redis"]["port"]
                )
                print("Redis connection successful.")
            except:
                print("Redis connection failed.")
                stop_flag.set()


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


### plugin :-> start timer


#for plugin in plugins_data["plugins"]:
#    #print("timer: " + plugin)
if isinstance(settings_data["timer"]["group"], Iterable):
    for plugin in settings_data["timer"]["group"]:
        timer_queue.append(plugin)


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

# Start Timer
class TimerThread(Thread):
    def __init__(self, event):
        Thread.__init__(self)
        self.stopped = event

    def run(self):
        while not self.stopped.wait( settings_data["timer"]["server"] / 1000.0 ):
            current_datetime = datetime.now()
            str_current_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")
            dt_obj = datetime.strptime(str_current_datetime, '%Y-%m-%d %H:%M:%S.%f')
            millisec = dt_obj.timestamp() * 1000
            print("##################")
            print("##" , str_current_datetime)
            print("##" , millisec)
            print("-> Timer is running for:", timer_queue)


            write_data_to_redis()
            #ts.add("yoyoyo", 1657265437756, 1, retention_msecs=86400000)
            # call a function
            print("\r\n")

stop_flag = Event()
thread = TimerThread(stop_flag)
thread.start()
# this will stop the timer
#stop_flag.set()


def write_data_to_redis():
    
    default_interface = settings_data["interface"]
    current_interface = None
    current_url = None

    try:
        if r.ping():
            print("-> Ping to redis server is successful.")
    except:
        print("-> Ping to redis server failed:" + str(settings_data["redis"]["host"]) + ":" + str(settings_data["redis"]["port"]))
        stop_flag.set()
        return

    ts = r.ts()

    sync_timestamp = time.time() * 1000.0

    #print("Total Varname: " + str(len(varname_data)))
    for key_varname in varname_data:
        #print("-> Processing: " + key_varname)
        if "interface" in varname_data[key_varname]:
            current_interface = varname_data[key_varname]["interface"]
            current_url = varname_data[key_varname]["url"]
        else:
            current_url = varname_data[key_varname]
            current_interface = default_interface

        current_parser = Factory(current_interface)
        #print("-> Parsing data from: " + current_url)
        #print(current_parser.parse(current_url))

        res = current_parser.parse(current_url)
        if res is None:
            print("-> No data for: " + key_varname)
            continue

        ts.add(
            key_varname,
            res["timestamp"],
            res["value"],
            retention_msecs=86400000)

    print("-> Writing data to redis.")


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
        
        # check other data sources: rtsp or rest
        with open("style.yaml", 'r') as stream:
            try:
                style_data = yaml.load(stream, Loader=yaml.Loader)
            except yaml.YAMLError as exc:
                print(exc)

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

        # Load varname data
        vardata = {}
        with open("varname.yaml", 'r') as stream:
            try:
                vardata = yaml.load(stream, Loader=yaml.Loader)
            except yaml.YAMLError as exc:
                print(exc)

        data = {
            "style": style_data,
            "typedef": typedef_data,
            "vardata": vardata,
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

        data = {
            "style": style_data,
            "varname": varname_data,
            "delay": settings_data["timer"]["client"]
        }

        data["title"] = settings_data["title"]
        data["version"] = BORA_VERSION

        self.render('status.html', data=data)


class GetDataHandler(tornado.web.RequestHandler):
    def get(self):
        with open("style.yaml", 'r') as stream:
            try:
                style_data = yaml.load(stream, Loader=yaml.Loader)
            except yaml.YAMLError as exc:
                print(exc)

        ts = r.ts()
        data = {}
       
        for key_varname in varname_data:
            if r.exists(key_varname):
                if key_varname in style_data:
                    latest_data = ts.get(key_varname)
                    data[key_varname] = {
                        "timestamp": latest_data[0],
                        "value": latest_data[1],
                        "widget": style_data[key_varname]["widget"],
                        "invalid": settings_data["timer"]["invalid"]
                    }
                else:
                    pass
                    #print("No style data for: " + key_varname)
            else:
                pass
                #print("No data for: " + key_varname)
        
        for key_stylename in style_data:
            # filter key_stylename to calc_ prefix
            if key_stylename.startswith("calc_"):
                res = re.findall(r'\[.*?\]', style_data[key_stylename]["div"]["data-formula"])
                for item in res:
                    varname_in_calc = item[1:-1]
                    if not varname_in_calc in data:
                        if r.exists(varname_in_calc):
                            latest_data = ts.get(varname_in_calc)
                            data[varname_in_calc] = {
                                "timestamp": latest_data[0],
                                "value": latest_data[1],
                                "widget": None,
                                "invalid": settings_data["timer"]["invalid"]
                            }
                        else:
                            pass
                            #print("No data for (calc): " + varname_in_calc)
        self.write(data)


######################### data viusalization ##################################
#fetches the data from Redis and returns it as JSON

class RedisDataHandler(tornado.web.RequestHandler):
    def get(self):
        try:
            ts = r.ts()
            keys = varname_data.keys()
            data = {}
            for key in keys:
                print(key)   
                try:
                    latest_data = ts.get(key)
                    if latest_data:
                        data[key] = {
                            "timestamp": latest_data[0],
                            "value": latest_data[1]
                        }
                except Exception as e:
                    logging.error(f"Error fetching data for {key}: {e}")
            self.write(json.dumps(data))
        except Exception as e:
            self.write({"error": str(e)})


class RedisDataPageHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('redis.html')

application = tornado.web.Application([
    (r"/version/?", VersionHandler), 
    (r"/list/?", ListHandler), # list sensors in cache
    (r"/backup/?", BackupHandler), # save the varname and style yamls into backup folder
    (r"/designer/?", DesignerHandler),
    (r"/", StatusHandler),
    (r"/save/?", SaveHandler), # save the style from frontend to backend yaml file
    (r"/getdata/?", GetDataHandler), # get data from cache file
    (r"/get-redis-data/?", RedisDataHandler),
    (r"/redis-data/?", RedisDataPageHandler), 
], debug=True, static_path=os.path.join(root, 'static'),
    cookie_secret='L8LwECiNRxq2N0N2eGxx9MZlrpmuMEimlydNX/vt1LM=')


if __name__ == "__main__":
    application.listen(int(settings_data["port"]))
    tornado.autoreload.start()
    tornado.ioloop.IOLoop.instance().start()
