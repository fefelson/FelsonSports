import os
import sqlite3
import unicodedata
import tarfile
import json
import shutil

from .. import Environ as ENV

from abc import ABCMeta, abstractmethod
from itertools import chain
from pprint import pprint

################################################################################
################################################################################


def yId(yahooId):
    try:
        return yahooId.split(".")[-1]
    except AttributeError:
        return "-1"


def normal(name):
    name = unicodedata.normalize("NFD", name)
    name = "".join(c for c in name if not unicodedata.combining(c))
    return name


checkTableCmd = "SELECT * FROM sqlite_master"
indexCmd = "CREATE INDEX idx_{} ON {} ({})"
updateCmd = "UPDATE {0[table]} SET {0[colCmd]} WHERE {0[pk]} = ?"


################################################################################
################################################################################


class DatabaseManager(metaclass=ABCMeta):
    """
        INPUTS ARE NOT VALIDATED HERE
    """

    _schema = None
    _dbPath = ENV.dbPath


    def __init__(self, dbPath):

        self.conn = None
        self.curs = None

        self.dbPath = dbPath
        if not os.path.exists(dbPath):
            os.makedirs("/".join(self.dbPath.split("/")[:-1]))
            self.openDB()
            self.create()
            self.seed()
            self.closeDB()


    def create(self):
        for line in self._schema:
            self.curs.execute(line)
        self.conn.commit()


    def openDB(self):
        self.conn = sqlite3.connect(self.dbPath)
        self.curs = self.conn.cursor()


    @abstractmethod
    def seed(self):
        pass


    @abstractmethod
    def insertGame(self, gameData):
        pass


    def checkEntry(self, table, item):
        pk = self.fetchOne("PRAGMA table_info({})".format(table))[1]
        cmd = "SELECT * FROM {} WHERE {} = {}".format(table, pk, item)
        self.curs.execute(cmd)
        answer = bool(self.curs.fetchone())
        return answer


    def closeDB(self):
        self.cursor.close()
        self.conn.close()


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


    def insert(self, table, *, colNames=None, info=None, values=None ):
        insertCmd = "INSERT INTO {0[table]} {0[cols]} VALUES( {0[qMarks]} )"
        if info:
            values = [info[col] for col in self.getTableCols(table) ]
        cols = "({})".format(",".join(colNames)) if colNames else ""
        qMarks = ",".join(["?" for x in values])
        self.executeCmd(insertCmd.format({"qMarks": qMarks, "table": table, "cols":cols}), values)


    def nextKey(self, table):
        pk = self.fetchOne("PRAGMA table_info({})".format(table))[1]
        keyCmd = "SELECT MAX({}) FROM {}".format(pk, table)
        try:
            key = int(self.fetchOne(keyCmd)[0]) + 1
        except TypeError:
            key = 1
        return key


    def getTableCols(self, table):
        return [x[1] for x in self.fetchAll("PRAGMA table_info({})".format(table))]


    def getKey(self, table, **kwargs):
        pk = self.fetchOne("PRAGMA table_info({})".format(table))[1]
        whereCmd = " AND ".join(["{}={}".format(key,value) for key, value in kwargs.items()])
        keyCmd = "SELECT {} FROM {} WHERE {}".format(pk, table, whereCmd)
        try:
            key = self.fetchOne(keyCmd)[0]
        except TypeError:
            key = self.nextKey(table)
            kwargs[pk] = key
            self.insert(table, info=kwargs)
        return key


    def update(self, table, pk, itemId, **kwargs):
        colCmd = ", ".join(["{} = {}".format(key, value) for key, value in kwargs.items()])
        cmd = updateCmd.format({"table":table, "colCmd":colCmd, "pk":pk})
        self.executeCmd(cmd, (itemId,))


    def insertPlayers(self):
        print("insertPlayers function")
        tar = tarfile.open("/home/ededub/FEFelson/{}/players.tar.xz".format(self._abrv))
        tar.extractall("/home/ededub/FEFelson/{}/temp".format(self._abrv))
        tar.close()

        for player in ["/home/ededub/FEFelson/{}/temp/".format(self._abrv)+ x for x in os.listdir("/home/ededub/FEFelson/{}/temp".format(self._abrv))]:
            print(player)
            with open(player) as fileIn:
                info = json.load(fileIn)
            self.insertPlayer(info)
        [os.remove("/home/ededub/FEFelson/{}/temp/".format(self._abrv)+ x) for x in os.listdir("/home/ededub/FEFelson/{}/temp".format(self._abrv))]



    def insertBoxScores(self):

        tar = tarfile.open("/home/ededub/FEFelson/{}/boxscores.tar.xz".format(self._abrv))
        tar.extractall("/home/ededub/FEFelson/{}/temp".format(self._abrv))
        tar.close()

        fileList = []
        for filePath, _, fileNames in os.walk("/home/ededub/FEFelson/{}/temp".format(self._abrv)):
            [fileList.append(filePath+"/"+fileName) for fileName in fileNames if fileName != "scoreboard.json" and fileName[0] != "M"]

        for filePath, _, fileNames in os.walk("/home/ededub/FEFelson/{}/{}".format(self._abrv, self._season)):
            [fileList.append(filePath+"/"+fileName) for fileName in fileNames if fileName != "scoreboard.json" and fileName != "schedule.json" and fileName[0] != "M"]

        for fileName in sorted(fileList, key=lambda x: int(x.split("/")[-1].split(".")[0])):
            print(fileName)
            with open(fileName) as fileIn:
                try:
                    self.insertGame(json.load(fileIn))
                except json.decoder.JSONDecodeError:
                    pass
        [shutil.rmtree("/home/ededub/FEFelson/{}/temp/".format(self._abrv)+ x) for x in os.listdir("/home/ededub/FEFelson/{}/temp".format(self._abrv))]




################################################################################
################################################################################
