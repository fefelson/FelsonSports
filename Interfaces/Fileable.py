import json
import os

from abc import ABCMeta, abstractmethod


## for Debugging
# from pprint import pprint



################################################################################
################################################################################


class Fileable(metaclass=ABCMeta):

    _filePath = None

    def __init__(self, info=None, *args, **kwargs):
        self.filePath = None
        self.info = info


    @abstractmethod
    def create(self, default):
        pass


    def getFilePath(self):
        return self.filePath


    def getInfo(self):
        return self.info


    @abstractmethod
    def setFilePath(self):
        self.filePath = self._filePath


    def read(self):
        with open(self.filePath) as fileIn:
            temp = json.load(fileIn)
            for key in self.info.keys():
                    self.info[key] = temp[key]


    def write(self):
        try:
            os.makedirs("/".join(self.filePath.split("/")[:-1]))
        except FileExistsError:
            pass

        with open(self.filePath, 'w') as fileOut:
            json.dump(self.info, fileOut)
