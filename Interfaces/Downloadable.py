import json

from abc import ABCMeta, abstractmethod
from bs4 import BeautifulSoup
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.request import urlopen, Request

## for Debugging
from pprint import pprint


headers = {
            "Host": "sports.yahoo.com",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Sec-GPC": "1",
            "Cache-Control": "max-age=0",
            "TE": "trailers"
        }


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
            req = Request(self.url, headers=headers)
            html = urlopen(req)
            parser = BeautifulSoup(html, features="html.parser")
            pprint(parser.text)
            for line in parser.text.split("\n"):
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
