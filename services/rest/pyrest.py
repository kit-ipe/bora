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
    "dma": {
        "resolution_x": 512,
        "resolution_y": 512,
        "num_images": 8,
        "bits_per_pixel": 8,
        "exposure_time": 1,
        "frame_rate": 30, 
        "gain": 2
    }
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


class RestHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")

    def options(self, **args):
        self.set_header("Access-Control-Allow-Methods", "*")
        self.set_header("Access-Control-Request-Credentials", "true")
        self.set_header("Access-Control-Allow-Private-Network", "true")
        self.set_header("Access-Control-Allow-Headers", "*")
        self.set_status(204)  # No Content

    def get(self, **params):
        # curl GET http://localhost:5617/api/v1/<group>/<parameter>
        device_group = str(params["group"])
        device_parameter = str(params["parameter"])
        
        # GET VALUE base on device_group and device_parameter
        # grabber.DevicePort.get("CameraControlMethod");
        res = LUT[device_group][device_parameter]
        
        self.write({
            "response": True,
            "value": res,
            "device_group": device_group,
            "device_parameter": device_parameter,
            "time": str(datetime.datetime.now())
        })
    def put(self, **params):
        # curl -X PUT http://localhost:5617/api/v1/<group>/<parameter>
        #   -H 'Content-Type: application/json'
        #   -d '{"value": "LIN2"}'
        device_group = str(params["group"])
        device_parameter = str(params["parameter"])
        
        data = tornado.escape.json_decode(self.request.body)
        LUT[device_group][device_parameter] = data["value"]

        # Update the value base on device_group and device_parameter
        # grabber.DevicePort.set("CameraControlMethod", "RC");
        
        self.write({
            "response": True,
            "device_group": device_group,
            "device_parameter": device_parameter,
            "time": str(datetime.datetime.now())
        })


application = tornado.web.Application([
    (r"/version/?", VersionHandler),
    (r"/api/v1/(?P<group>[^\/]+)/?"
     "(?P<parameter>[^\/]+)/?", RestHandler)
], debug=True)


if __name__ == "__main__":
    application.listen(5617)
    tornado.autoreload.start()
    tornado.ioloop.IOLoop.instance().start()
