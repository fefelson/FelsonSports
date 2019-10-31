from abc import ABCMeta, abstractmethod


class Observer(metaclass=ABCMeta):

    @abstractmethod
    def update(self, info):
        pass


class Observable(metaclass=ABCMeta):

    def __init__(self):
        self.observedChange = False
        self.observers = []


    def registerObserver(self, observer):
        self.observers.append(observer)


    def removeObserver(self, observer):
        for i, obs in enumerate(self.observers):
            if obs == observer:
                self.observers.pop(i)
                break


    def setChanged(self):
        self.observedChange = True


    @abstractmethod
    def notifyObservers(self):
        self.observedChange = False


    @abstractmethod
    def isChanged(self, info):
        pass
