import requests


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
        return r.json()['value']
 

class AdeiParser:
    """ parse the adei api response"""
    def __init__(self):
        pass

    def parse(self, url):
        """return one value"""
        return "adei"
