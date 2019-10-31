from abc import ABCMeta, abstractmethod
from json import load, dump
from os import environ

class Fileable(metaclass=ABCMeta):

    @abstractmethod
    def getFilePath(self):
        return environ["HOME"] + "/FelsonSports"


    def readFile(self):
        filePath = self.getFilePath()
        with open(filePath) as fileIn:
            info = load(fileIn)
        return info


    def writeFile(self, info):
        filePath = self.getFilePath()
        with open(filePath, "w") as fileOut:
            dump(info, fileOut)
