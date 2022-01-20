from abc import ABCMeta, abstractmethod


## for Debugging
# from pprint import pprint



################################################################################
################################################################################


class Databasable(metaclass=ABCMeta):

    def __init__(self, *args, **kwargs):

        self.db = None
        self.setDB()


    @abstractmethod
    def setDB(self, db):
        self.db = db()
        self.db.openDB()
