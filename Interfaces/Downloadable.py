import json

from abc import ABCMeta, abstractmethod
from bs4 import BeautifulSoup
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.request import urlopen, Request

## for Debugging
from pprint import pprint


def detachedDownload(url, attempts = 3, sleepTime = 10):
    """
    Recursive function to download yahoo url and isolate json
    Or write to errorFile
    """

    item = {}

    try:
        print("New Download\n{}\n".format(url))
        html = urlopen(url)
        for line in [x.decode("utf-8") for x in html.readlines()]:
            if "root.App.main" in line:
                item = json.loads(";".join(line.split("root.App.main = ")[1].split(";")[:-1]))
                item = item["context"]["dispatcher"]["stores"]

    except (URLError, HTTPError, ValueError) as e:
        if hasattr(e,'code'):
            print (e.code)
        if hasattr(e,'reason'):
            print (e.reason)
        if attempts:
            sleep(sleepTime)
            return self.downloadItem(attempts -1, sleepTime)
        pass
    # pprint(item)
    return item


################################################################################
################################################################################


class Downloadable(metaclass=ABCMeta):

    _url = None

    def __init__(self, *args, **kwargs):
        self.url = None


    @abstractmethod
    def parseData(self, data):
        pass


    @abstractmethod
    def setUrl(self, item=None):
        self.url = self._url


    def getUrl(self):
        return self.url


    def downloadItem(self, attempts = 3, sleepTime = 10):
        """
        Recursive function to download yahoo url and isolate json
        Or write to errorFile
        """

        item = {}

        try:
            print("New Download\n{}\n".format(self.url))
            html = urlopen(self.url)
            for line in [x.decode("utf-8") for x in html.readlines()]:
                if "root.App.main" in line:
                    item = json.loads(";".join(line.split("root.App.main = ")[1].split(";")[:-1]))
                    item = item["context"]["dispatcher"]["stores"]

        except (URLError, HTTPError, ValueError) as e:
            if hasattr(e,'code'):
                print (e.code)
            if hasattr(e,'reason'):
                print (e.reason)
            if attempts:
                sleep(sleepTime)
                return self.downloadItem(attempts -1, sleepTime)
            pass
        # pprint(item)
        return item
