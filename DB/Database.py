import os
import sqlite3

from abc import ABCMeta, abstractmethod
from itertools import chain
from pprint import pprint

################################################################################
################################################################################


checkTableCmd = "SELECT * FROM sqlite_master"
indexCmd = "CREATE INDEX idx_{} ON {} ({})"
insertCmd = "INSERT INTO {0[tableName]} VALUES( {0[qMarks]} )"
updateCmd = "UPDATE {0[table]} SET {0[colCmd]} WHERE {0[pk]} = ?"


################################################################################
################################################################################


class Database(metaclass=ABCMeta):
    """
        INPUTS ARE NOT VALIDATED HERE
    """

    def __init__(self, filePath):

        self.filePath = filePath

        self.conn = None
        self.curs = None
        self.isOpen = False


    def openDB(self):
        if not os.path.exists("/".join(self.filePath.split("/")[:-1])):
            os.makedirs("/".join(self.filePath.split("/")[:-1]))
        self.conn = sqlite3.connect(self.filePath)
        self.curs = self.conn.cursor()

        # If there are no tables
        if not self.fetchOne(checkTableCmd):
            # Create tables
            for table in self.getTableList():
                self.createTable(table)

            self.seed()
            self.commit()


    @abstractmethod
    def seed(self):
        pass


    def checkEntry(self, table, pk):
        cmd = "SELECT * FROM {} WHERE {} = {}".format(table.getName(), table.getPk(), pk)
        self.curs.execute(cmd)
        return bool(self.curs.fetchone())


    def closeDB(self):
        self.conn.close()


    def commit(self):
        self.conn.commit()


    def createTable(self, table):
        self.executeCmd(table.createTableCmd())
        for indexCmd in table.createIndexCmds():
            self.executeCmd(indexCmd)


    def drop(self, table):
        self.curs.execute("DROP TABLE {}".format(table.getName()))


    def executeCmd(self, cmd, values=[]):
        self.curs.execute(cmd, values)


    def fetchItem(self, cmd, values=[]):
        self.executeCmd(cmd, values)
        item = None
        try:
            item = self.curs.fetchone()[0]
        except TypeError:
            pass
        return item


    def fetchOne(self, cmd, values=[]):
        self.executeCmd(cmd, values)
        return self.curs.fetchone()


    def fetchAll(self, cmd, values=[]):
        self.executeCmd(cmd, values)
        return self.curs.fetchall()


    def insert(self, table, *, info=None, values=None):
        if not info and not values:
            raise AssertionError("info dict or values list/tuple must be provided")
        if not values:
            values = [info.get(key, None) for key in table.getCols()]
        qMarks = ",".join(["?" for col in table.getCols()])
        self.executeCmd(insertCmd.format({"qMarks": qMarks, "tableName": table.getName()}), values)


    def nextKey(self, table):
        keyCmd = "SELECT MAX({}) FROM {}".format(table.getPk(), table.getName())
        try:
            key = int(self.fetchOne(keyCmd)[0]) + 1
        except TypeError:
            key = 1
        return key


    def getKey(self, table, **kwargs):
        whereCmd = " AND ".join(["{}={}".format(key,value) for key, value in kwargs.items()])
        keyCmd = "SELECT {} FROM {} WHERE {}".format(table.getPk(), table.getName(), whereCmd)
        try:
            key = self.fetchOne(keyCmd)[0]
        except TypeError:
            key = self.nextKey(table)
            kwargs[table.getPk()] = key
            self.insert(table, info=kwargs)
        return key


    def update(self, table, pk, itemId, **kwargs):
        colCmd = ", ".join(["{} = {}".format(key, value) for key, value in kwargs.items()])
        cmd = updateCmd.format({"table":table, "colCmd":colCmd, "pk":pk})
        self.executeCmd(cmd, (itemId,))


################################################################################
################################################################################


class Table:

    def __init__(self, tableName):

        self.tableName = tableName
        self.pk = None
        self.tableCols = []
        self.tableCmds = []
        self.fk = []
        self.indexes = []


    def getName(self):
        return self.tableName


    def getPk(self):
        return self.pk


    def createIndexCmds(self):
        return [indexCmd.format(title,self.tableName,index) for title, index in self.indexes]


    def createTableCmd(self):
        colCmds = ", ".join(chain(self.tableCmds,self.fk))
        return "CREATE TABLE {} ( {} )".format(self.tableName, colCmds)


    def addPk(self, item, itemType):
        self.pk = item
        self.tableCmds.append("{} {} PRIMARY KEY".format(item, itemType))


    def multiPk(self, items):
        self.tableCmds.append("PRIMARY KEY ({})".format(items))


    def getCols(self):
        if self.pk:
            return [self.pk, *self.tableCols]
        else:
            return [*self.tableCols]


    def addCol(self, item, itemType, allowNull=False):
        nullValue = "NOT NULL" if not allowNull else ""
        self.tableCols.append(item)
        self.tableCmds.append("{} {} {}".format(item, itemType, nullValue))


    def addFk(self, item, table, key):
        self.tableCols.append(item)
        self.tableCmds.append("{} INT NOT NULL".format(item))
        self.fk.append("FOREIGN KEY ({}) REFERENCES {} ({})".format(item, table, key))


    def addIndex(self, name, sequence):
        self.indexes.append((name, sequence))
