from abc import ABCMeta, abstractmethod

class Databasable(metaclass=ABCMeta):

    @abstractmethod
    def getDB(self):
        pass


    @abstractmethod
    def getDBTable(self):
        pass


    @abstractmethod
    def getTableItems(self):
        pass


    @abstractmethod
    def getTablePK(self):
        pass


    @abstractmethod
    def getItemId(self):
        pass


    def getDBInfo(self):
        db = self.getDB()
        table = self.getDBTable()
        pk = self.getTablePK()
        items = self.getTableItems()
        itemId = self.getItemId()
        return zip(items, db.fetchOne("SELECT * FROM {} WHERE {} = ?".format(table, pk), (itemId,)))


    def updateDBInfo(self, **kwargs):
        db = self.getDB()
        table = self.getDBTable()
        pk = self.getTablePK()
        itemId = self.getItemId()
        db.update(table, pk, itemId, kwargs)


    def setDBInfo(self, *args):
        db = self.getDB()
        table = self.getDBTable()
        pk = self.getTablePK()
        itemId = self.getItemId()
        db.insert(table, pk, itemId, args)
