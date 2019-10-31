from abc import ABCMeta, abstractmethod
from datetime import datetime

class Updatable(metaclass=ABCMeta):

    def checkUpdate(self):
        if self.nextUpdate() != "N/A" and self.nextUpdate() >= datetime.today():
            self.update()


    @abstractmethod
    def nextUpdate(self):
        pass


    @abstractmethod
    def update(self):
        pass
