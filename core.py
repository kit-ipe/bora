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

widget_queue = []
settings_data = load_data("settings.yaml")
varname_data = load_data("varname.yaml")

bora_init()

# init redis connection
if "redis" in settings_data:
    if settings_data["redis"]:
        if settings_data["redis"]["host"] and settings_data["redis"]["port"]:
            r = redis.Redis(host=settings_data["redis"]["host"], port=settings_data["redis"]["port"])


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


### plugin :-> start timer


#for plugin in plugins_data["plugins"]:
#    #print("timer: " + plugin)
if isinstance(settings_data["timer"]["plugins"], Iterable):
    for plugin in settings_data["timer"]["plugins"]:
        widget_queue.append(plugin)


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
            print("-> Timer is running for:", widget_queue)


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
    if r.ping():
        print("-> Ping to redis server is successful.")
    ts = r.ts()

    sync_timestamp = time.time() * 1000.0

    for plugin in varname_data:
        if plugin in widget_queue:
            print(plugin)
            for sensor in varname_data[plugin]:
                print(sensor)
                print(varname_data[plugin][sensor]["source"])
                url = varname_data[plugin][sensor]["source"]
                data = requests.get(
                    url,
                    auth=(os.environ["BORA_ADEI_USERNAME"],
                          os.environ["BORA_ADEI_PASSWORD"])
                ).content

                data = data.decode("utf-8")

                if data == "":
                    logger.info(str(plugin) + ': Empty data!')
                    print(str(plugin) + ': Empty data!')
                    continue


                if "ERROR" in data.splitlines()[-1]:
                    logger.error(str(param) + ': Query')
                    print("ERROR: " + str(param) + ': Query')
                    continue

                tmp_data = data.splitlines()[-1]

                last_value = tmp_data.split(",")[-1].strip()
                first_value = tmp_data.split(",")[-2].strip()
                
                try:
                    test_x = float(last_value)
                except ValueError:
                    logger.error(str(param) + ': Last value is not a float')
                    print("ERROR: " + str(param) + ': Last value is not a float')
                    continue

                try:
                    time_buffer = first_value.split("-")
                    time_buffer[1] = str(strptime(time_buffer[1],'%b').tm_mon).zfill(2)
                    first_value = "-".join(time_buffer)
                    first_ts = calendar.timegm(datetime.strptime(first_value, "%d-%m-%y %H:%M:%S.%f").timetuple()) * 1000
                except:
                    logger.error(str(param) + ': Last value is not a float')
                    print("ERROR: " + str(param) + ': Last value is not a float')
                    continue

                #print(first_ts)
                #print(last_value)
                ts.add(sensor, int(sync_timestamp), last_value, retention_msecs=86400000)

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


        print(style_data)

        data = {
            "style": style_data,
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

        data = {
            "style": style_data,
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