import json
from pprint import pprint
import os
import NFLProjections.NFLProjections.DB.NFL as DB
import NFLProjections.NFLProjections.Managers.DownloadManager as DM
import NFLProjections.NFLProjections.Environ as ENV
import re

filePath = "/home/ededub/FEFelson/NFLProjections/BoxScore/{}/{}/"
teamPath = "/home/ededub/FEFelson/NFLProjections/Teams/"


def safeValue(value):
    if value == "N/A":
        return 0
    elif ":" in value:
        return ".".join(value.split(":")[1:])
    elif "-" in value:
        return re.sub("-",".",value)
    else:
        return value


def rId(yahooId):
    if isinstance(yahooId, int) or yahooId == None:
        return yahooId
    return yahooId.split(".")[-1]

nflDB = DB.NFLDatabase()
nflDB.openDB()

dManager = DM.DownloadManager()

for teamId in [x.split(".")[0] for x in os.listdir(teamPath) if os.path.isfile(teamPath+x)]:
    dManager.getFiles("roster", teamId, True)
    if int(teamId) not in (-1,):
        filePath = ENV.getPath("roster", fileName=teamId)
        for playerId in ENV.getJsonInfo(filePath)["players"]:
            dManager.getFiles("player", playerId, True)

    
nflDB.closeDB()
