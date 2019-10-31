from abc import ABCMeta, abstractmethod
from bs4 import BeautifulSoup
from json import loads
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.request import urlopen, Request


headers = {"Host": "sports.yahoo.com",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0",
            "Connection": "close",
            "Cache-Control": "max-age=0"}


class Downloadable(metaclass=ABCMeta):

    def downloadItem(self, attempts = 3, sleepTime = 10):
        """
        Recursive function to download yahoo url and isolate json
        Or write to errorFile
        """

        item = None
        url = self.getUrl()

        try:
            req = Request(url, headers=headers)
            html = urlopen(req)
            parser = BeautifulSoup(html,"lxml")

            for line in parser.text.split("\n"):
                if "root.App.main" in line:
                    item = loads(";".join(line.split("root.App.main = ")[1].split(";")[:-1]))

        except (URLError, HTTPError, IncompleteRead) as e:
            if hasattr(e,'code'):
                print (e.code)
            if hasattr(e,'reason'):
                print (e.reason)
            if attempts:
                sleep(sleepTime)
                return downloadItem(attempts -1, sleepTime)
            raise
        return item


    @abstractmethod
    def getUrl(self, **kwargs):
        pass


    @abstractmethod
    def parseData(self, data):
        pass
