import requests
import os
import calendar
from datetime import date, datetime
from time import strptime


def Factory(parser):
 
    """Factory Method"""
    parsers = {
        "rest": RestParser,
        "adei": AdeiParser
    }
 
    return parsers[parser]()


class RestParser:
    """ parse the rest api response"""
    def __init__(self):
        pass

    def parse(self, url):
        """
        In [1]: import requests
        In [2]: r = requests.get("http://localhost:18080/api/v1/get-data/311-RBY-1-5052")
        In [3]: r.json()
        Out[3]:
            {'response': True,
             'value': 18,
             'parameter': '311-RBY-1-5052',
             'time': '2024-04-28 10:52:26.795386'}
        """
        r = requests.get(url)
        return { "value": r.json()['value'], "timestamp": r.json()['time'] }
 

class AdeiParser:
    """ parse the adei api response"""
    def __init__(self):
        pass

    def parse(self, url):
        data = requests.get(
            url,
            auth=(
                os.environ["BORA_ADEI_USERNAME"],
                os.environ["BORA_ADEI_PASSWORD"])
        ).content

        data = data.decode("utf-8")

        if data == "":
            print(': Empty data!')
            return None

        if "ERROR" in data.splitlines()[-1]:
            print("ERROR: : Query")
            return None

        tmp_data = data.splitlines()[-1]

        last_value = tmp_data.split(",")[-1].strip()
        first_value = tmp_data.split(",")[-2].strip()
        
        try:
            test_x = float(last_value)
        except ValueError:
            print("ERROR: : Last value is not a float 1")
            return None

        try:
            time_buffer = first_value.split("-")
            time_buffer[1] = str(strptime(time_buffer[1],'%b').tm_mon).zfill(2)
            first_value = "-".join(time_buffer)
            first_ts = calendar.timegm(datetime.strptime(first_value, "%d-%m-%y %H:%M:%S.%f").timetuple()) * 1000
        except:
            print("ERROR: : Last value is not a float 2")
            return None

        return {"timestamp": first_ts, "value": last_value}
