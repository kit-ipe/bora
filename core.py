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
from datetime import date, datetime
from time import strftime
from tornado.escape import json_decode, json_encode, url_escape
from threading import Timer


root = os.path.dirname(__file__)

with open("config.yaml", 'r') as stream:
    try:
        config = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)
if config is None:
    print("Error: Empty configuration file.")
    sys.exit(1)


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
    time_range = "-1"
    for param in varname:
        dest = config['server'] + config['script']
        url = dest + "?" + varname[param] + "&window=" + time_range
        data = requests.get(url,
                            auth=(config['username'],
                                  config['password'])).content
        last_value = data.split(",")[-1].strip()
        try:
            test_x = float(last_value)
        except ValueError:
            last_value = ""
        cache_data[param] = last_value
        current_timestamp = strftime("%Y-%m-%d %H:%M:%S")
        cache_data['time'] = current_timestamp
        urlimage = (config['server'] + 'services/getimage.php' + "?" +
                    varname[param] + "&window=" + time_image_range +
                    "&frame_width=600&frame_height=400")
        image = requests.get(urlimage,
                             auth=(config['username'],
                                   config['password']))

        with open("static/dataimage/" + param + ".png", 'wb') as handle:
            for chunk in image.iter_content():
                handle.write(chunk)

    with open(".tmp.yaml", 'w') as stream_tmp:
        stream_tmp.write(yaml.dump(cache_data, default_flow_style=False))
    src_file = os.getcwd() + "/.tmp.yaml"
    dst_file = os.getcwd() + "/cache.yaml"
    shutil.copy(src_file, dst_file)


class BaseHandler(tornado.web.RequestHandler):
    def get_current(self):
        return self.get_secure_cookie("user")


class ListHandler(tornado.web.RequestHandler):
    def get(self):
        with open("cache.yaml", 'r') as stream:
            try:
                response = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        if response is None:
            response = {"error": "No data entry."}
        self.write(response)


class StartHandler(tornado.web.RequestHandler):
    def get(self):
        print "Start fetchData"
        rt.start()


class StopHandler(tornado.web.RequestHandler):
    def get(self):
        print "Stop fetchData"
        rt.stop()


class SetTimerHandler(tornado.web.RequestHandler):
    def get(self, duration):
        print "Set interval"
        rt.setInterval(float(duration))


class DesignerHandler(tornado.web.RequestHandler):
    @tornado.web.authenticated
    def get(self):
        print "In designer mode."
        with open("cache.yaml", 'r') as stream:
            try:
                cache_data = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        if cache_data is None:
            print("Error: Empty cache data file.")
            return

        with open("style.yaml", 'r') as stream:
            try:
                style_data = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        data = {
            "cache": cache_data,
            "style": style_data
        }

        self.render('designer.html', data=data)


class VersionHandler(tornado.web.RequestHandler):
    def get(self):
        response = {'version': '0.0.1',
                    'last_build': date.today().isoformat()}
        self.write(response)


class BackupHandler(tornado.web.RequestHandler):
    def post(self):
        backup_dst = os.getcwd() + "/backup/"
        fname = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        os.makedirs(backup_dst + fname)
        copyfile(os.getcwd() + "/varname.yaml", backup_dst +
                 fname + "/varname.yaml")
        copyfile(os.getcwd() + "/style.yaml", backup_dst +
                 fname + "/style.yaml")


class SaveHandler(tornado.web.RequestHandler):

    def post(self):
        print self.request.body
        json_obj = json_decode(self.request.body)

        print('Post data received')
        with open("style.yaml", 'w') as output:
            output.write(yaml.safe_dump(json_obj,  encoding='utf-8',
                         allow_unicode=True, default_flow_style=False))
        response = {"success": "Data entry inserted."}


class StatusHandler(tornado.web.RequestHandler):
    def get(self):
        print "In status mode."
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

        data = {
            "style": style_data,
            "varname": varname_data
        }

        if "background" in config:
            data["background"] = config["background"]

        if "title" in config:
            data["title"] = config["title"]
        else:
            data["title"] = "BORA"

        if "server" in config:
            data["server"] = config["server"]
        else:
            data["server"] = "http://katrin.kit.edu/adei-katrin/"

        self.render('status.html', data=data)


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
        if config["type"] != "adei":
            print("Error: Wrong handler.")
            return

        dest = config['server'] + config['script']
        query_cmds = []
        query_cmds.append("db_server="+str(params['db_server']))
        query_cmds.append("db_name="+str(params['db_name']))
        query_cmds.append("db_group="+str(params['db_group']))

        query_cmds.append("db_mask=all")
        query_cmds.append("window=-1")

        query = "&".join(query_cmds)
        url = dest + "?" + query

        # get the db_masks
        # store the query command in varname

        data = requests.get(url, auth=(config['username'], config['password']))
        cr = data.content
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
        with open("cache.yaml", 'r') as stream:
            try:
                cache_data = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        if cache_data is None:
            cache_data = {}
        self.write(cache_data)


class AuthLoginHandler(BaseHandler):
    def get(self):
        try:
            errormessage = self.get_argument("error")
        except:
            errormessage = ""
        print errormessage
        self.render("login.html", errormessage=errormessage)

    def check_permission(self, password, username):
        if (username == config["username"] and
                password == config["pw_designer"]):
            return True
        return False

    def post(self):
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")
        auth = self.check_permission(password, username)
        if auth:
            self.set_current_user(username)
            print "In designer mode."
            with open("cache.yaml", 'r') as stream:
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

            data = {
                "cache": cache_data,
                "style": style_data,
                "index": index_data,
            }

            if "background" in config:
                data["background"] = config["background"]

            self.render('designer.html', data=data)
        else:
            error_msg = (u"?error=" +
                         url_escape("Login incorrect"))
            self.redirect(u"/auth/login/" + error_msg)

    def set_current_user(self, user):
        if user:
            self.set_secure_cookie("user", tornado.escape.json_encode(user))
        else:
            self.clear_cookie("user")


print "Running..."
rt = RepeatedTimer(int(config["polling"]), fetchDataADEI)

application = tornado.web.Application([
    (r"/auth/login/?", AuthLoginHandler),
    (r"/version/?", VersionHandler),
    (r"/list/?", ListHandler),
    (r"/start/?", StartHandler),
    (r"/backup/?", BackupHandler),
    (r"/stop/?", StopHandler),
    (r"/designer/?", DesignerHandler),
    (r"/status/?", StatusHandler),
    (r"/save/?", SaveHandler),
    (r"/getdata/?", GetDataHandler),
    (r"/timer/(?P<duration>[^\/]+)/?", SetTimerHandler),
    (r"/add/(?P<db_server>[^\/]+)/?(?P<db_name>[^\/]+)/?"
     "(?P<db_group>[^\/]+)/?(?P<sensor_name>[^\/]+)?", AdeiKatrinHandler)
], debug=True, static_path=os.path.join(root, 'static'),
    js_path=os.path.join(root, 'js'), login_url="/auth/login",
    cookie_secret='L8LwECiNRxq2N0N2eGxx9MZlrpmuMEimlydNX/vt1LM=')


if __name__ == "__main__":
    application.listen(int(config["port"]))
    tornado.autoreload.start()
    tornado.ioloop.IOLoop.instance().start()
