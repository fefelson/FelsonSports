from abc import ABCMeta, abstractmethod

class Serializable(metaclass=ABCMeta):

    @abstractmethod
    def serialize(self):
        pass

    @abstractmethod
    def unserialize(self, info):
        pass
