from SportsDB.Models.SportsManager import SportsManager
from SportsDB.WebService.ESPN.TeamParser import getRoster
import SportsDB.Environ as ENV
from SportsDB.DB.NBA import gameDateCmd
from json import load, dump
from datetime import date, timedelta
from itertools import chain
from os import environ
from pprint import pprint
import numpy



#############################################
sm = SportsManager()
nba = sm.getLeague("nba")
nba.databaseManager.openDB("fantasy")
nba.databaseManager.openDB("season")
db = nba.databaseManager.db["fantasy"]
seasonDB = nba.databaseManager.db["season"]
gameDate = date.today()#-timedelta(1)

############################################




mainPath = environ["HOME"] +"/FEFelson/NBA/BoxScores/{}/{}/{}/"
#fileNames = (mainPath +"P401071821.json", mainPath +"P401071822.json", mainPath +"P401071823.json", mainPath +"P401071824.json",)
#fileNames = (mainPath +"P401071819.json", mainPath +"P401071820.json", )
fileNames = (mainPath +"P401071827.json", )
fileNames  = (mainPath +"proj.json",) 

class Player:

    def __init__(self, gameId, info):

        self.gameId = gameId
        self.playerId = info["playerId"]
        self.name = info["name"]
        self.status = info["status"]
        try:
            self.price = db.curs.execute("SELECT price FROM dk_price AS pr INNER JOIN dk_players AS pl ON pr.dk_id = pl.dk_id WHERE game_id = ? AND espn_id = ?",(self.gameId, self.playerId)).fetchone()[0]
            self.pos = [x[0] for x in db.curs.execute("SELECT position FROM dk_positions AS pos INNER JOIN dk_players AS pl ON pos.dk_id = pl.dk_id WHERE game_id = ? AND espn_id = ?",(self.gameId, self.playerId)).fetchall()]
        except TypeError:
            self.price = -1
            self.pos=[]
        self.stats = self.setStats(info)
        self.scores = self.setScores()
        self.boxes = {"total":0, "3andUnder":0,"4":0,"5":0,"6":0,"7":0,"8":0, "9+":0}
        self.setBoxes()
        self.setAverages()

    def setAverages(self):
        totalBoxes = {"5":0,"6":0,"7":0,"8":0,"9":0}
        games = seasonDB.curs.execute("SELECT tpm, reb, ast, stl, blk, turn, points FROM player_stats AS stats INNER JOIN games ON stats.game_id = games.game_id WHERE season = 2019 AND player_id = ?", (self.playerId,)).fetchall()
        for game in games:
            gameScore = scoreGame(game)
            if gameScore >= int(self.price * 5 / 1000):
                totalBoxes["5"] += 1
            if gameScore >= int(self.price * 6 / 1000):
                totalBoxes["6"] += 1
            if gameScore >= int(self.price * 7 / 1000):
                totalBoxes["7"] += 1
            if gameScore >= int(self.price * 8 / 1000):
                totalBoxes["8"] += 1
            if gameScore >= int(self.price * 9 / 1000):
                totalBoxes["9"] += 1

        if len(games):
            totalBoxes["total"] = len(games)
        else:
            totalBoxes["total"] = 1
        
        self.averages = totalBoxes.copy()


    def setBoxes(self):
        for score in self.scores.values():
            self.boxes["3andUnder"] = self.boxes["3andUnder"] + 1
            if score/(self.price/1000) >= 4:
                self.boxes["4"] = self.boxes["4"] + 1
            if score/(self.price/1000) >= 5:
                self.boxes["5"] = self.boxes["5"] + 1
            if score/(self.price/1000) >= 6:
                self.boxes["6"] = self.boxes["6"] + 1
            if score/(self.price/1000) >= 7:
                self.boxes["7"] = self.boxes["7"] + 1
            if score/(self.price/1000) >= 8:
                self.boxes["8"] = self.boxes["8"] + 1
            if score/(self.price/1000) >= 9:
                self.boxes["9+"] = self.boxes["9+"] + 1
            self.boxes["total"] = self.boxes["total"] + 1
        if not self.boxes["total"]:
            self.boxes["total"] = 1
                


    def getScore(self, scoreType):
        if scoreType == "avg":
            return numpy.mean([x for x in self.scores.values()])

        if scoreType == "max":
            return max([x for x in self.scores.values()])

        if scoreType == "min":
            return min([x for x in self.scores.values()])

        
    def setScores(self):
        scores = {}
        for key in self.stats["points"]:
            if "start" in key:
                newScore = 0
                pts = self.stats["points"][key]
                thr = self.stats["3ptm"][key] * .5
                reb = (self.stats["oreb"][key]+self.stats["dreb"][key])*1.25
                ast = self.stats["ast"][key]*1.5
                if self.stats["stl"]:
                    stl = self.stats["stl"][key]*2
                else:
                    stl = 0
                if self.stats["blk"][key]:
                    blk = self.stats["blk"][key]*2
                else:
                    blk = 0
                trn = self.stats["turn"][key]*-.5

                total = 0
                for stat in (pts, reb, ast, stl, blk):
                    if stat == None:
                        stat = 0
                    if stat >= 10:
                        total += 1
                if total >= 2:
                    newScore += 1.5

                if total >=3:
                    newScore += 3

                for item in (pts,thr,reb,ast,stl,blk,trn):
                    newScore += item
                scores[key] = newScore
        return scores






    def setStats(self, info):
        stats = {}
        
        for stat in ("points", "oreb", "dreb", "ast", "stl", "blk", "3ptm", "turn"):
            stats[stat] = info["playerStats"][stat]["statAdj"]
##            pprint(info["playerStats"][stat])
        return stats


    def __str__(self):
        return "${}  {}    {}   ".format( str(self.price), str("/".join([x for x in self.pos if x not in ("UTIL", "G", "F")])), self.name)




def scoreGame(game):
    score =0
    pts = game[6]
    thr = game[0] * .5
    reb = game[1]*1.25
    ast = game[2]*1.5
    stl = game[3]*2
    blk = game[4]*2
    trn = game[5]*-.5

    total = 0
    for stat in (pts, reb, ast, stl, blk):
        if stat >= 10:
            total += 1
    if total >= 2:
        score += 1.5

    if total >=3:
        score += 3

    for item in (pts,thr,reb,ast,stl,blk,trn):
        score += item
    return score



if __name__ == "__main__":

    pList = {"PG":[], "SG":[], "SF":[], "PF":[], "C":[], "G":[], "F":[], "UTIL":[] }
    players = []

    matchups = []
    for fileName in fileNames:
        with open(fileName.format(*str(gameDate).split("-"))) as fileIn:
            proj = load(fileIn)
            for matchup in proj["matchups"]:
                matchups.append(matchup)
    

    for matchup in matchups:
        gameId = matchup["gameId"]
        for team in (matchup["homeTeam"], matchup["awayTeam"]):
            for player in chain(team["starters"], team["bench"]):
                players.append(Player(gameId, player))

    for player in players:
        for abrv in pList.keys():
            if abrv in player.pos:
                pList[abrv].append(player)



    nameLength = 25
    
    try:
        for abrv in pList.keys():
            print("\n\n\n")
            print(abrv.upper())
            pList[abrv] = sorted(pList[abrv], key=lambda x: [(x.averages["7"]/x.averages["total"])*(x.boxes["7"]/x.boxes["total"]), (x.averages["6"]/x.averages["total"])*(x.boxes["6"]/x.boxes["total"])] , reverse=True)
            for player in pList[abrv]:
                try:
                    print(player)                            
                    print()
                    print(round(player.getScore("min"),2), round(player.getScore("avg")), round(player.getScore("max"),2),)
                    print("\t{:d}pts    Five - {:d}%     {:d}%".format(int(player.price * 5 / 1000), int(player.boxes["5"]/player.boxes["total"]*100), int(player.averages["5"]/player.averages["total"]*100) ))
                    print("\t{:d}pts    Six - {:d}%     {:d}%".format(int(player.price * 6 / 1000), int(player.boxes["6"]/player.boxes["total"]*100), int(player.averages["6"]/player.averages["total"]*100) ))
                    print("\t{:d}pts    Seven - {:d}%     {:d}%".format(int(player.price * 7 / 1000), int(player.boxes["7"]/player.boxes["total"]*100), int(player.averages["7"]/player.averages["total"]*100) ))
                    print("\t{:d}pts    Eight - {:d}%     {:d}%".format(int(player.price * 8 / 1000), int(player.boxes["8"]/player.boxes["total"]*100), int(player.averages["8"]/player.averages["total"]*100) ))
                    print("\t{:d}pts    Nine - {:d}%     {:d}%".format(int(player.price * 9 / 1000), int(player.boxes["9+"]/player.boxes["total"]*100), int(player.averages["9"]/player.averages["total"]*100) ))
                    print("\n\n\n")
                except ZeroDivisionError:
                    pass
##            print("\nExpensive $8,000 - $11,000\n")
##            for player in pList[abrv]:
##                if player.getScore(decide)/(player.price/1000) >=4.9 and player.price/1000 >=8:
##                    print("{}".format(player.name).ljust(nameLength)+"{:.2f}   ${:,d}   {:.4f}".format(player.getScore(decide), player.price, player.getScore(decide)/(player.price/1000)))
##                    print("{}".format("").ljust(nameLength)+"{:.2f}\n".format(player.getScore(decide)))
##            print("\nMid-Level $5,000 - $7,999\n")
##            for player in pList[abrv]:
##                if player.getScore(decide)/(player.price/1000) >=4.9 and player.price/1000 >=5 and player.price/1000 < 8:
##                    print("{}".format(player.name).ljust(nameLength)+"{:.2f}   ${:,d}   {:.4f}".format(player.getScore(decide), player.price, player.getScore(decide)/(player.price/1000)))
##                    print("{}".format("").ljust(nameLength)+"{:.2f}\n".format(player.getScore(decide)))
##            print("\nCheap $3,000 - $4,999\n")
##            for player in pList[abrv]:
##                if player.getScore(decide)/(player.price/1000) >=4.9 and player.price/1000 <5:
##                    print("{}".format(player.name).ljust(nameLength)+"{:.2f}   ${:,d}   {:.4f}".format(player.getScore(decide), player.price, player.getScore(decide)/(player.price/1000)))
##                    print("{}".format("").ljust(nameLength)+"{:.2f}\n".format(player.getScore(decide)))
    except AttributeError:
        pass
    



    

            
