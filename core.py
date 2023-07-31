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


root = os.path.dirname(__file__)
BORA_VERSION = "1.1.0"
python_version = sys.version_info.major


###########################
#  Loading setup data     #
###########################
setings_data = None
with open("settings.yaml", 'r') as stream:
    try:
        settings_data = yaml.load(stream, Loader=yaml.Loader)
    except yaml.YAMLError as exc:
        print(exc)
print(settings_data)


varname_data = None
with open("varname.yaml", 'r') as stream:
    try:
        varname_data = yaml.load(stream, Loader=yaml.Loader)
    except yaml.YAMLError as exc:
        print(exc)


###########################
#  Copy Master files      #
###########################
shutil.copyfile("background.png", "./bora/static/background.png")

shutil.copyfile("./bora/designer_master.html", "./bora/designer.html")
shutil.copyfile("./bora/status_master.html", "./bora/status.html")


###########################
#  Setup Plugins          #
###########################

# init :-> create fresh runtime_env folder
if os.path.isdir('./runtime_env'):
    rmtree("./runtime_env")
Path("./runtime_env").mkdir(parents=True, exist_ok=True)


# init :-> copy the plugins to the user space
for plugin in settings_data["plugins"]:
    print("copy: " + plugin)
    # load lambda.yaml
    if settings_data["plugins"][plugin]["function"]:
        print("    fn: " + settings_data["plugins"][plugin]["function"])

        copy_tree(
            "./bora/function/" + settings_data["plugins"][plugin]["function"],
            "./runtime_env/" + settings_data["plugins"][plugin]["function"]
        )

### plugin :-> install
for plugin in settings_data["plugins"]:
    print("install: " + plugin)
    # load lambda.yaml
    
    if settings_data["plugins"][plugin]["function"]:
        print("    fn: " + settings_data["plugins"][plugin]["function"])

        with open("./bora/function/" + settings_data["plugins"][plugin]["function"] + "/lambda.yaml" , 'r') as stream:
            try:
                lambda_data = yaml.load(stream, Loader=yaml.Loader)
                #print(lambda_data["install"])
                for item in lambda_data["install"]:
                    if item:
                        os.system(item)
            except yaml.YAMLError as exc:
                print(exc)


### plugin :-> setup
for plugin in settings_data["plugins"]:
    print("setup: " + plugin)
    # load lambda.yaml
    if settings_data["plugins"][plugin]["function"]:
        print("    fn: " + settings_data["plugins"][plugin]["function"])
        with open("./bora/function/" + settings_data["plugins"][plugin]["function"] + "/lambda.yaml" , 'r') as stream:
            try:
                lambda_data = yaml.load(stream, Loader=yaml.Loader)
                #print(lambda_data["install"])
                for item in lambda_data["setup"]:
                    if item:
                        cmd = item %(plugin)
                        os.system(cmd)
            except yaml.YAMLError as exc:
                print(exc)


### plugin :-> run
for plugin in settings_data["plugins"]:
    print("run: " + plugin)
    # load lambda.yaml
    if settings_data["plugins"][plugin]["function"]:
        print("    fn: " + settings_data["plugins"][plugin]["function"])
    
        with open("./bora/function/" + settings_data["plugins"][plugin]["function"] + "/lambda.yaml" , 'r') as stream:
            try:
                lambda_data = yaml.load(stream, Loader=yaml.Loader)
                print("Checking...")
                print(lambda_data["run"])
                for item in lambda_data["run"]:
                    print(item)
                    if item:
                        print("run?!")
                        os.system(item)
            except yaml.YAMLError as exc:
                print(exc)


### plugin :-> javascript
for plugin in settings_data["plugins"]:
    print("javascript: " + plugin)
    # load lambda.yaml
    if settings_data["plugins"][plugin]["function"]:
        print("    fn: " + settings_data["plugins"][plugin]["function"])
    
        with open("./bora/function/" + settings_data["plugins"][plugin]["function"] + "/lambda.yaml" , 'r') as stream:
            try:
                lambda_data = yaml.load(stream, Loader=yaml.Loader)
                print(lambda_data["javascript"])
                for item in lambda_data["javascript"]:
                    if item:
                        print("Copy Javascript")
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


"""
class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

    def setInterval(self, interval):
        self.interval = interval


months = {
    'Jan' : 1,
    'Feb' : 2,
    'Mar' : 3,
    'Apr' : 4,
    'May' : 5,
    'Jun' : 6,
    'Jul' : 7,
    'Aug' : 8,
    'Sep' : 9,
    'Oct' : 10,
    'Nov' : 11,
    'Dec' : 12
}
"""


"""
def fetchDataADEI():

    with open("varname.yaml", 'r') as stream:
        try:
            varname = yaml.load(stream, Loader=yaml.Loader)
        except yaml.YAMLError as exc:
            print(exc)
    if varname is None:
        print("Warning: Empty varname file. Nothing to read.")
        return

    cache_data = {}
    tmp_cache_data = {}
    curtime = int(time.time())
    time_image_range = str((curtime-3600)) + "-" + str(curtime)
    time_range = "3600,-1"
    for data_source in varname:
        if data_source == "adei":
            for param in varname["adei"]:
                dest = os.environ["BORA_ADEI_SERVER"] + 'services/getdata.php'
                url = dest + "?" + varname["adei"][param] + "&window=" + time_range + "&experiment=*-*&rt=full&cache=1"
                data = requests.get(url,
                                    auth=(os.environ["BORA_ADEI_USERNAME"],
                                          os.environ["BORA_ADEI_PASSWORD"])).content
                                    
                if python_version == 3:
                    data = data.decode("utf-8")
                                 
                if data == "":
                    logger.info(str(param) + ': Empty data!')
                    continue
                
                
                tmp_data = data.splitlines()[-1]
                if "ERROR" in tmp_data:
                    logger.error(str(param) + ': Query')
                    continue
                last_value = tmp_data.split(",")[-1].strip()
                first_value = tmp_data.split(",")[-2].strip()
                try:
                    test_x = float(last_value)
                except ValueError:
                    last_value = ""

                try:
                    time_buffer = first_value.split("-")
                    time_buffer[1] = str(months[time_buffer[1]])
                    first_value = "-".join(time_buffer)
                    first_ts = calendar.timegm(datetime.datetime.strptime(first_value, "%d-%m-%y %H:%M:%S.%f").timetuple())
                except:
                    first_ts = ""

                tmp_cache_data[param] = {'timestamp': first_ts, 'value': last_value}
            
                current_timestamp = strftime("%Y-%m-%d %H:%M:%S")
                cache_data['time'] = current_timestamp
                cache_data["adei"] = tmp_cache_data
        else:
            print("Other data source, do nothing: " + data_source)
       
    with open("./bora/.tmp.yaml", 'w') as stream_tmp:
        stream_tmp.write(yaml.dump(cache_data, default_flow_style=False))
    src_file = os.getcwd() + "/bora/.tmp.yaml"
    dst_file = os.getcwd() + "/bora/cache.yaml"
    shutil.copy(src_file, dst_file)
"""


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

"""
class StartHandler(tornado.web.RequestHandler):
    def get(self):
        try:
            rt.start()
            res = True
        except:
            res = False
        
        output = {
            "response": res,
            "http": "get",
            "action": "start-fetch",
            "time": str(datetime.datetime.now())
        }
        print(output)
        self.write(output)
"""

"""
class StopHandler(tornado.web.RequestHandler):
    def get(self):
        try:
            rt.stop()
            res = True
        except:
            res = False
        output = {
            "response": res,
            "http": "get",
            "action": "stop fetch",
            "time": str(datetime.datetime.now())
        }
        print(output)
        self.write(output)
"""

"""
class SetTimerHandler(tornado.web.RequestHandler):
    def get(self, duration):
        print ("Set interval")
        rt.setInterval(float(duration))
"""

class DesignerHandler(tornado.web.RequestHandler):
    def get(self):
        print("In designer mode.")
        with open("./bora/cache.yaml", 'r') as stream:
            try:
                cache_data = yaml.load(stream, Loader=yaml.Loader)
            except yaml.YAMLError as exc:
                print(exc)

        """
        # serialize data
        tmp_data = {}
        if cache_data:
            for data_source in cache_data:
                print(data_source)
                if data_source == "time":
                    tmp_data["time"] = cache_data["time"] 
                else:
                    print(data_source)
                    for param in cache_data[data_source]:
                        print(param)
                        tmp_data[param] = cache_data[data_source][param]
        """
        
        # check other data sources: rtsp or rest
        
        with open("style.yaml", 'r') as stream:
            try:
                style_data = yaml.load(stream, Loader=yaml.Loader)
            except yaml.YAMLError as exc:
                print(exc)
        

        # Prepare typedef yaml
        print(settings_data)
        
        typedef_data = {}
        for myitem in settings_data["plugins"]:
            tmp_data = None
            with open("./bora/typedef/" + str(myitem) + ".yaml", 'r') as stream:
                try:
                    tmp_data = yaml.load(stream, Loader=yaml.Loader)
                except yaml.YAMLError as exc:
                    print(exc)
            typedef_data[myitem] = tmp_data

        # TODO: add those non data type definitions e.g. Header, Calc 
        #print(typedef_data)


        
        index_data = None
        # intersect of cache file and style file
        if cache_data:
            if style_data:
                index_data = list(set(cache_data) | set(style_data))
            else:
                index_data = cache_data

        
        if index_data is not None:
            index_data = sorted(index_data)

        data = {
            "cache": cache_data,
            "style": style_data,
            "index": index_data, # variable list for the ADEI panel
            "rtsp": varname_data["rtsp"],
            "rest": varname_data["rest"],
            "adei": varname_data["adei"],
            "vardata": varname_data,
            "typedef": typedef_data
        }
        
        #print(typedef_data)

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
        print(response)
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
        print(response)
        self.write(response)


class SaveHandler(tornado.web.RequestHandler):

    def post(self):
        json_obj = json_decode(self.request.body)
        
        with open("style.yaml", 'wb') as output:
            output.write(yaml.safe_dump(json_obj,  encoding='utf-8',
                         allow_unicode=True, default_flow_style=False))
        response = {"success": "Data entry inserted."}


class StatusHandler(tornado.web.RequestHandler):
    def get(self):
        print( "In status mode.")
        with open("style.yaml", 'r') as stream:
            try:
                style_data = yaml.load(stream, Loader=yaml.Loader)
            except yaml.YAMLError as exc:
                print(exc)

        if not os.path.isfile("./bora/cache.yaml"): 
            print("BORA is loading data, please refresh the page again in a moment.")
            open("./bora/cache.yaml","wb")

        with open("./bora/cache.yaml", 'r') as vstream:
            try:
                cache_data = yaml.load(vstream, Loader=yaml.Loader)
            except yaml.YAMLError as exc:
                print(exc)

        data = {
            "style": style_data,
            "adei": varname_data["adei"],
            "cache": cache_data,
            "rtsp": varname_data["rtsp"],
            "rest": varname_data["rest"]
        }

        print("Status Handler")

        data["title"] = settings_data["title"]
        #data["server"] = os.environ["BORA_ADEI_SERVER"]
        data["version"] = BORA_VERSION

        self.render('status.html', data=data)

"""
class UpdateHandler(tornado.web.RequestHandler):
    def get(self):
        print( "Update Sensor Definition")
        new_data = {}
        rt.stop()
        with open("varname.yaml", 'r') as stream:
            try:
                cache_data = yaml.load(stream, Loader=yaml.Loader)
            except yaml.YAMLError as exc:
                print(exc)

        for item in cache_data:
            tmp_data = cache_data[item]
            tmp_str = []
            tmp_store = []
            for adei_unit in tmp_data.split("&"):
                lhs, rhs = adei_unit.split("=")
                if lhs == "db_mask":
                    tmp_str.append("db_mask=all")
                    continue
                elif lhs == "db_server":
                    db_server = rhs

                tmp_str.append(adei_unit)
                tmp_store.append(adei_unit)
            tmp_str.append("window=3600,-1")
            tmp_str.append("experiment=*-*")
            tmp_str.append("rt=full")
            tmp_str.append("cache=1")

            query = "&".join(tmp_str)
            dest = os.environ["BORA_ADEI_SERVER"] + 'services/getdata.php'
            url = dest + "?" + query

            data = requests.get(url, auth=(os.environ["BORA_ADEI_USERNAME"],
                                os.environ["BORA_ADEI_PASSWORD"]))
            cr = data.content
            cr = cr.split(",")

            match_token = item
            if db_server != "lara" and db_server != "hiu":
                # parameter name stored in ADEI with '-IST_Val' suffix
                if "MOD" in item:
                    match_token = item + "-MODUS_Val"
                elif "GRA" in item:
                    match_token = item + "-GRAD_Val"
                elif "RPO" in item:
                    match_token = item + "-ZUST_Val"
                elif "VYS" in item:
                    match_token = item + "-ZUST_Val"
                elif "MSS" in item:
                    match_token = item + "_Val"
                else:
                    match_token = item + "-IST_Val"

            db_mask = None
            for i, iter_item in enumerate(cr):
                if match_token == iter_item.strip():
                    db_mask = i - 1
            if db_mask is None:
                continue

            tmp_store.append("db_mask="+str(db_mask))

            new_data[item] = "&".join(tmp_store)

        with open("varname.yaml", 'wb') as output:
            output.write(yaml.dump(new_data, default_flow_style=False))
            response = {"success": "Data entry inserted."}

        rt.start()
"""


"""
class AdeiKatrinHandler(tornado.web.RequestHandler):
    def get(self, **params):
        sensor_name = str(params["sensor_name"])
        #{'db_group': u'320_KRY_Kryo_4K_CurLead',
        # 'db_name': u'ControlSystem_CPS',
        # 'sensor_name': u'320-RTP-8-1103',
        # 'db_server': u'cscps',
        # 'control_group': u'320_KRY_Kryo_3K'}
        dest = os.environ["BORA_ADEI_SERVER"] + 'services/getdata.php'
        query_cmds = []
        query_cmds.append("db_server="+str(params['db_server']))
        query_cmds.append("db_name="+str(params['db_name']))
        query_cmds.append("db_group="+str(params['db_group']))

        query_cmds.append("db_mask=all")
        query_cmds.append("window=3600,-1")
        query_cmds.append("experiment=*-*")
        query_cmds.append("rt=full")
        query_cmds.append("cache=1")

        query = "&".join(query_cmds)
        url = dest + "?" + query

        # get the db_masks
        # store the query command in varname

        data = requests.get(
            url,
            auth=(os.environ["BORA_ADEI_USERNAME"], 
                os.environ["BORA_ADEI_PASSWORD"])
        )
        
        cr = data.content
        
        if python_version == 3:
            cr = cr.decode("utf-8")
        
        cr = cr.splitlines()
        cr = ",".join(cr)
        cr = cr.split(",")

        # handling the inconsistency on naming convention
        match_token = params['sensor_name']
        if (params["db_server"] != "lara" and params["db_server"] != "hiu" and
                params["db_server"] != "safety-first"):
            # parameter name stored in ADEI with '-IST_Val' suffix
            if "MOD" in params['sensor_name']:
                match_token = params['sensor_name'] + "-MODUS_Val"
            elif "GRA" in params['sensor_name']:
                match_token = params['sensor_name'] + "-GRAD_Val"
            elif "RPO" in params['sensor_name']:
                match_token = params['sensor_name'] + "-ZUST_Val"
            elif "VYS" in params['sensor_name']:
                match_token = params['sensor_name'] + "-ZUST_Val"
            elif "HVS" in params['sensor_name']:
                match_token = params['sensor_name'] + "-ZUST_Val"
            elif "VAO" in params['sensor_name']:
                match_token = params['sensor_name'] + "-ZUST_Val"
            elif "MSS" in params['sensor_name']:
                match_token = params['sensor_name'] + "_Val"
            else:
                match_token = params['sensor_name'] + "-IST_Val"
            db_mask = None

        for i, item in enumerate(cr):
            if "[" and "]" in item.strip():
                lhs = re.match(r"[^[]*\[([^]]*)\]", item.strip()).groups()[0]
                if lhs == params['sensor_name']:
                    db_mask = i - 1
            else:
                if item.strip() == match_token:
                    db_mask = i - 1
        if db_mask is None:
            response = {"Error": "Cannot find variable on ADEI server."}
            self.write(response)
            return

        query_cmds = []
        query_cmds.append("db_server="+str(params['db_server']))
        query_cmds.append("db_name="+str(params['db_name']))
        query_cmds.append("db_group="+str(params['db_group']))

        query_cmds.append("db_mask="+str(db_mask))
        query = "&".join(query_cmds)

        # column name available
        # store in yaml file
        with open("varname.yaml", 'r') as stream:
            try:
                cache_data = yaml.load(stream, Loader=yaml.Loader)
            except yaml.YAMLError as exc:
                print(exc)

        if cache_data is None:
            cache_data = {}
            cache_data["adei"][sensor_name] = query
        else:
            if sensor_name not in cache_data:
                cache_data["adei"][sensor_name] = query
            else:
                response = {"Error":
                            "Variable already available in varname file."}
                self.write(response)
                return

        with open("varname.yaml", 'wb') as output:
            output.write(yaml.dump(cache_data, default_flow_style=False))
            response = {"success": "Data entry inserted."}

        self.write(response)
"""


class GetDataHandler(tornado.web.RequestHandler):
    def get(self):
        cache_data = None
        if not os.path.isfile("./bora/cache.yaml"): 
            print( "BORA is loading data, please refresh the page again in a moment.")
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
            print(data_source)
            if data_source == "time":
                tmp_data["time"] = cache_data["time"] 
            else:
                print(data_source)
                for param in cache_data[data_source]:
                    print(param)
                    tmp_data[param] = cache_data[data_source][param]
        self.write(tmp_data)


#print ("Running...")
#rt = RepeatedTimer(int(os.environ["BORA_POLLING"]), fetchDataADEI)


application = tornado.web.Application([
    (r"/version/?", VersionHandler), 
    (r"/list/?", ListHandler), # list sensors in cache
    #(r"/start/?", StartHandler), # start timer
    (r"/backup/?", BackupHandler), # save the varname and style yamls into backup folder
    #(r"/stop/?", StopHandler), # stop timer
    (r"/designer/?", DesignerHandler),
    (r"/", StatusHandler),
    (r"/save/?", SaveHandler), # save the style from frontend to backend yaml file
    #(r"/update/?", UpdateHandler), # update the cache file with the varname file
    (r"/getdata/?", GetDataHandler), # get data from cache file
    #(r"/timer/(?P<duration>[^\/]+)/?", SetTimerHandler)
    #(r"/add/adei/(?P<db_server>[^\/]+)/?"
    # "(?P<db_name>[^\/]+)/?(?P<db_group>[^\/]+)/?(?P<sensor_name>[^\/]+)?",
    # AdeiKatrinHandler)
], debug=True, static_path=os.path.join(root, 'static'),
    cookie_secret='L8LwECiNRxq2N0N2eGxx9MZlrpmuMEimlydNX/vt1LM=')


if __name__ == "__main__":
    application.listen(int(settings_data["port"]))
    tornado.autoreload.start()
    tornado.ioloop.IOLoop.instance().start()
