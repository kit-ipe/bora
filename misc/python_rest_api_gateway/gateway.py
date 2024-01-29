import random
import logging
import calendar
import datetime
import os
import re
import sys
import yaml
import time
import requests
import tornado.ioloop
import tornado.web
import tornado.autoreload
from datetime import date
from time import gmtime, strftime
from tornado.escape import json_decode, json_encode, url_escape


root = os.path.dirname(__file__)


LUT = {
    "adei-data": {
        "311-RBY-1-5052": "http://localhost:18080/api/v1/get-data/311-rby-1-5052",
        "320-FLW-2-8010": "http://localhost:18080/api/v1/get-data/320-flw-2-8010"
    },
    "integer-to-string": {
        "311-RBY-1-5053": "http://localhost:18080/api/v1/get-data/311-rby-1-5053",
        "320-FLW-2-8011": "http://localhost:18080/api/v1/get-data/320-flw-2-8011"
    },
    "icon": {
        "311-RBY-1-5054": "http://localhost:18080/api/v1/get-data/311-rby-1-5054",
        "320-FLW-2-8012": "http://localhost:18080/api/v1/get-data/320-flw-2-8012"
    },
    "hls": {
        "camera01": "http://ipepdvcompute1.ipe.kit.edu:8000/streams/3cbaef0e4180012603286095abe01b67.m3u8"
    },
    "button": {
        "button01": "http://localhost:18080/api/v1/get-data/button01",
    },
    "rest": {
        "rest01": "http://localhost:18080/api/v1/get-data/rest01",
        "rest02": "http://localhost:18080/api/v1/get-data/rest02",
    }
}

mock_data = {
    "311-RBY-1-5052": "int_0_100",
    "320-FLW-2-8010": "int_0_100",
    "311-RBY-1-5053": "int_0_5",
    "320-FLW-2-8011": "int_0_5",
    "311-RBY-1-5054": "int_0_1",
    "320-FLW-2-8012": "int_0_1",
    "button01": "btn_str_pressed",
    "rest01": "rest_get_int_0_5_put_str_pressed",
    "rest02": "rest_get_int_0_5_put_str_pressed",
}



class VersionHandler(tornado.web.RequestHandler):
    def get(self):
        response = {
            "version": "1.0.0",
            "response": True,
            "action": "version",
            "time": str(datetime.datetime.now())
        }
        print(response)
        self.write(response)


class GetListHandler(tornado.web.RequestHandler):

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
    
    def options(self, *args):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_status(204)
        self.finish()

    def get(self, **params):
        # curl GET http://localhost:5617/api/v1/get-list/<type>
        data_type = str(params["type"])
        
        res = LUT[data_type]
        
        self.write({
            "response": True,
            "value": res,
            "data_type": data_type,
            "time": str(datetime.datetime.now())
        })

class GetDataHandler(tornado.web.RequestHandler):

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
    
    def options(self, *args):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_status(204)
        self.finish()

    def get(self, **params):
        # curl GET http://localhost:5617/api/v1/get-data/<name>
        parameter = str(params["name"])
        
        res = mock_data[parameter]
       
        # handle res parameter
        if res.startswith("int_"):
            mymin = int(res.split("_")[1])
            mymax = int(res.split("_")[2])
            res = random.randint(mymin,mymax)
        elif res.startswith("btn_"):
            res = random.choice(["pressed", "released"])
        elif res.startswith("rest_"):
            mymin = int(res.split("_")[3])
            mymax = int(res.split("_")[4])
            res = random.randint(mymin,mymax)
        else:
            res = "error"

        self.write({
            "response": True,
            "value": res,
            "parameter": parameter,
            "time": str(datetime.datetime.now())
        })


application = tornado.web.Application([
    (r"/version/?", VersionHandler),
    (r"/api/v1/get-list/(?P<type>[^\/]+)/?", GetListHandler),
    (r"/api/v1/get-data/(?P<name>[^\/]+)/?", GetDataHandler)
], debug=True)


if __name__ == "__main__":
    application.listen(18080)
    tornado.autoreload.start()
    tornado.ioloop.IOLoop.instance().start()
