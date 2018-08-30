import logging
import calendar
import datetime
import os
import re
import sys
import yaml
import time
import requests
import shutil
import tornado.ioloop
import tornado.web
import tornado.autoreload
from shutil import copyfile
from datetime import date
from time import gmtime, strftime
from tornado.escape import json_decode, json_encode, url_escape
from threading import Timer
import subprocess

root = os.path.dirname(__file__)

python_version = sys.version_info.major


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


def fetchDataADEI():

    with open("varname.yaml", 'r') as stream:
        try:
            varname = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    if varname is None:
        print("Error: Empty varname file.")
        return

    cache_data = {}
    curtime = int(time.time())
    time_image_range = str((curtime-3600)) + "-" + str(curtime)
    time_range = "3600,-1"
    for param in varname:
        dest = os.environ["BORA_ADEI_SERVER"] + 'services/getdata.php'
        url = dest + "?" + varname[param] + "&window=" + time_range + "&experiment=*-*&rt=full&cache=1"
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
            st_ts = ""

        cache_data[param] = {'timestamp': first_ts, 'value': last_value}
    
        current_timestamp = strftime("%Y-%m-%d %H:%M:%S")
        cache_data['time'] = current_timestamp
       
    with open("./bora/.tmp.yaml", 'w') as stream_tmp:
        stream_tmp.write(yaml.dump(cache_data, default_flow_style=False))
    src_file = os.getcwd() + "/bora/.tmp.yaml"
    dst_file = os.getcwd() + "/bora/cache.yaml"
    shutil.copy(src_file, dst_file)


class BaseHandler(tornado.web.RequestHandler):
    def get_current(self):
        return self.get_secure_cookie("user")


class ListHandler(tornado.web.RequestHandler):
    def get(self):
        with open("./bora/cache.yaml", 'r') as stream:
            try:
                response = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        if response is None:
            response = {"error": "No data entry."}
        self.write(response)


class StartHandler(tornado.web.RequestHandler):
    def get(self):
        print ("Start fetchData")
        rt.start()


class StopHandler(tornado.web.RequestHandler):
    def get(self):
        print ("Stop fetchData")
        rt.stop()


class SetTimerHandler(tornado.web.RequestHandler):
    def get(self, duration):
        print ("Set interval")
        rt.setInterval(float(duration))


class DesignerHandler(tornado.web.RequestHandler):
    def get(self):
        print("In designer mode.")
        with open("./bora/cache.yaml", 'r') as stream:
            try:
                cache_data = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        with open("style.yaml", 'r') as stream:
            try:
                style_data = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        if style_data:
            index_data = list(set(cache_data) | set(style_data))
        else:
            index_data = cache_data

        if index_data is not None:
            index_data = sorted(index_data)

        data = {
            "cache": cache_data,
            "style": style_data,
            "index": index_data,
        }

        data["title"] = os.environ["BORA_TITLE"]

        self.render('designer.html', data=data)


class VersionHandler(tornado.web.RequestHandler):
    def get(self):
        response = {'version': '1.0.0'}
        self.write(response)


class BackupHandler(tornado.web.RequestHandler):
    def post(self):
        backup_dst = os.getcwd() + "/backup/"
        fname = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        os.makedirs(backup_dst + fname)
        copyfile("varname.yaml", backup_dst +
                 fname + "/varname.yaml")
        copyfile("style.yaml", backup_dst +
                 fname + "/style.yaml")


class SaveHandler(tornado.web.RequestHandler):

    def post(self):
        json_obj = json_decode(self.request.body)
        
        with open("style.yaml", 'w') as output:
            output.write(yaml.safe_dump(json_obj,  encoding='utf-8',
                         allow_unicode=True, default_flow_style=False))
        response = {"success": "Data entry inserted."}


class StatusHandler(tornado.web.RequestHandler):
    def get(self):
        print( "In status mode.")
        with open("style.yaml", 'r') as stream:
            try:
                style_data = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        with open("varname.yaml", 'r') as vstream:
            try:
                varname_data = yaml.load(vstream)
            except yaml.YAMLError as exc:
                print(exc)

        if not os.path.isfile("./bora/cache.yaml"): 
            print("BORA is loading data, please refresh the page again in a moment.")
            open("./bora/cache.yaml","w")

        with open("./bora/cache.yaml", 'r') as vstream:
            try:
                cache_data = yaml.load(vstream)
            except yaml.YAMLError as exc:
                print(exc)

        data = {
            "style": style_data,
            "varname": varname_data,
            "cache": cache_data
        }

        data["title"] = os.environ["BORA_TITLE"]

        data["server"] = os.environ["BORA_ADEI_SERVER"]

        self.render('status.html', data=data)


class UpdateHandler(tornado.web.RequestHandler):
    def get(self):
        print( "Update Sensor Definition")
        new_data = {}
        rt.stop()
        with open("varname.yaml", 'r') as stream:
            try:
                cache_data = yaml.load(stream)
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

        with open("varname.yaml", 'w') as output:
            output.write(yaml.dump(new_data, default_flow_style=False))
            response = {"success": "Data entry inserted."}

        rt.start()


class AdeiKatrinHandler(tornado.web.RequestHandler):
    def get(self, **params):
        sensor_name = str(params["sensor_name"])
        """
        {'db_group': u'320_KRY_Kryo_4K_CurLead',
         'db_name': u'ControlSystem_CPS',
         'sensor_name': u'320-RTP-8-1103',
         'db_server': u'cscps',
         'control_group': u'320_KRY_Kryo_3K'}
        """
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
                cache_data = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        if cache_data is None:
            cache_data = {}
            cache_data[sensor_name] = query
        else:
            if sensor_name not in cache_data:
                cache_data[sensor_name] = query
            else:
                response = {"Error":
                            "Variable already available in varname file."}
                self.write(response)
                return

        with open("varname.yaml", 'w') as output:
            output.write(yaml.dump(cache_data, default_flow_style=False))
            response = {"success": "Data entry inserted."}

        self.write(response)


class GetDataHandler(tornado.web.RequestHandler):
    def get(self):
        cache_data = None
        if not os.path.isfile("./bora/cache.yaml"): 
            print( "BORA is loading data, please refresh the page again in a moment.")
            open("./bora/cache.yaml","w")
        with open("./bora/cache.yaml", 'r') as stream:
            try:
                cache_data = yaml.load(stream)
            except yaml.YAMLError as exc:
        
                print(exc)
        if cache_data is None:
            cache_data = {}
        self.write(cache_data)


print ("Running...")
rt = RepeatedTimer(int(os.environ["BORA_POLLING"]), fetchDataADEI)

application = tornado.web.Application([
    (r"/version/?", VersionHandler),
    (r"/list/?", ListHandler),
    (r"/start/?", StartHandler),
    (r"/backup/?", BackupHandler),
    (r"/stop/?", StopHandler),
    (r"/designer/?", DesignerHandler),
    (r"/", StatusHandler),
    (r"/save/?", SaveHandler),
    (r"/update/?", UpdateHandler),
    (r"/getdata/?", GetDataHandler),
    (r"/timer/(?P<duration>[^\/]+)/?", SetTimerHandler),
    (r"/add/(?P<db_server>[^\/]+)/?"
     "(?P<db_name>[^\/]+)/?(?P<db_group>[^\/]+)/?(?P<sensor_name>[^\/]+)?",
     AdeiKatrinHandler)
], debug=True, static_path=os.path.join(root, 'static'),
    cookie_secret='L8LwECiNRxq2N0N2eGxx9MZlrpmuMEimlydNX/vt1LM=')


if __name__ == "__main__":
    application.listen(int(os.environ["BORA_PORT"]))
    tornado.autoreload.start()
    tornado.ioloop.IOLoop.instance().start()
