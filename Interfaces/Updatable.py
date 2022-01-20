from abc import ABCMeta, abstractmethod


## for Debugging
# from pprint import pprint



################################################################################
################################################################################


class Updatable(metaclass=ABCMeta):



    @abstractmethod
    def checkUpdate(self):
        pass


    @abstractmethod
    def determineUpdates(self):
        pass


    @abstractmethod
    def update(self):
        pass
