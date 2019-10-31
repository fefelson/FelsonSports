from abc import ABCMeta, abstractmethod
from datetime import datetime


class Loggable(metaclass=ABCMeta):

    @abstractmethod
    def getLogPath(self):
        pass


    @abstractmethod
    def createErrorMsg(self):
        pass


    def writeErrorMsg(self, msg):
        """
        Writes error message to log file
        """
        formating = {"timestamp":datetime.today().timestamp(),
                        "msg":msg}
        logPath = self.getLogPath()
        print("Writing to Error File")
        with open(logPath, "a+") as logFile:
            print("{0[timestamp]}   {0[msg]}\n".format(formating))
            logFile.write("{0[timestamp]}\t{0[msg]}\n".format(formating))
