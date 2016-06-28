import os
import sys
import yaml
import requests
import shutil
from datetime import date
import csv
import urllib2
import re
import datetime
from shutil import copyfile
from time import gmtime, strftime


import tornado.escape
import tornado.ioloop
import tornado.web
import tornado.autoreload
from  tornado.escape import json_decode
from  tornado.escape import json_encode

from threading import Timer
import collections

root = os.path.dirname(__file__)

with open("config.yaml", 'r') as stream:
    try:
        #print(yaml.load(stream))
        config = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)
if config == None:
    print("Error: Empty configuration file.")
    sys.exit(1)


class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
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
    if os.path.isfile(config["path"]+".mutex"):
        #print("Process running...")
        return
    else:
        #print("Created mutex")
        file = open(config["path"]+'.mutex', 'w+')
    
    with open("varname.yaml", 'r') as stream:
        try:
            #print(yaml.load(stream))
            varname = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    if varname == None:
        print("Error: Empty varname file.")
    	os.remove(config["path"]+".mutex")
        return
    
    cache_data = {}
    for param in varname:
        print param
        dest = config['server'] + config['script']
        url = dest + "?" + varname[param] + "&window=-1"
        print url
        data = requests.get(url,
                            auth=(config['username'],
                                  config['password'])).content
        #tmp_data = data.content
        #print "CHECK THIS"
        #print data

        last_value = data.split(",")[-1].strip()
	try:
            print last_value
            test_x = float(last_value)
        except ValueError:
            last_value = ""
 	print last_value
        cache_data[param] = last_value
        #current_timestamp = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        current_timestamp = strftime("%Y-%m-%d %H:%M:%S")
        cache_data['time'] = current_timestamp

    with open(".tmp.yaml", 'w') as stream_tmp:
        stream_tmp.write(yaml.dump(cache_data, default_flow_style=False))
    src_file = config["path"] + ".tmp.yaml"
    dst_file = config["path"] + "cache.yaml"
    shutil.copy(src_file, dst_file)
    
    
    os.remove(config["path"]+".mutex")
    
    
"""
with open("config.yaml", 'r') as stream:
    try:
        #print(yaml.load(stream))
        config = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)
if config == None:
    print("Error: Empty configuration file.")
    sys.exit(1)
"""
    
print "Start torrenting..."
# it auto-starts, no need of rt.start()

print "Debugging..."
# TODO: Turn off for debug
rt = RepeatedTimer(config["polling"], fetchDataADEI)
    


class ListHandler(tornado.web.RequestHandler):
    def get(self):
        with open("cache.yaml", 'r') as stream:
            try:
                #print(yaml.load(stream))
                response = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        if response == None:
            response = {"error": "No data entry."}
        print response
        self.write(response)


class StartHandler(tornado.web.RequestHandler):
    def get(self):
        print "Start fetchData"
        rt.start()
        

class StopHandler(tornado.web.RequestHandler):
    def get(self):
        print "Stop fetchData"
        rt.stop()
        if os.path.isfile(config["path"]+".mutex"):
            os.remove(config["path"]+".mutex")


class SetTimerHandler(tornado.web.RequestHandler):
    def get(self, duration):
        print "Set interval"
        rt.setInterval(float(duration))



class DesignerHandler(tornado.web.RequestHandler):
    def get(self):
        print "In designer mode."
        with open("cache.yaml", 'r') as stream:
            try:
                #print(yaml.load(stream))
                cache_data = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        if cache_data == None:
            print("Error: Empty cache data file.")
            return
        
        print cache_data
        
        with open("style.yaml", 'r') as stream:
            try:
                #print(yaml.load(stream))
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
        print "Backup"
        print config["path"]
        backup_dst = config["path"] + "backup/"
        fname = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        os.makedirs(backup_dst + fname)
        copyfile(config["path"] + "varname.yaml", backup_dst + fname + "/varname.yaml")        
        copyfile(config["path"] + "style.yaml", backup_dst + fname + "/style.yaml")        
        #self.write(json.dumps(response))


class SaveHandler(tornado.web.RequestHandler):

    def post(self):
        print self.request.body
        json_obj = json_decode(self.request.body)
            
        print('Post data received')
        with open("style.yaml", 'w') as output:
            output.write(yaml.safe_dump(json_obj,  encoding='utf-8', allow_unicode=True, default_flow_style=False))
        response = {"success": "Data entry inserted."}
        #self.write(json.dumps(response))


class StatusHandler(tornado.web.RequestHandler):
    def get(self):
        print "In status mode."
        with open("style.yaml", 'r') as stream:
            try:
                #print(yaml.load(stream))
                style_data = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        if style_data == None:
            print("Error: Empty style data file.")
            return
        
	with open("varname.yaml", 'r') as vstream:
            try:
                #print(yaml.load(stream))
                varname_data = yaml.load(vstream)
            except yaml.YAMLError as exc:
                print(exc)
        if varname_data == None:
            print("Error: Empty varname data file.")
            return
        
	data = {
            "style": style_data,
            "varname": varname_data
        }
        self.render('status.html', data=data)


class AdeiKatrinHandler(tornado.web.RequestHandler):
    def get(self, **params):
        #print params
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
        
        
        #print config
        
        dest = config['server'] + config['script']
        query_cmds = []
        query_cmds.append("db_server="+str(params['db_server']))
        query_cmds.append("db_name="+str(params['db_name']))
        query_cmds.append("db_group="+str(params['db_group']))
        
        query_cmds.append("db_mask=all")
        query_cmds.append("window=-1")
        
        query = "&".join(query_cmds)
        url = dest + "?" + query

        #print url
        # get the db_masks
        # store the query command in varname
        
        data = requests.get(url, auth=(config['username'], config['password']))
        cr = data.content
        cr = cr.split(",")
        print cr, len(cr)
        
        # parameter name stored in ADEI with '-IST_Val' suffix
        if "MOD" in params['sensor_name']:
	    match_token = params['sensor_name'] + "-MODUS_Val"
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
        if db_mask == None:
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
                #print(yaml.load(stream))
                cache_data = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        #print "CHECK THIS"
        #print sensor_name, query
        #print cache_data
        if cache_data == None:
            cache_data = {}
            cache_data[sensor_name] = query
        else:
            if sensor_name not in cache_data:
                cache_data[sensor_name] = query
            else:
                response = {"Error": "Variable already available in varname file."}
                self.write(response)
                return
                
        with open("varname.yaml", 'w') as output:
            output.write(yaml.dump(cache_data, default_flow_style=False))
            response = {"success": "Data entry inserted."}
        
        #print match_token, db_mask
        self.write(response)
        
class GetDataHandler(tornado.web.RequestHandler):
    def get(self):
        with open("cache.yaml", 'r') as stream:
            try:
                #print(yaml.load(stream))
                cache_data = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        print("GetData:")
        if cache_data == None:
            cache_data = {}
        print cache_data
        self.write(cache_data) 


application = tornado.web.Application([
    (r"/version", VersionHandler),
    (r"/list", ListHandler),
    (r"/start", StartHandler),
    (r"/backup/", BackupHandler),
    (r"/stop", StopHandler),
    (r"/designer", DesignerHandler),
    (r"/status", StatusHandler),
    (r"/save/", SaveHandler),
    (r"/getdata/", GetDataHandler),
    (r"/timer/(?P<duration>[^\/]+)/?", SetTimerHandler),
    (r"/add/(?P<db_server>[^\/]+)/?(?P<db_name>[^\/]+)/?(?P<db_group>[^\/]+)/?(?P<sensor_name>[^\/]+)?", AdeiKatrinHandler)
], debug=True, static_path=os.path.join(root, 'static'), js_path=os.path.join(root, 'js'))
 

if __name__ == "__main__":
    application.listen(8888)
    tornado.autoreload.start()
    #tornado.autoreload.watch('myfile')
    tornado.ioloop.IOLoop.instance().start()
    
