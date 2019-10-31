import MLBProjections.MLBProjections.Models.DownloadManager as DM
import MLBProjections.MLBProjections.Models.DatabaseManager as DBM
import MLBProjections.MLBProjections.Models.GameManager as GM
import MLBProjections.MLBProjections.DB.MLB as DB
import MLBProjections.MLBProjections.Environ as ENV
from MLBProjections.MLBProjections.Models.Umpire import Umpire
from MLBProjections.MLBProjections.Models.PA import PlateAppearance as PA

import datetime
import sqlite3
import json
import copy
from pprint import pprint


dm = DM.DownloadManager()
dm.update()
mlbDB = DB.MLBDatabase()
mlbDB.openDB()
mlbDB.update()
raise AssertionError




today = datetime.date.today()
with open(ENV.getLineupPath(today)) as fileIn:
    matchups = json.load(fileIn)["matchups"]

    for _ in range(2):

        for  i,matchup in enumerate(matchups):

       
    
            gameDB = DB.MLBGame(matchup["gameId"])

##                    gameDB.openDB()
##
##                    umpire = Umpire(gameDB)
##                    umpire.scoreKeeper.flipBook()
##
##                    batter = umpire.nextBatter()
##                    pitcher = umpire.getPitcher()
##
##                    PA(pitcher, batter, umpire)
##                    raise AssertionError
##
##                    gameDB.closeDB()
##
##                    raise AssertionError
##

                
            for n in range(200):

            


            
                GM.BaseballGame(gameDB)
            
