from SportsDB.DB.NBA import gameDateCmd
from SportsDB.Models.SportsManager import SportsManager

from datetime import date, timedelta
import numpy
from pprint import pprint
from re import sub
from sqlite3 import IntegrityError
from sqlite3 import OperationalError

#################################################################################


gameDate = date.today()
yesterday = gameDate - timedelta(1)
twoWeeks = gameDate - timedelta(14)
sixWeeks = gameDate - timedelta(42)
seasonCmd = gameDateCmd(seasons=("2019",))
sixWeeksCmd = gameDateCmd(gameDates=(sixWeeks,gameDate))
twoWeeksCmd = gameDateCmd(gameDates=(twoWeeks,gameDate))


#################################################################################


timeFrameList = ("season", )#"sixWeeks", )#"twoWeeks", "season")
allHomeAway = ("home", "away", "all")


def getGDCmd(timeFrame):
    return {"season": seasonCmd, "sixWeeks": sixWeeksCmd, "twoWeeks": twoWeeksCmd}[timeFrame]


def getGICmd(gameTuple):
    giCmd = "stats.game_id"
    if gameTuple:
        giCmd += " IN "+str(gameTuple) if len(gameTuple) > 1 else " = "+str(gameTuple[0])
    else:
        giCmd+= " IN "+str(tuple())
    return giCmd


def getHACmd(homeAway):
    return {"home": homeCmd, "away": awayCmd, "all": allCmd }[homeAway]


def getOppCmd(teamTuple):
    teamCmd = "stats.opp_id"
    teamCmd += " IN "+str(teamTuple) if len(teamTuple) > 1 else " = "+str(teamTuple[0])
    return teamCmd


def getPlayerCmd(playerTuple):
    playerCmd = "stats.player_id"
    playerCmd += " IN "+str(playerTuple) if len(playerTuple) > 1 else " = "+str(playerTuple[0])
    return playerCmd

def getTeamCmd(teamTuple):
    teamCmd = "stats.team_id"
    teamCmd += " IN "+str(teamTuple) if len(teamTuple) > 1 else " = "+str(teamTuple[0])
    return teamCmd
    
 
allCmd = " stats.game_id = gd.game_id"
awayCmd = allCmd + " AND stats.team_id = gd.away_id"
homeCmd = allCmd + " AND stats.team_id = gd.home_id"


#################################################################################

baseBucketCmd = "SELECT stat_15, stat_85, stat_60, stat_40 FROM {0[bucketTable]}_totals WHERE stat_id = '{0[stat_id]}' AND proj_id = '{0[check_id]}' AND time_frame = '{0[time_frame]}' AND home_away = '{0[home_away]}' AND item_id = 'all'"
bucketCmd = "SELECT bucket FROM {0[bucketTable]}_buckets WHERE stat_id = '{0[stat_id]}' AND proj_id = '{0[proj_id]}' AND time_frame = '{0[time_frame]}' AND home_away = '{0[home_away]}' AND off_def = '{0[off_def]}' AND item_id = '{0[item_id]}'"
oppJoin = "INNER JOIN team_stats AS opp ON stats.game_id = opp.game_id AND stats.opp_id = opp.team_id"
posJoin = "INNER JOIN positions AS pos ON stats.game_id = pos.game_id AND stats.player_id = pos.player_id"
selectStatsCmd = "SELECT gd.mins, {0[selectCmd]} FROM {0[item_type]}_stats AS stats {0[oppJoin]}{0[posJoin]} INNER JOIN ({0[gdCmd]}) AS gd ON {0[haCmd]} {0[whereCmd]} {0[gbCmd]}" 
similarCmd = "SELECT DISTINCT item_id FROM {0[bucketTable]}_buckets WHERE stat_id = '{0[stat_id]}' AND proj_id = '{0[check_id]}' AND time_frame = '{0[time_frame]}' AND home_away = '{0[home_away]}' AND off_def = '{0[off_def]}' AND bucket = '{0[bucket]}'"
similarWhereCmd = "WHERE {0[itemCmd]} AND {0[oppCmd]}"

baseAvgCmd = "SELECT stat_avg FROM {0[bucketTable]}_totals WHERE proj_id = '{0[proj_id]}' AND stat_id = '{0[stat_id]}' AND time_frame = '{0[time_frame]}' AND home_away = '{0[home_away]}' AND item_id = '{0[item_id]}'"
allAvgCmd = "SELECT stat_avg FROM {0[bucketTable]}_totals WHERE proj_id = '{0[proj_id]}' AND stat_id = '{0[stat_id]}' AND time_frame = '{0[time_frame]}' AND home_away = '{0[home_away]}'"


teamNegotiateCmd = "SELECT num, stat_85, stat_60, stat_avg, stat_40, stat_15, stat_max, stat_min FROM team_totals WHERE stat_id = '{0[stat_id]}' AND proj_id = '{0[proj_id]}' AND time_frame = '{0[time_frame]}' AND home_away = '{0[home_away]}' AND off_def = '{0[off_def]}' AND item_id = {0[item_id]}"
        

#################################################################################


playerBucketTable = { "name": "player_buckets",

                     "columns": ("proj_id", "item_id", "stat_id", "time_frame",
                                 "home_away", "off_def", "bucket"),

                     "cmd": ("proj_id TEXT NOT NULL, item_id TEXT NOT NULL, "
                             "stat_id TEXT NOT NULL, time_frame TEXT NOT NULL, "
                             "home_away TEXT NOT NULL, off_def TEXT NOT NULL, "
                             "bucket TEXT NOT NULL, "
                             "PRIMARY KEY (proj_id, item_id, stat_id, time_frame, home_away, off_def), "
                             "FOREIGN KEY (item_id) REFERENCES pro_players (player_id)")
                     }


#----------------------------------------------


playerTotalsTable = { "name": "player_totals",

                     "columns": ("proj_id", "item_id", "stat_id", "time_frame",
                                 "home_away", "off_def", "num", "stat_avg",
                                 "stat_15", "stat_85", "stat_40",
                                 "stat_60", "stat_max", "stat_min"),

                     "cmd": ("proj_id TEXT NOT NULL, item_id TEXT NOT NULL, "
                             "stat_id TEXT NOT NULL, time_frame TEXT NOT NULL, "
                             "home_away TEXT NOT NULL, off_def TEXT NOT NULL, "
                             "num INT NOT NULL, stat_avg REAL NOT NULL, "
                             "stat_15 REAL NOT NULL, stat_85 REAL NOT NULL, "
                             "stat_40 REAL NOT NULL, stat_60 REAL NOT NULL, "
                             "stat_max REAL NOT NULL, stat_min REAL NOT NULL, "
                             "PRIMARY KEY (proj_id, item_id, stat_id, time_frame, home_away, off_def), "
                             "FOREIGN KEY (item_id) REFERENCES pro_players (player_id)")
                     }


#----------------------------------------------


teamBucketTable = { "name": "team_buckets",

                     "columns": ("proj_id", "item_id", "stat_id", "time_frame",
                                 "home_away", "off_def", "bucket"),

                     "cmd": ("proj_id TEXT NOT NULL, item_id TEXT NOT NULL, "
                             "stat_id TEXT NOT NULL, time_frame TEXT NOT NULL, "
                             "home_away TEXT NOT NULL, off_def TEXT NOT NULL, "
                             "bucket TEXT NOT NULL, "
                             "PRIMARY KEY (proj_id, item_id, stat_id, time_frame, home_away, off_def), "
                             "FOREIGN KEY (item_id) REFERENCES pro_teams (team_id)")
                     }


#----------------------------------------------


teamTotalsTable = { "name": "team_totals",

                     "columns": ("proj_id", "item_id", "stat_id", "time_frame",
                                 "home_away", "off_def", "num", "stat_avg",
                                 "stat_15", "stat_85", "stat_40",
                                 "stat_60", "stat_max", "stat_min"),

                     "cmd": ("proj_id TEXT NOT NULL, item_id TEXT NOT NULL, "
                             "stat_id TEXT NOT NULL, time_frame TEXT NOT NULL, "
                             "home_away TEXT NOT NULL, off_def TEXT NOT NULL, "
                             "num INT NOT NULL, stat_avg REAL NOT NULL, "
                             "stat_15 REAL NOT NULL, stat_85 REAL NOT NULL, "
                             "stat_40 REAL NOT NULL, stat_60 REAL NOT NULL, "
                             "stat_max REAL NOT NULL, stat_min REAL NOT NULL, "
                             "PRIMARY KEY (proj_id, item_id, stat_id, time_frame, home_away, off_def), "
                             "FOREIGN KEY (item_id) REFERENCES pro_teams (team_id)")
                     }


#----------------------------------------------


vsBucketTable = { "name": "vs_buckets",

                     "columns": ("proj_id", "item_id", "stat_id", "time_frame",
                                 "home_away", "off_def", "bucket"),

                     "cmd": ("proj_id TEXT NOT NULL, item_id TEXT NOT NULL, "
                             "stat_id TEXT NOT NULL, time_frame TEXT NOT NULL, "
                             "home_away TEXT NOT NULL, off_def TEXT NOT NULL, "
                             "bucket TEXT NOT NULL, "
                             "PRIMARY KEY (proj_id, item_id, stat_id, time_frame, home_away, off_def), "
                             "FOREIGN KEY (item_id) REFERENCES pro_teams (team_id)")
                     }


#----------------------------------------------


vsTotalsTable = { "name": "vs_totals",

                     "columns": ("proj_id", "item_id", "stat_id", "time_frame",
                                 "home_away", "off_def", "num", "stat_avg",
                                 "stat_15", "stat_85", "stat_40",
                                 "stat_60", "stat_max", "stat_min"),

                     "cmd": ("proj_id TEXT NOT NULL, item_id TEXT NOT NULL, "
                             "stat_id TEXT NOT NULL, time_frame TEXT NOT NULL, "
                             "home_away TEXT NOT NULL, off_def TEXT NOT NULL, "
                             "num INT NOT NULL, stat_avg REAL NOT NULL, "
                             "stat_15 REAL NOT NULL, stat_85 REAL NOT NULL, "
                             "stat_40 REAL NOT NULL, stat_60 REAL NOT NULL, "
                             "stat_max REAL NOT NULL, stat_min REAL NOT NULL, "
                             "PRIMARY KEY (proj_id, item_id, stat_id, time_frame, home_away, off_def), "
                             "FOREIGN KEY (item_id) REFERENCES pro_teams (team_id)")
                     }


#----------------------------------------------



tableList = (teamBucketTable, teamTotalsTable, playerBucketTable, playerTotalsTable, vsBucketTable, vsTotalsTable)

def createTempTables(db):
    for table in tableList:
        #print(table["name"])
        #TODO: TEMP TABLE
        createCmd = "CREATE TABLE IF NOT EXISTS {0[name]} (" + table["cmd"] + ")"
        db.curs.execute(createCmd.format({"name":table["name"]}))
        if table.get("index", None):
            indexCmd = "CREATE INDEX IF NOT EXISTS idx_{0[name]} ON {0[name]} (" + table["index"] + ")"
            db.curs.execute(indexCmd.format({"name":table["name"]}))
        db.conn.commit()


def dropTables(db):
    for table in tableList:
        dropCmd = "DROP TABLE IF EXISTS {0[name]} "
        db.curs.execute(dropCmd.format({"name":table["name"]}))
    db.conn.commit()


#################################################################################


def quantile(numList, pct):
    num = len(numList)
    index = int(pct*num)
    return sorted(numList)[index] 


#################################################################################


class Projection:

    def __init__(self, title, baseLineId, gameGroup, whereCmd):

        self.title = title
        self.projId = lambda item: self.title.format(item.getTitle())
        self.baseLineId = baseLineId
        self.gameGroup = gameGroup
        self.whereCmd = whereCmd


    def getBaseLine(self):
        return self.baseLineId


    def getCheckId(self):
        return self.baseLineId


    def getConstraints(self, homeConstraint):
        raise AssertionError


    def getGameGroup(self, item):
        return self.gameGroup(item)


    def getLabel(self, timeFrame, homeAway):
        return lambda item: "{}-".format(self.getProjId()(item))+"{}-{}".format(timeFrame, homeAway)


    def getProjId(self):
        return self.projId


    def getTitle(self):
        return self.title


    def getWhereCmd(self):
        return self.whereCmd


#----------------------------------------------


class PlayerProjection(Projection):

    def __init__(self, title, baseLineId="team_player", gameGroup=lambda x: None, whereCmd=lambda x: ""):
        super().__init__(title, baseLineId, gameGroup, whereCmd)


    def getConstraints(self, homeConstraint):
        homeAwayList = allHomeAway if not homeConstraint else ("all", homeConstraint)
        for timeFrame in timeFrameList:
            for homeAway in homeAwayList:
                yield (timeFrame, homeAway, "offense")


#----------------------------------------------


class TeamProjection(Projection):

    def __init__(self, title, baseLineId = "team", gameGroup=lambda x: None, whereCmd=lambda x: ""):
        super().__init__(title, baseLineId, gameGroup, whereCmd)


    def getConstraints(self, homeConstraint):
        homeAwayList = allHomeAway if not homeConstraint else ("all", homeConstraint)
        for timeFrame in timeFrameList:
            for homeAway in homeAwayList:
                for offDef in ("offense", "defense"):
                    yield (timeFrame, homeAway, offDef)


#----------------------------------------------


teamProj = TeamProjection("team", whereCmd=lambda itemId: "WHERE stats.team_id = {}".format(itemId)) 
lineupProj = TeamProjection("lineup", gameGroup=lambda team: team.getLineupGames(), whereCmd=lambda itemId, giCmd: "WHERE stats.team_id = {}".format(itemId) + " AND {}".format(giCmd))
teamMatchProj = TeamProjection("matchup_{}", gameGroup=lambda team: team.getMatchupGames(), whereCmd=lambda itemId, giCmd: "WHERE stats.team_id = {}".format(itemId) + " AND {}".format(giCmd))
teamB2bProj = TeamProjection("b2b_{}", gameGroup= lambda team: team.getB2bGames(), whereCmd=lambda itemId, giCmd: "WHERE stats.team_id = {}".format(itemId) + " AND {}".format(giCmd))
teamSimProj = TeamProjection("similar_{}")


#----------------------------------------------


playerProj = PlayerProjection("team_player")
playerLineupProj = PlayerProjection("lineup_player", gameGroup=lambda player: player.team.getLineupGames())
playerMatchProj = PlayerProjection("matchup_{}", gameGroup=lambda player: player.team.getMatchupGames(), whereCmd=lambda itemId, giCmd: "WHERE stats.player_id = {}".format(itemId) + " AND {}".format(giCmd))
playerB2bProj = PlayerProjection("b2b_{}", gameGroup= lambda player: player.team.getB2bGames(), whereCmd=lambda itemId, giCmd: "WHERE stats.player_id = {}".format(itemId) + " AND {}".format(giCmd))
playerSimProj = PlayerProjection("similar_{}")


#################################################################################
    

class Stat:

    StatDB = None

    def __init__(self, statId):

        self.statId = statId


    def SetDB(db):
        Stat.StatDB = db


    def SetTeamBaselines():
        print("SetTeamBaselines")
        raise AssertionError


    def SetPlayerBaseLine():
        pass
        
#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
    def calcItemList(self, itemList, formatting):
        formatting["num"] = len(itemList)

        if len(itemList) == 0:
            for item in ("stat_avg", "stat_min", "stat_15",
                          "stat_40", "stat_60", "stat_85", "stat_max"):
                formatting[item] = None

        elif len(itemList) == 1:
            for item in ("stat_avg","stat_min", "stat_15",
                          "stat_40", "stat_60", "stat_85", "stat_max"):
                formatting[item] = round(itemList[0], 4)

        else:
            for item, value in (("stat_avg", round(quantile(itemList, .5),4)),
                                ("stat_min", round(min(itemList), 4)),
                                ("stat_15", round(quantile(itemList, .15), 4)),
                                ("stat_40", round(quantile(itemList, .4), 4)),
                                ("stat_60", round(quantile(itemList, .6), 4)),
                                ("stat_85", round(quantile(itemList, .85), 4)),
                                ("stat_max", round(max(itemList), 4))):
                formatting[item] = value
       
        return formatting


    def computeGame(self, game):
        result = 0
        gameMins = game[0]
        stat = game[1]
        try:
            result = (stat/gameMins)*48
        except ZeroDivisionError:
            pass
        return result


    def crunchNumbers(self):
        raise AssertionError
    

    def getB2bGames(self):
        raise AssertionError


    def getB2bProj(self):
        raise AssertionError


    def getBaseBucketCmd(self):
        raise AssertionError


    def getBucketTable(self):
        raise AssertionError

    
    def getGameConditions(self, proj, itemId="all", haConstraint=None):
        conditionsLists = []
        for constraints in proj.getConstraints(haConstraint):
            timeFrame, homeAway, offDef = constraints
            conditions = {}
            for key, value in (("item_type", self.getItemType()),
                               ("item_id", itemId),
                               ("stat_id", self.statId),
                               # proj_id is a lambda?
                               ("proj_id", proj.getProjId()),
                               ("check_id", proj.getCheckId()),
                               ("time_frame", timeFrame),
                               ("home_away", homeAway),
                               ("off_def", offDef),
                               ("gdCmd", getGDCmd(timeFrame)),
                               ("haCmd", getHACmd(homeAway)),
                               # giCmd is a lambda
                               ("gameGroup", proj.getGameGroup(self.getItem())),
                               ("selectCmd", self.getSelectCmd(offDef)),
                               ("whereCmd", proj.getWhereCmd()),
                               ("gbCmd", ""),
                               ("oppJoin", oppJoin),
                               ("posJoin", ""),
                               # label is a lambda
                               ("label",proj.getLabel(timeFrame,homeAway)),
                               ):
                conditions[key] = value
            conditionsLists.append(conditions.copy())
        return conditionsLists


    def getItCmd(self):
        raise AssertionError


    def getItem(self):
        raise AssertionError


    def getItemId(self):
        raise AssertionError


    def getItemType(self):
        raise AssertionError


    def getJson(self):
        jsonDict = {"statId":self.statId,
                    "statProj":self.statProj
                    }        
        return jsonDict


    def getPlayerConditions(self, playerId=None):
        posList = ("","PG", "SG", "SF", "PF", "C")
        starterList = ("","0","1")
        if playerId:
            cmd = "SELECT DISTINCT position FROM positions AS pos INNER JOIN ("+seasonCmd+") AS gd ON pos.game_id = gd.game_id WHERE player_id = {}".format(playerId)
            posList = ["",]+[x[0] for x in self.db.curs.execute(cmd).fetchall() if x[0] in posList]
            cmd = "SELECT DISTINCT starter FROM player_stats AS stats INNER JOIN ("+seasonCmd+") AS gd ON stats.game_id = gd.game_id WHERE player_id = {}".format(playerId)
            starterList = ["",]+[str(x[0]) for x in self.db.curs.execute(cmd).fetchall() if str(x[0]) in starterList]
        for pos in posList:
            for starter in starterList:
                yield(pos, starter)


    def getProjections(self):
        raise AssertionError


    def getMatchupGames(self):
        raise AssertionError


    def getMatchProj(self):
        raise AssertionError

    
    def getNewBucket(self, formatting):
        
        bucket = "n/a"
    
        try:
            baseLow, baseHigh, base60, base40 = self.db.curs.execute(baseBucketCmd.format(formatting)).fetchone()
        except TypeError:
            print(baseBucketCmd.format(formatting))
            print()
            pprint(formatting)
            raise AssertionError
        statAvg = self.db.curs.execute(baseAvgCmd.format(formatting)).fetchone()
        #print(baseLow, baseHigh, base60, base40)
        try:
            statAvg = statAvg[0]
            if statAvg >= baseHigh:
                bucket = "a"
            elif statAvg >= base60:
                bucket = "b"
            elif statAvg >= base40:
                bucket = "c"
            elif statAvg >= baseLow:
                bucket = "d"
            else:
                bucket = "e"
                
            formatting["bucket"] = bucket
        except TypeError:
            formatting["bucket"] = bucket
        
        return formatting


    def getProjections(self):
        raise AssertionError


    def getSimGameConditions(self, proj, haConstraint=None):
        conditionsLists = []
        for constraints in proj.getConstraints(haConstraint):
            timeFrame, homeAway, offDef = constraints
            
            conditions = {}
            for key, value in (("item_type", self.getItemType()),
                               ("stat_id", self.statId),
                               ("proj_id", proj.getProjId()),
                               ("check_id", proj.getCheckId()),
                               ("time_frame", timeFrame),
                               ("home_away", homeAway),
                               ("gdCmd", getGDCmd(timeFrame)),
                               ("haCmd", getHACmd(homeAway)),
                               ("selectCmd", self.getSelectCmd(offDef)),
                               ("gbCmd",""),
                               ("oppJoin", oppJoin),
                               ("posJoin", ""),
                               ("label",proj.getLabel(timeFrame,homeAway))
                               ):
                conditions[key] = value
            if offDef == "offense":
                conditionsLists.append(conditions.copy())
        return conditionsLists


    def getSimProj(self):
        raise AssertionError


    def getStatId(self):
        return self.statId


    def getStatProj(self, label):
        return self.statProj[label]


    def getTotalsTable(self):
        raise AssertionError


    def insertResults(self, table, conditions):
        raise AssertionError
    

    def makeBuckets(self, proj):
        table = self.getTotalsTable()
        for conditions in self.getGameConditions(proj):
            conditions["proj_id"] = conditions["proj_id"](proj)
            conditions["label"] = conditions["label"](proj)
            conditions["bucketTable"] = "team"
            conditions["whereCmd"] = ""

            totals = [x[0] for x in self.db.curs.execute(allAvgCmd.format(conditions)).fetchall()]
            formatting = self.calcItemList(totals, conditions)
            try:
                self.db.insert(table, formatting)
            except IntegrityError:
                pass


    def makeVsBuckets(self, proj):
        for conditions in self.getGameConditions(proj):
            conditions["proj_id"] = conditions["proj_id"](proj)
            conditions["bucketTable"] = "vs"
            if conditions["off_def"] == "offense":
                for pos, start in self.getPlayerConditions():
                    vsConditions = conditions.copy()
                    vsConditions["pos"] = pos
                    vsConditions["start"] = start
                    vsConditions["off_def"] = "defense"
                    vsConditions["item_type"] = "player"
                    
                    posComponent = "_{}".format(pos) if pos else ""
                    startComponent = "_{}".format(start) if start else ""

                    vsConditions["proj_id"] = conditions["proj_id"]+"_vs_player"+posComponent+startComponent
                    vsConditions["label"] = vsConditions["proj_id"]+"-{}-{}".format(conditions["time_frame"], conditions["home_away"])
                    vsConditions["whereCmd"] = ""

                    totals = [x[0] for x in self.db.curs.execute(allAvgCmd.format(vsConditions)).fetchall()]
                    formatting = self.calcItemList(totals, vsConditions)

                    try:
                        self.db.insert(vsTotalsTable, formatting)
                    except IntegrityError:
                        pass    


    def negotiate(self, formatting):
        raise AssertionError


    def setB2bStats(self, proj):
        for conditions in self.getGameConditions(self.getB2bProj(), itemId=self.getItemId(), haConstraint=self.getItem().getHomeAway()):                            
            games = None
            conditions["proj_id"] = conditions["proj_id"](proj)
            conditions["label"] = conditions["label"](proj)
            if proj.getGameGroup(self.getItem()):
                games = tuple(set(proj.getGameGroup(self.getItem())).intersection(set(conditions["gameGroup"])))
            else:
                games = conditions["gameGroup"]
            conditions["whereCmd"] = conditions["whereCmd"](self.getItemId(), getGICmd(games))
            try:
                self.insertResults(self.getTotalsTable(), conditions)
            except OperationalError:
                pprint(conditions)
                print()
                pprint(selectStatsCmd.format(conditions))
                raise AssertionError


    def setB2bVsStats(self, proj):
        for conditions in self.getGameConditions(self.getB2bProj(), itemId=self.getItemId(), haConstraint=self.getItem().getHomeAway()):                            
            games = None

            conditions["proj_id"] = conditions["proj_id"](proj)

            
            if conditions["off_def"] == "offense":
                for pos, start in self.getPlayerConditions():
                    vsConditions = conditions.copy()
                    vsConditions["pos"] = pos
                    vsConditions["start"] = start
                    vsConditions["off_def"] = "defense"
                    vsConditions["oppJoin"] = ""
                    vsConditions["posJoin"] = posJoin
                    vsConditions["item_type"] = "player"
                    
                    posComponent = "_{}".format(pos) if pos else ""
                    startComponent = "_{}".format(start) if start else ""

                    vsConditions["proj_id"] = conditions["proj_id"]+"_vs_player"+posComponent+startComponent
                    vsConditions["check_id"] = conditions["check_id"] +"_vs_player"+posComponent+startComponent
                    vsConditions["label"] = vsConditions["proj_id"]+"-{}-{}".format(conditions["time_frame"], conditions["home_away"])

                    if proj.getGameGroup(self.getItem()):
                        games = tuple(set(proj.getGameGroup(self.getItem())).intersection(set(conditions["gameGroup"])))
                    else:
                        games = conditions["gameGroup"]


                    whereCmd = "WHERE stats.opp_id = {}".format(self.getItemId())
                    if pos:
                        if pos in ("PG","SG"):
                            whereCmd += " AND (position = '{}' OR position = 'G')".format(pos)
                        if pos in ("SF","PF"):
                            whereCmd += " AND (position = '{}' OR position = 'F')".format(pos)
                        else:
                            whereCmd += " AND position = '{}'".format(pos)
                    if start:
                        whereCmd += " AND starter = {}".format(start)

                    vsConditions["whereCmd"] = whereCmd + " AND " + getGICmd(conditions["gameGroup"])
                    
            
                    try:
                        self.insertResults(self.getTotalsTable(), vsConditions.copy())
                    except OperationalError:
                        pprint(vsConditions)
                        print()
                        pprint(selectStatsCmd.format(vsConditions))
                        raise AssertionError



    def setBaselineTendencies(self, proj):
        ##  For each team_id in database
        ##  item_type allows for players or teams
        for itemId in [x[0] for x in self.db.curs.execute("SELECT {0[item_type]}_id FROM pro_{0[item_type]}s".format({"item_type":self.getItemType()})).fetchall()]:
            for conditions in self.getGameConditions(proj, itemId=itemId):
                conditions["proj_id"] = conditions["proj_id"](proj)
                conditions["label"] = conditions["label"](proj)
                conditions["whereCmd"] = conditions["whereCmd"](itemId)
##                pprint(conditions)
##                raise AssertionError
                ##  Compile game stats offense/defense for every game teamId
                ##   played under these conditions
                try:
                    self.insertResults(self.getTotalsTable(), conditions)
                except OperationalError:
                    pprint(conditions)
                    print()
                    pprint(selectStatsCmd.format(conditions))
                    raise AssertionError


    def setBuckets(self, proj):
        ##  For each team_id in database
        ##  item_type allows for players or teams
        for itemId in [x[0] for x in self.db.curs.execute("SELECT {0[item_type]}_id FROM pro_{0[item_type]}s".format({"item_type":self.getItemType()})).fetchall()]:
            for conditions in self.getGameConditions(proj, itemId=itemId):
                conditions["proj_id"] = conditions["proj_id"](proj)
                conditions["label"] = conditions["label"](proj)
                conditions["bucketTable"] = "team"
                conditions["whereCmd"] = conditions["whereCmd"](itemId)                         
                formatting = self.getNewBucket(conditions)
                try:
                    self.db.insert(self.getBucketTable(), formatting)
                except IntegrityError:
                    pass


    def setDB(self, db):
        self.db = db


    def setLineupStats(self, proj):
        for conditions in self.getGameConditions(proj, itemId=self.getItemId(), haConstraint=self.getItem().getHomeAway()):
            conditions["bucketTable"] = "team"
            conditions["proj_id"] = conditions["proj_id"](proj)
            conditions["label"] = conditions["label"](proj)
            conditions["whereCmd"] = conditions["whereCmd"](self.getItemId(), getGICmd(conditions["gameGroup"]))
##            pprint(conditions)
            self.insertResults(self.getTotalsTable(), conditions)
            formatting = self.getNewBucket(conditions)
            try:
                self.db.insert(self.getBucketTable(), formatting)
            except IntegrityError:
                pass


    def setLineupVsStats(self, proj):
        for conditions in self.getGameConditions(proj, itemId=self.getItemId(), haConstraint=self.getItem().getHomeAway()):
            conditions["bucketTable"] = "vs"
            conditions["proj_id"] = conditions["proj_id"](proj)

            
            if conditions["off_def"] == "offense":
                for pos, start in self.getPlayerConditions():
                    vsConditions = conditions.copy()
                    vsConditions["pos"] = pos
                    vsConditions["start"] = start
                    vsConditions["off_def"] = "defense"
                    vsConditions["oppJoin"] = ""
                    vsConditions["posJoin"] = posJoin
                    vsConditions["item_type"] = "player"
                    
                    posComponent = "_{}".format(pos) if pos else ""
                    startComponent = "_{}".format(start) if start else ""

                    vsConditions["proj_id"] = conditions["proj_id"]+"_vs_player"+posComponent+startComponent
                    vsConditions["check_id"] = conditions["check_id"] +"_vs_player"+posComponent+startComponent
                    vsConditions["label"] = vsConditions["proj_id"]+"-{}-{}".format(conditions["time_frame"], conditions["home_away"])

                    whereCmd = "WHERE stats.opp_id = {}".format(self.getItemId())
                    if pos:
                        if pos in ("PG","SG"):
                            whereCmd += " AND (position = '{}' OR position = 'G')".format(pos)
                        if pos in ("SF","PF"):
                            whereCmd += " AND (position = '{}' OR position = 'F')".format(pos)
                        else:
                            whereCmd += " AND position = '{}'".format(pos)
                    if start:
                        whereCmd += " AND starter = {}".format(start)

                    vsConditions["whereCmd"] = whereCmd + " AND " + getGICmd(conditions["gameGroup"])

                    try:
                        self.insertResults(vsTotalsTable, vsConditions.copy())
                    except OperationalError:
                        pprint(vsConditions)
                        print()
                        pprint(selectStatsCmd.format(vsConditions))
                        raise AssertionError

                    formatting = self.getNewBucket(vsConditions)

                    try:
                        if formatting["bucket"] != "n/a":
                            self.db.insert(vsBucketTable, formatting)
                    except IntegrityError:
                        pass
            

    def setMatchupStats(self, proj):
        for conditions in self.getGameConditions(self.getMatchProj(), itemId=self.getItemId(), haConstraint=self.getItem().getHomeAway()):
            if conditions["off_def"] == "offense":
                games = None
                conditions["proj_id"] = conditions["proj_id"](proj)
                conditions["label"] = conditions["label"](proj)
                if proj.getGameGroup(self.getItem()):
                    games = tuple(set(proj.getGameGroup(self.getItem())).intersection(set(conditions["gameGroup"])))
                else:
                    games = conditions["gameGroup"]
                conditions["whereCmd"] = conditions["whereCmd"](self.getItemId(), getGICmd(games))
                try:
                    self.insertResults(self.getTotalsTable(), conditions)
                except OperationalError:
                    pprint(conditions)
                    print()
                    pprint(selectStatsCmd.format(conditions))
                    raise AssertionError


    def setSimilarStats(self, proj):
        for conditions in self.getSimGameConditions(self.getSimProj(), haConstraint=self.team.getHomeAway()):
            conditions["check_id"] = proj.getCheckId()
            conditions["bucketTable"] = "team"
            offConditions = conditions.copy()
            offConditions["proj_id"] = proj.getProjId()(proj)
            offConditions["off_def"] = "offense"
            offConditions["item_id"] = self.getItemId()
            
            defConditions = conditions.copy()
            if defConditions["home_away"] != "all":
                defConditions["home_away"] = "away" if conditions["home_away"] == "home" else "home"
            defConditions["proj_id"] = proj.getProjId()(proj)
            defConditions["off_def"] = "defense"
            defConditions["item_id"] = self.getItem().getOppId()

            try:
                offBucket = self.db.curs.execute(bucketCmd.format(offConditions)).fetchone()[0]
                offConditions["bucket"] = offBucket
                
                defBucket = self.db.curs.execute(bucketCmd.format(defConditions)).fetchone()[0]
                defConditions["bucket"] = defBucket

                
                offTeams = tuple([x[0] for x in self.db.curs.execute(similarCmd.format(offConditions)).fetchall() if x[0] != str(self.getItemId())]) 
                defTeams = tuple([x[0] for x in self.db.curs.execute(similarCmd.format(defConditions)).fetchall() if x[0] != str(self.team.getOppId())]) 


                teamCmd = getTeamCmd(offTeams)
                oppCmd = getOppCmd(defTeams)
                offConditions["proj_id"] = conditions["proj_id"](proj)
                offConditions["item_id"] = self.getItemId()
                offConditions["whereCmd"] = similarWhereCmd.format({"itemCmd":teamCmd, "oppCmd":oppCmd})
                
                # enter into team_totals
                self.insertResults(self.getTotalsTable(), offConditions)
                
                # make similar bucket 
                formatting = self.getNewBucket(offConditions)
                try:
                    # enter bucket into team_bucket
                    self.db.insert(teamBucketTable, formatting)
                except IntegrityError:
                    pass

                # similar defenses vs Offense team
                teamCmd = getTeamCmd((self.getItemId(),))
                oppCmd = getOppCmd(defTeams)
            
                offConditions["proj_id"] = "vs_"+conditions["proj_id"](proj)
                offConditions["whereCmd"] = similarWhereCmd.format({"itemCmd":teamCmd, "oppCmd":oppCmd})
                
                # enter into team_totals
                self.insertResults(self.getTotalsTable(), offConditions)

                # similar offenses vs Defense team
                teamCmd = getTeamCmd(offTeams)
                oppCmd = getOppCmd((self.team.getOppId(),))
                defConditions["proj_id"] = "vs_"+conditions["proj_id"](proj)
                defConditions["whereCmd"] = similarWhereCmd.format({"itemCmd":teamCmd, "oppCmd":oppCmd})
                # enter into team_totals
                self.insertResults(self.getTotalsTable(), defConditions)

            except TypeError:
                pass
            except IndexError:
                pass


    def setStatEst(self, formatting):
        raise AssertionError
   

    def setStats(self):
        raise AssertionError


###############################################


class TeamStat(Stat):

    TeamProjections = (teamProj, lineupProj)
                       
    def __init__(self, team, statId):
        self.team = team
        self.statProj = {}
        self.estTotal = {}
        super().__init__(statId)


    def crunchNumbers(self):
        for proj in self.getProjections():
            if not self.isBaselineSet(proj):

                print("Setting Team {} Baselines\n".format(self.statId))
                self.setBaselineTendencies(proj)
                self.makeBuckets(proj)
                self.setBuckets(proj)

                if self.getNewPlayerStat():
                    print("Setting VS {} Baselines\n".format(self.statId))
                    self.setVsBaseline(proj)
                    self.makeVsBuckets(proj)
                    self.setVsBuckets(proj)

                self.setBaseline(proj)

            if proj == lineupProj:
                self.setLineupStats(proj)
                if self.getNewPlayerStat():
                    self.setLineupVsStats(proj)

            if self.getMatchupGames():
                self.setMatchupStats(proj)

            if self.getB2bGames():
                self.setB2bStats(proj)
                if self.getNewPlayerStat():
                    self.setB2bVsStats(proj)

            self.setSimilarStats(proj)

        
    def getB2bGames(self):
        return self.team.getB2bGames()


    def getB2bProj(self):
        return teamB2bProj


    def getBucketTable(self):
        return teamBucketTable


    def getItem(self):
        return self.team


    def getItemId(self):
        return self.team.getTeamId()

    
    def getItemType(self):
        return "team"


    def getMatchupGames(self):
        return self.team.getMatchupGames()


    def getMatchProj(self):
        return teamMatchProj


    def getNewPlayerStat(self):
        raise AssertionError


    def getProjections(self):
        return TeamStat.TeamProjections


    def getSelectCmd(self, offDef):
        # {0} is filled with stats when on offense, opp when on defense
        formatting = ("stats", "opp") if offDef == "offense" else ("opp", "stats")
        cmd = ", ".join(self.getDesiredStats())
        return cmd.format(*formatting)


    def getSimProj(self):
        return teamSimProj


    def getTotalsTable(self):
        return teamTotalsTable


    def insertResults(self, table, conditions):
        #pprint(selectStatsCmd.format(conditions))
        totals = [self.computeGame(x) for x in self.db.curs.execute(selectStatsCmd.format(conditions)).fetchall()]
        #pprint(totals)
        ##  calculate num, min, 15qtr, 40qtr, avg, 60qtr, 85qtr, max of totals
        formatting = self.calcItemList(totals, conditions)
        if formatting["num"]:
            try:
                self.db.insert(table, formatting)
            except IntegrityError:
                pass


    def negotiate(self, formatting):
        # Initiate variables
        totals = []
        index = 3
        result = 0

##        print(formatting["label"])
        
        dFormatting = formatting.copy()
        dFormatting["item_id"] = self.team.getOppId()
        dFormatting["off_def"] = "defense"
        if dFormatting["home_away"] != "all":
            dFormatting["home_away"] = "away" if formatting["home_away"] == "home" else "home"

        teamResult = self.db.curs.execute(teamNegotiateCmd.format(formatting)).fetchone()
##        print(teamNegotiateCmd.format(formatting))
##        print("\n\nteamResult")
##        print(teamResult)
        

        oppResult =  self.db.curs.execute(teamNegotiateCmd.format(dFormatting)).fetchone()
##        print(teamNegotiateCmd.format(dFormatting))
##        print("\noppResult")
##        print(oppResult)


        matchFormat = formatting.copy()
        matchFormat["proj_id"] = "matchup_{}".format(formatting["proj_id"])
        matchResult = self.db.curs.execute(teamNegotiateCmd.format(matchFormat)).fetchone()
##        print(teamNegotiateCmd.format(matchFormat))
##        print("\nmatchResult")
##        print(matchResult)


        b2bFormat = formatting.copy()
        b2bFormat["proj_id"] = "b2b_{}".format(formatting["proj_id"])
        b2bResult = self.db.curs.execute(teamNegotiateCmd.format(b2bFormat)).fetchone()
##        print(teamNegotiateCmd.format(b2bFormat))
##        print("\nb2bResult")
##        print(b2bResult)


        b2bDFormat = dFormatting.copy()
        b2bDFormat["proj_id"] = "b2b_{}".format(formatting["proj_id"])
        b2bDResult = self.db.curs.execute(teamNegotiateCmd.format(b2bDFormat)).fetchone()
##        print(teamNegotiateCmd.format(b2bDFormat))
##        print("\nb2bDResult")
##        print(b2bDResult)


        simOffFormat = formatting.copy()
        simOffFormat["proj_id"] = "vs_similar_{}".format(formatting["proj_id"])
        simOffResult = self.db.curs.execute(teamNegotiateCmd.format(simOffFormat)).fetchone()
##        print(teamNegotiateCmd.format(simOffFormat))
##        print("\nsimOffResult")
##        print(simOffResult)


        simDefFormat = dFormatting.copy()
        simDefFormat["proj_id"] = "vs_similar_{}".format(formatting["proj_id"])
        simDefResult = self.db.curs.execute(teamNegotiateCmd.format(simDefFormat)).fetchone()
##        print(teamNegotiateCmd.format(simDefFormat))
##        print("\nsimDefResult")
##        print(simDefResult)



        simFormat = formatting.copy()
        simFormat["proj_id"] = "similar_{}".format(formatting["proj_id"])
        simResult = self.db.curs.execute(teamNegotiateCmd.format(simFormat)).fetchone()
##        print(teamNegotiateCmd.format(simFormat))
##        print("\nsimResult")
##        print(simResult)

        try:
            bucket = self.db.curs.execute(bucketCmd.format(simFormat)).fetchone()[0]
            index = {"a":1,"b":2,"c":3,"d":4,"e":5}[bucket]
##            print("\nindex-{}".format(index))
        except TypeError:
            pass
        except KeyError:
            pass
    
        if teamResult:
            totals.append(teamResult[index])

        if oppResult:
            totals.append(oppResult[index])

        if matchResult:
            totals.append(matchResult[index])

        if b2bResult:
            totals.append(b2bResult[index])

        if b2bDResult:
            totals.append(b2bDResult[index])

        if simResult:
            totals.append(simResult[index])

        if simOffResult:
            totals.append(simOffResult[index])

        if simDefResult:
            totals.append(simDefResult[index])

        if len(totals):
            result = numpy.mean(totals)

##        print("\nresult")
##        print(result)
##        print("\n"+("-"*50)+"\n")
        return result
                

    def setStats(self, proj):        
        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
            if conditions["off_def"] == "offense":
                conditions["proj_id"] = conditions["proj_id"](proj)
                conditions["label"] = conditions["label"](proj)
                
                label = conditions["label"]
                self.statProj[label] = round(self.negotiate(conditions))


    def setVsBaseline(self, proj):
        ##  For each team_id in database
        ##  item_type allows for players or teams
        for itemId in [x[0] for x in self.db.curs.execute("SELECT DISTINCT team_id FROM team_stats AS stats INNER JOIN ({0[gdCmd]}) AS gd ON stats.game_id = gd.game_id".format({"gdCmd": seasonCmd})).fetchall()[:100]]:
            for conditions in self.getGameConditions(proj, itemId=itemId):
                if conditions["off_def"] == "offense":
                    conditions["proj_id"] = conditions["proj_id"](proj)            
                    for pos, start in self.getPlayerConditions():
                        vsConditions = conditions.copy()
                        vsConditions["pos"] = pos
                        vsConditions["start"] = start
                        vsConditions["off_def"] = "defense"
                        vsConditions["oppJoin"] = ""
                        vsConditions["posJoin"] = posJoin
                        vsConditions["item_type"] = "player"
                        
                        posComponent = "_{}".format(pos) if pos else ""
                        startComponent = "_{}".format(start) if start else ""

                        vsConditions["proj_id"] = conditions["proj_id"]+"_vs_player"+posComponent+startComponent
                        vsConditions["label"] = vsConditions["proj_id"]+"-{}-{}".format(conditions["time_frame"], conditions["home_away"])

                        whereCmd = "WHERE stats.opp_id = {}".format(itemId)
                        if pos:
                            if pos in ("PG","SG"):
                                whereCmd += " AND (position = '{}' OR position = 'G')".format(pos)
                            if pos in ("SF","PF"):
                                whereCmd += " AND (position = '{}' OR position = 'F')".format(pos)
                            else:
                                whereCmd += " AND position = '{}'".format(pos)
                        if start:
                            whereCmd += " AND starter = {}".format(start)

                        vsConditions["whereCmd"] = whereCmd

                        ##  Compile offensive game stats for every player group where oppId = teamId
                        ##   played under these conditions
                        try:
                            self.insertResults(vsTotalsTable, vsConditions)
                        except OperationalError:
                            pprint(vsConditions)
                            print()
                            pprint(selectStatsCmd.format(vsConditions))
                            raise AssertionError


    def setVsBuckets(self, proj):
        ##  For each team_id in database
        ##  item_type allows for players or teams
        for itemId in [x[0] for x in self.db.curs.execute("SELECT DISTINCT team_id FROM team_stats AS stats INNER JOIN ({0[gdCmd]}) AS gd ON stats.game_id = gd.game_id".format({"gdCmd": seasonCmd})).fetchall()[:100]]:
             for conditions in self.getGameConditions(proj, itemId=itemId):
                if conditions["off_def"] == "offense":
                    conditions["bucketTable"] = "vs"
                    conditions["proj_id"] = conditions["proj_id"](proj)            
                    for pos, start in self.getPlayerConditions():
                        vsConditions = conditions.copy()
                        vsConditions["pos"] = pos
                        vsConditions["start"] = start
                        vsConditions["off_def"] = "defense"
                        
                        posComponent = "_{}".format(pos) if pos else ""
                        startComponent = "_{}".format(start) if start else ""

                        vsConditions["proj_id"] = conditions["proj_id"]+"_vs_player"+posComponent+startComponent
                        vsConditions["check_id"] = conditions["check_id"]+"_vs_player"+posComponent+startComponent
                        vsConditions["label"] = vsConditions["proj_id"]+"-{}-{}".format(conditions["time_frame"], conditions["home_away"])

                        whereCmd = "WHERE stats.opp_id = {}".format(itemId)
                        if pos:
                            if pos in ("PG","SG"):
                                whereCmd += " AND (position = '{}' OR position = 'G')".format(pos)
                            if pos in ("SF","PF"):
                                whereCmd += " AND (position = '{}' OR position = 'F')".format(pos)
                            else:
                                whereCmd += " AND position = '{}'".format(pos)
                        if start:
                            whereCmd += " AND starter = {}".format(start)

                        vsConditions["whereCmd"] = whereCmd
                    
                        formatting = self.getNewBucket(vsConditions)
                        try:
                            if formatting["bucket"] != "n/a":
                                self.db.insert(vsBucketTable, formatting)
                        except IntegrityError:
                            pass

        
    
#----------------------------------------------


class FtaPerFoul(TeamStat):

    baselineSet = []

    def __init__(self, team):
        super().__init__(team, "fta_per_foul")


    def computeGame(self, game):
        result = 0
        fta = game[1]
        oppFouls = game[2]
        try:
            result = fta/oppFouls
        except ZeroDivisionError:
            pass
        return result


    def getDesiredStats(self):
        return ("{0}.fta", "{1}.fouls" )


    def getNewPlayerStat(self):
        return None


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in FtaPerFoul.baselineSet


    def setBaseline(self, proj):
        FtaPerFoul.baselineSet.append(proj.getBaseLine())


    def setStats(self, proj):        
        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
            if conditions["off_def"] == "offense":
                conditions["proj_id"] = conditions["proj_id"](proj)
                conditions["label"] = conditions["label"](proj)
                
                label = conditions["label"]
                self.statProj[label] = self.negotiate(conditions)


#----------------------------------------------


class Possessions(TeamStat):

    baselineSet = []
    
    def __init__(self, team):
        super().__init__(team, "poss")


    def computeGame(self, game):
        result = 0
        gameMins = game[0]
        poss = sum(game[1:])
        try:
            result = (poss/gameMins)*48
        except ZeroDivisionError:
            pass
        return result


    def getDesiredStats(self):
        return ("{0}.fga", "{0}.turn", "{1}.fouls")


    def getNewPlayerStat(self):
        return None


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in Possessions.baselineSet


    def setBaseline(self, proj):
        Possessions.baselineSet.append(proj.getBaseLine())


#----------------------------------------------


class Team2ptAttempt(TeamStat):

    baselineSet = []

    def __init__(self, team):
        super().__init__(team, "2pta")


    def computeGame(self, game):
        result = 0
        gameMins = game[0]
        fga = game[1]
        tpa = game[2]
        try:
            result = ((fga-tpa)/gameMins)*48
        except ZeroDivisionError:
            pass
        return result


    def getDesiredStats(self):
        return ("{0}.fga", "{0}.tpa")


    def getNewPlayerStat(self):
        newStat = Player2ptAttempt(self)
        return newStat


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in Team2ptAttempt.baselineSet


    def setBaseline(self, proj):
        Team2ptAttempt.baselineSet.append(proj.getBaseLine())


    def setStats(self, proj):        
        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
            if conditions["off_def"] == "offense":
                conditions["proj_id"] = conditions["proj_id"](proj)
                conditions["label"] = conditions["label"](proj)
                
                label = conditions["label"]
                
                p,t,h = label.split("-")
                if h != "all":
                    h = "home" if h == "away" else "away"
                oppLabel = "-".join((p,t,h))
                
                poss = self.team.teamStats["poss"].getStatProj(label)
                turn = self.team.teamStats["turn"].getStatProj(label)
                fouls = self.team.matchup.getOpp(self.team).teamStats["fouls"].getStatProj(oppLabel)
                fga = poss - turn - fouls
            
                twoPerFga = self.team.teamStats["2pt_per_fga"].getStatProj(label)
                
                self.statProj[label] = round(fga * twoPerFga)

        
#----------------------------------------------


class Team2ptMade(TeamStat):

    baselineSet = []

    def __init__(self, team):
        super().__init__(team, "2ptm")


    def computeGame(self, game):
        result = 0
        gameMins = game[0]
        fgm = game[1]
        tpm = game[2]
        try:
            result = ((fgm-tpm)/gameMins)*48
        except ZeroDivisionError:
            pass
        return result


    def getDesiredStats(self):
        return ("{0}.fgm", "{0}.tpm")


    def getNewPlayerStat(self):
        newStat = Player2ptMade(self)
        return newStat


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in Team2ptMade.baselineSet


    def setBaseline(self, proj):
        Team2ptMade.baselineSet.append(proj.getBaseLine())


    def setStats(self, proj):        
        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
            if conditions["off_def"] == "offense":
                conditions["proj_id"] = conditions["proj_id"](proj)
                conditions["label"] = conditions["label"](proj)
                
                label = conditions["label"]
                
                #pprint(conditions)

                twoAtt = self.team.teamStats["2pta"].getStatProj(label)
                twoPct = self.team.teamStats["2pt_pct"].getStatProj(label)
                
                self.statProj[label] = round(twoAtt * twoPct)

        
#----------------------------------------------


class Team2ptPct(TeamStat):

    baselineSet = []

    def __init__(self, team):
        super().__init__(team, "2pt_pct")


    def computeGame(self, game):
        result = 0
        gameMins = game[0]
        fga = game[1]
        fgm = game[2]
        tpa = game[3]
        tpm = game[4]

        twoatt = fga-tpa
        twomad = fgm-tpm
        try:
            result = twomad/twoatt
        except ZeroDivisionError:
            pass
        return result


    def getDesiredStats(self):
        return ("{0}.fga", "{0}.fgm", "{0}.tpa", "{0}.tpm")


    def getNewPlayerStat(self):
        newStat = Player2ptPct(self)
        return newStat


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in Team2ptPct.baselineSet


    def setBaseline(self, proj):
        Team2ptPct.baselineSet.append(proj.getBaseLine())


    def setStats(self, proj):        
        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
            if conditions["off_def"] == "offense":
                conditions["proj_id"] = conditions["proj_id"](proj)
                conditions["label"] = conditions["label"](proj)
                
                label = conditions["label"]
                self.statProj[label] = self.negotiate(conditions)

        
#----------------------------------------------


class Team2ptPerFga(TeamStat):

    baselineSet = []

    def __init__(self, team):
        super().__init__(team, "2pt_per_fga")


    def computeGame(self, game):
        result = 0
        gameMins = game[0]
        fga = game[1]
        tpa = game[2]
        try:
            result = (fga-tpa)/fga
        except ZeroDivisionError:
            pass
        return result


    def getDesiredStats(self):
        return ("{0}.fga", "{0}.tpa")


    def getNewPlayerStat(self):
        return None


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in Team2ptPerFga.baselineSet


    def setBaseline(self, proj):
        Team2ptPerFga.baselineSet.append(proj.getBaseLine())


    def setStats(self, proj):        
        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
            if conditions["off_def"] == "offense":
                conditions["proj_id"] = conditions["proj_id"](proj)
                conditions["label"] = conditions["label"](proj)
                
                label = conditions["label"]
                self.statProj[label] = self.negotiate(conditions)

        
#----------------------------------------------


class Team3ptAttempt(TeamStat):

    baselineSet = []

    def __init__(self, team):
        super().__init__(team, "3pta")


    def getDesiredStats(self):
        return ("{0}.tpa",)


    def getNewPlayerStat(self):
        newStat = Player3ptAttempt(self)
        return newStat


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in Team3ptAttempt.baselineSet


    def setBaseline(self, proj):
        Team3ptAttempt.baselineSet.append(proj.getBaseLine())


    def setStats(self, proj):        
        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
            if conditions["off_def"] == "offense":
                conditions["proj_id"] = conditions["proj_id"](proj)
                conditions["label"] = conditions["label"](proj)
                
                label = conditions["label"]
                

                p,t,h = label.split("-")
                if h != "all":
                    h = "home" if h == "away" else "away"
                oppLabel = "-".join((p,t,h))
                
                poss = self.team.teamStats["poss"].getStatProj(label)
                turn = self.team.teamStats["turn"].getStatProj(label)
                fouls = self.team.matchup.getOpp(self.team).teamStats["fouls"].getStatProj(oppLabel)
                fga = poss - turn - fouls
            
                threePerFga = self.team.teamStats["3pt_per_fga"].getStatProj(label)
                
                self.statProj[label] = round(fga * threePerFga)

        
#----------------------------------------------


class Team3ptMade(TeamStat):

    baselineSet = []

    def __init__(self, team):
        super().__init__(team, "3ptm")


    def getDesiredStats(self):
        return ("{0}.tpm", )


    def getNewPlayerStat(self):
        newStat = Player3ptMade(self)
        return newStat


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in Team3ptMade.baselineSet


    def setBaseline(self, proj):
        Team3ptMade.baselineSet.append(proj.getBaseLine())


    def setStats(self, proj):        
        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
            if conditions["off_def"] == "offense":
                conditions["proj_id"] = conditions["proj_id"](proj)
                conditions["label"] = conditions["label"](proj)
                
                label = conditions["label"]
                

                threeAtt = self.team.teamStats["3pta"].getStatProj(label)
                threePct = self.team.teamStats["3pt_pct"].getStatProj(label)
                
                self.statProj[label] = round(threeAtt * threePct)

        
#----------------------------------------------


class Team3ptPct(TeamStat):

    baselineSet = []

    def __init__(self, team):
        super().__init__(team, "3pt_pct")


    def computeGame(self, game):
        result = 0
        gameMins = game[0]
        tpa = game[1]
        tpm = game[2]
        
        try:
            result = tpm/tpa
        except ZeroDivisionError:
            pass
        return result


    def getDesiredStats(self):
        return ("{0}.tpa", "{0}.tpm")


    def getNewPlayerStat(self):
        newStat = Player3ptPct(self)
        return newStat


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in Team3ptPct.baselineSet


    def setBaseline(self, proj):
        Team3ptPct.baselineSet.append(proj.getBaseLine())


    def setStats(self, proj):        
        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
            if conditions["off_def"] == "offense":
                conditions["proj_id"] = conditions["proj_id"](proj)
                conditions["label"] = conditions["label"](proj)
                
                label = conditions["label"]
                self.statProj[label] = self.negotiate(conditions)

        
#----------------------------------------------


class Team3ptPerFga(TeamStat):

    baselineSet = []

    def __init__(self, team):
        super().__init__(team, "3pt_per_fga")


    def computeGame(self, game):
        result = 0
        gameMins = game[0]
        fga = game[1]
        tpa = game[2]
        try:
            result = tpa/fga
        except ZeroDivisionError:
            pass
        return result


    def getDesiredStats(self):
        return ("{0}.fga", "{0}.tpa")


    def getNewPlayerStat(self):
        return None


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in Team3ptPerFga.baselineSet


    def setBaseline(self, proj):
        Team3ptPerFga.baselineSet.append(proj.getBaseLine())


    def setStats(self, proj):        
        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
            if conditions["off_def"] == "offense":
                conditions["proj_id"] = conditions["proj_id"](proj)
                conditions["label"] = conditions["label"](proj)
                
                label = conditions["label"]
                self.statProj[label] = self.negotiate(conditions)


#----------------------------------------------


class TeamAssists(TeamStat):

    baselineSet = []

    def __init__(self, team):
        super().__init__(team, "ast")


    def getDesiredStats(self):
        return ("{0}.ast", )


    def getNewPlayerStat(self):
        newStat = PlayerAssists(self)
        return newStat


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in TeamAssists.baselineSet


    def setBaseline(self, proj):
        TeamAssists.baselineSet.append(proj.getBaseLine())


    def setStats(self, proj):        
        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
            if conditions["off_def"] == "offense":
                conditions["proj_id"] = conditions["proj_id"](proj)
                conditions["label"] = conditions["label"](proj)
                
                label = conditions["label"]
                
                    
                astPer = self.team.teamStats["ast_per_fgm"].getStatProj(label)
                fgm = self.team.teamStats["fgm"].getStatProj(label)
                
                self.statProj[label] = round(fgm * astPer)



#----------------------------------------------


class TeamAssistsPerFgm(TeamStat):

    baselineSet = []

    def __init__(self, team):
        super().__init__(team, "ast_per_fgm")


    def computeGame(self, game):
        result = 0
        gameMins = game[0]
        ast = game[1]
        fgm = game[2]
        try:
            result = ast/fgm
        except ZeroDivisionError:
            pass
        return result


    def getDesiredStats(self):
        return ("{0}.ast", "{0}.fgm")


    def getNewPlayerStat(self):
        return None


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in TeamAssistsPerFgm.baselineSet


    def setBaseline(self, proj):
        TeamAssistsPerFgm.baselineSet.append(proj.getBaseLine())


    def setStats(self, proj):        
        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
            if conditions["off_def"] == "offense":
                conditions["proj_id"] = conditions["proj_id"](proj)
                conditions["label"] = conditions["label"](proj)
                
                label = conditions["label"]
                self.statProj[label] = self.negotiate(conditions)


#----------------------------------------------


class TeamBlocks(TeamStat):

    baselineSet = []

    def __init__(self, team):
        super().__init__(team, "blk")


    def getDesiredStats(self):
        return ("{0}.blk", )


    def getNewPlayerStat(self):
        newStat = PlayerBlocks(self)
        return newStat


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in TeamBlocks.baselineSet


    def setBaseline(self, proj):
        TeamBlocks.baselineSet.append(proj.getBaseLine())


    def setStats(self, proj):        
        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
            if conditions["off_def"] == "offense":
                conditions["proj_id"] = conditions["proj_id"](proj)
                conditions["label"] = conditions["label"](proj)
                
                label = conditions["label"]
                
                    
                p,t,h = label.split("-")
                if h != "all":
                    h = "home" if h == "away" else "away"
                oppLabel = "-".join((p,t,h))

                blkPer = self.team.teamStats["blk_per_fga"].getStatProj(label)
                fga = self.team.matchup.getOpp(self.team).teamStats["fga"].getStatProj(oppLabel)
                
                self.statProj[label] = round(fga * blkPer)



#----------------------------------------------


class TeamBlocksPerFga(TeamStat):

    baselineSet = []

    def __init__(self, team):
        super().__init__(team, "blk_per_fga")


    def computeGame(self, game):
        result = 0
        gameMins = game[0]
        blk = game[1]
        fga = game[2]
        try:
            result = blk/fga
        except ZeroDivisionError:
            pass
        return result


    def getDesiredStats(self):
        return ("{0}.blk", "{1}.fga")


    def getNewPlayerStat(self):
        return None


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in TeamBlocksPerFga.baselineSet


    def setBaseline(self, proj):
        TeamBlocksPerFga.baselineSet.append(proj.getBaseLine())


    def setStats(self, proj):        
        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
            if conditions["off_def"] == "offense":
                conditions["proj_id"] = conditions["proj_id"](proj)
                conditions["label"] = conditions["label"](proj)
                
                label = conditions["label"]
                self.statProj[label] = self.negotiate(conditions)


#----------------------------------------------


class TeamDReb(TeamStat):

    baselineSet = []

    def __init__(self, team):
        super().__init__(team, "dreb")


    def getDesiredStats(self):
        return ("{0}.dreb", )


    def getNewPlayerStat(self):
        newStat = PlayerDReb(self)
        return newStat


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in TeamDReb.baselineSet


    def setBaseline(self, proj):
        TeamDReb.baselineSet.append(proj.getBaseLine())


    def setStats(self, proj):        
        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
            if conditions["off_def"] == "offense":
                conditions["proj_id"] = conditions["proj_id"](proj)
                conditions["label"] = conditions["label"](proj)
                
                label = conditions["label"]
                
                    
                p,t,h = label.split("-")
                if h != "all":
                    h = "home" if h == "away" else "away"
                oppLabel = "-".join((p,t,h))

                drebPer = self.team.teamStats["dreb_per_miss"].getStatProj(label)
                fga = self.team.matchup.getOpp(self.team).teamStats["fga"].getStatProj(oppLabel)
                fgm = self.team.matchup.getOpp(self.team).teamStats["fgm"].getStatProj(oppLabel)

                self.statProj[label] = round((fga-fgm) * drebPer)



#----------------------------------------------


class TeamDRebPerMiss(TeamStat):

    baselineSet = []

    def __init__(self, team):
        super().__init__(team, "dreb_per_miss")


    def computeGame(self, game):
        result = 0
        gameMins = game[0]
        dreb = game[1]
        fga = game[2]
        fgm = game[3]
        try:
            result = dreb/(fga - fgm)
        except ZeroDivisionError:
            pass
        return result


    def getDesiredStats(self):
        return ("{0}.dreb", "{1}.fga", "{1}.fgm")


    def getNewPlayerStat(self):
        return None


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in TeamDRebPerMiss.baselineSet


    def setBaseline(self, proj):
        TeamDRebPerMiss.baselineSet.append(proj.getBaseLine())


    def setStats(self, proj):        
        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
            if conditions["off_def"] == "offense":
                conditions["proj_id"] = conditions["proj_id"](proj)
                conditions["label"] = conditions["label"](proj)
                
                label = conditions["label"]
                self.statProj[label] = self.negotiate(conditions)


#----------------------------------------------


class TeamFga(TeamStat):

    baselineSet = []

    def __init__(self, team):
        super().__init__(team, "fga")


    def getDesiredStats(self):
        return ("{0}.fga", )

    def getNewPlayerStat(self):
        newStat = PlayerFga(self)
        return newStat


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in TeamFga.baselineSet


    def setBaseline(self, proj):
        TeamFga.baselineSet.append(proj.getBaseLine())


    def setStats(self, proj):        
        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
            if conditions["off_def"] == "offense":
                conditions["proj_id"] = conditions["proj_id"](proj)
                conditions["label"] = conditions["label"](proj)
                
                label = conditions["label"]
                

                twoPta = self.team.teamStats["2pta"].getStatProj(label)
                threePta = self.team.teamStats["3pta"].getStatProj(label)
                
                self.statProj[label] = round(twoPta + threePta)

        
#----------------------------------------------


class TeamFgm(TeamStat):

    baselineSet = []

    def __init__(self, team):
        super().__init__(team, "fgm")


    def getDesiredStats(self):
        return ("{0}.fgm", )


    def getNewPlayerStat(self):
        newStat = PlayerFgm(self)
        return newStat


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in TeamFgm.baselineSet


    def setBaseline(self, proj):
        TeamFgm.baselineSet.append(proj.getBaseLine())


    def setStats(self, proj):        
        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
            if conditions["off_def"] == "offense":
                conditions["proj_id"] = conditions["proj_id"](proj)
                conditions["label"] = conditions["label"](proj)
                
                label = conditions["label"]
                

                twoPtm = self.team.teamStats["2ptm"].getStatProj(label)
                threePtm = self.team.teamStats["3ptm"].getStatProj(label)
                
                self.statProj[label] = round(twoPtm + threePtm)

        
#----------------------------------------------


class TeamFta(TeamStat):

    baselineSet = []

    def __init__(self, team):
        super().__init__(team, "fta")


    def getDesiredStats(self):
        return ("{0}.fta", )


    def getNewPlayerStat(self):
        newStat = PlayerFta(self)
        return newStat


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in TeamFta.baselineSet


    def setBaseline(self, proj):
        TeamFta.baselineSet.append(proj.getBaseLine())


    def setStats(self, proj):        
        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
            if conditions["off_def"] == "offense":
                conditions["proj_id"] = conditions["proj_id"](proj)
                conditions["label"] = conditions["label"](proj)
                
                label = conditions["label"]
                
                    
                p,t,h = label.split("-")
                if h != "all":
                    h = "home" if h == "away" else "away"
                oppLabel = "-".join((p,t,h))

                ftaPer = self.team.teamStats["fta_per_foul"].getStatProj(label)
                fouls = self.team.matchup.getOpp(self.team).teamStats["fouls"].getStatProj(oppLabel)
                
                self.statProj[label] = round(fouls * ftaPer)

        
#----------------------------------------------


class TeamFtm(TeamStat):

    baselineSet = []

    def __init__(self, team):
        super().__init__(team, "ftm")


    def getDesiredStats(self):
        return ("{0}.ftm", )


    def getNewPlayerStat(self):
        newStat = PlayerFtm(self)
        return newStat


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in TeamFtm.baselineSet


    def setBaseline(self, proj):
        TeamFtm.baselineSet.append(proj.getBaseLine())


    def setStats(self, proj):        
        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
            if conditions["off_def"] == "offense":
                conditions["proj_id"] = conditions["proj_id"](proj)
                conditions["label"] = conditions["label"](proj)
                
                label = conditions["label"]
                

                fta = self.team.teamStats["fta"].getStatProj(label)
                ftPct = self.team.teamStats["ft_pct"].getStatProj(label)
                
                self.statProj[label] = round(fta * ftPct)

        
#----------------------------------------------


class TeamFtPct(TeamStat):

    baselineSet = []

    def __init__(self, team):
        super().__init__(team, "ft_pct")


    def computeGame(self, game):
        result = 0
        gameMins = game[0]
        fta = game[1]
        ftm = game[2]
        try:
            result = ftm/fta
        except ZeroDivisionError:
            pass
        return result


    def getDesiredStats(self):
        return ("{0}.fta", "{0}.ftm" )


    def getNewPlayerStat(self):
        newStat = PlayerFtPct(self)
        return newStat


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in TeamFtPct.baselineSet


    def negotiate(self, formatting):
        # Initiate variables
        totals = []
        index = 3
        result = 0
       
        teamResult = self.db.curs.execute(teamNegotiateCmd.format(formatting)).fetchone()
##        print(teamNegotiateCmd.format(formatting))
##        print("\n\nteamResult")
##        print(teamResult)
        

        matchFormat = formatting.copy()
        matchFormat["proj_id"] = "matchup"
        matchResult = self.db.curs.execute(teamNegotiateCmd.format(matchFormat)).fetchone()
##        print(teamNegotiateCmd.format(matchFormat))
##        print("\nmatchResult")
##        print(matchResult)


        b2bFormat = formatting.copy()
        b2bFormat["proj_id"] = "b2b"
        b2bResult = self.db.curs.execute(teamNegotiateCmd.format(b2bFormat)).fetchone()
##        print(teamNegotiateCmd.format(b2bFormat))
##        print("\nb2bResult")
##        print(b2bResult)

    
        if teamResult:
            totals.append(teamResult[index])

        if matchResult:
            totals.append(matchResult[index])

        if b2bResult:
            totals.append(b2bResult[index])

        if len(totals):
            result = numpy.mean(totals)

##        print("\nresult")
##        print(result)
##        print("\n"+("-"*50)+"\n")
        return result



    def setBaseline(self, proj):
        TeamFtPct.baselineSet.append(proj.getBaseLine())


    def setStats(self, proj):        
        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
            if conditions["off_def"] == "offense":
                conditions["proj_id"] = conditions["proj_id"](proj)
                conditions["label"] = conditions["label"](proj)
                
                label = conditions["label"]
                self.statProj[label] = self.negotiate(conditions)

        
#----------------------------------------------


class TeamFouls(TeamStat):

    baselineSet = []

    def __init__(self, team):
        super().__init__(team, "fouls")


    def getDesiredStats(self):
        return ("{0}.fouls", )


    def getNewPlayerStat(self):
        newStat = PlayerFouls(self)
        return newStat


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in TeamFouls.baselineSet


    def setBaseline(self, proj):
        TeamFouls.baselineSet.append(proj.getBaseLine())


#----------------------------------------------


class TeamMinutes(TeamStat):

    def __init__(self, team):
        super().__init__(team, "mins")


    def getDesiredStats(self):
        return ("{0}.fga", )


    def getNewPlayerStat(self):
        newStat = PlayerMinutes(self)
        return newStat
        

    def isBaselineSet(self, proj):
        return True


    def setLineupStats(self, proj):
        pass


    def setMatchupStats(self, proj):
        pass

    def setB2bStats(self, proj):
        pass

    def setB2BVsStats(self, proj):
        pass

    def setSimilarStats(self, proj):
        pass



    def setLineupVsStats(self, proj):
        pass


    def setStats(self, proj):        
        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
            if conditions["off_def"] == "offense":
                conditions["proj_id"] = conditions["proj_id"](proj)
                conditions["label"] = conditions["label"](proj)
                
                label = conditions["label"]
                self.statProj[label] = 48.0*5


    def updateMins(self, label, newMins):
        self.statProj[label] = newMins
        

#----------------------------------------------


class TeamOReb(TeamStat):

    baselineSet = []

    def __init__(self, team):
        super().__init__(team, "oreb")


    def getDesiredStats(self):
        return ("{0}.oreb", )


    def getNewPlayerStat(self):
        newStat = PlayerOReb(self)
        return newStat


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in TeamOReb.baselineSet


    def setBaseline(self, proj):
        TeamOReb.baselineSet.append(proj.getBaseLine())


    def setStats(self, proj):        
        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
            if conditions["off_def"] == "offense":
                conditions["proj_id"] = conditions["proj_id"](proj)
                conditions["label"] = conditions["label"](proj)
                
                label = conditions["label"]
                
                orebPer = self.team.teamStats["oreb_per_miss"].getStatProj(label)
                fga = self.team.teamStats["fga"].getStatProj(label)
                fgm = self.team.teamStats["fgm"].getStatProj(label)

                self.statProj[label] = round((fga-fgm) * orebPer)



#----------------------------------------------


class TeamORebPerMiss(TeamStat):

    baselineSet = []

    def __init__(self, team):
        super().__init__(team, "oreb_per_miss")


    def computeGame(self, game):
        result = 0
        gameMins = game[0]
        oreb = game[1]
        fga = game[2]
        fgm = game[3]
        try:
            result = oreb/(fga - fgm)
        except ZeroDivisionError:
            pass
        return result


    def getDesiredStats(self):
        return ("{0}.oreb", "{0}.fga", "{0}.fgm")


    def getNewPlayerStat(self):
        return None


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in TeamORebPerMiss.baselineSet


    def setBaseline(self, proj):
        TeamORebPerMiss.baselineSet.append(proj.getBaseLine())


    def setStats(self, proj):        
        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
            if conditions["off_def"] == "offense":
                conditions["proj_id"] = conditions["proj_id"](proj)
                conditions["label"] = conditions["label"](proj)
                
                label = conditions["label"]
                self.statProj[label] = self.negotiate(conditions)


#----------------------------------------------


class TeamPoints(TeamStat):

    baselineSet = []

    def __init__(self, team):
        super().__init__(team, "points")


    def getDesiredStats(self):
        return ("{0}.points",  )


    def getNewPlayerStat(self):
        newStat = PlayerPoints(self)
        return newStat


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in TeamPoints.baselineSet


    def setBaseline(self, proj):
        TeamPoints.baselineSet.append(proj.getBaseLine())


    def setStats(self, proj):        
        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
            if conditions["off_def"] == "offense":
                conditions["proj_id"] = conditions["proj_id"](proj)
                conditions["label"] = conditions["label"](proj)
                
                label = conditions["label"]
                
                    
                ftm = self.team.teamStats["ftm"].getStatProj(label)
                fgm = self.team.teamStats["fgm"].getStatProj(label)
                tpm = self.team.teamStats["3ptm"].getStatProj(label)
                
                self.statProj[label] = round((fgm*2) + ftm + tpm)



#----------------------------------------------


class TeamSteals(TeamStat):

    baselineSet = []

    def __init__(self, team):
        super().__init__(team, "stl")


    def getDesiredStats(self):
        return ("{0}.stl",  )


    def getNewPlayerStat(self):
        newStat = PlayerSteals(self)
        return newStat


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in TeamSteals.baselineSet


    def setBaseline(self, proj):
        TeamSteals.baselineSet.append(proj.getBaseLine())


    def setStats(self, proj):        
        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
            if conditions["off_def"] == "offense":
                conditions["proj_id"] = conditions["proj_id"](proj)
                conditions["label"] = conditions["label"](proj)
                
                label = conditions["label"]
                
                    
                p,t,h = label.split("-")
                if h != "all":
                    h = "home" if h == "away" else "away"
                oppLabel = "-".join((p,t,h))

                stealPer = self.team.teamStats["stl_per_turn"].getStatProj(label)
                turn = self.team.matchup.getOpp(self.team).teamStats["turn"].getStatProj(oppLabel)
                
                self.statProj[label] = round(turn * stealPer)


#----------------------------------------------


class TeamStealsPerTurn(TeamStat):

    baselineSet = []

    def __init__(self, team):
        super().__init__(team, "stl_per_turn")


    def computeGame(self, game):
        result = 0
        gameMins = game[0]
        stl = game[1]
        turn = game[2]
        try:
            result = stl/turn
        except ZeroDivisionError:
            pass
        return result


    def getDesiredStats(self):
        return ("{0}.stl", "{1}.turn" )


    def getNewPlayerStat(self):
        return None


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in TeamStealsPerTurn.baselineSet


    def setBaseline(self, proj):
        TeamStealsPerTurn.baselineSet.append(proj.getBaseLine())


    def setStats(self, proj):        
        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
            if conditions["off_def"] == "offense":
                conditions["proj_id"] = conditions["proj_id"](proj)
                conditions["label"] = conditions["label"](proj)
                
                label = conditions["label"]
                self.statProj[label] = self.negotiate(conditions)


#----------------------------------------------


class TeamTurnovers(TeamStat):

    baselineSet = []

    def __init__(self, team):
        super().__init__(team, "turn")


    def getDesiredStats(self):
        return ("{0}.turn", )


    def getNewPlayerStat(self):
        newStat = PlayerTurnovers(self)
        return newStat


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in TeamTurnovers.baselineSet


    def setBaseline(self, proj):
        TeamTurnovers.baselineSet.append(proj.getBaseLine())


###############################################


class PlayerStat(Stat):

    PlayerProjections = (playerProj, playerLineupProj, )
                       
    def __init__(self, teamStat, statId):
        self.teamStat = teamStat
        self.player = None
        self.statEst = {}
        self.statAdj = {}
        super().__init__(statId)


    def crunchNumbers(self):
        for proj in self.getProjections():
##            if not self.isBaselineSet(proj):
##                print("Setting Player {} Baselines\n".format(self.statId))
##                self.setBaselineTendencies(proj)
##                self.makeBuckets(proj)
##                self.setBuckets(proj)   
##                self.setBaseline(proj)
##                self.db.conn.commit()

            if proj == playerLineupProj:
                self.setLineupStats(proj)
               
            if self.getMatchupGames():
                self.setMatchupStats(proj)

            if self.getB2bGames():
                self.setB2bStats(proj)

            self.setSimilarStats(proj)


    def getB2bGames(self):
        return self.player.team.getB2bGames()


    def getB2bProj(self):
        return playerB2bProj


    def getBucketTable(self):
        return playerBucketTable


    def getGameConditions(self, proj, itemId="all", haConstraint=None):
        conditionsLists = []
        for constraints in proj.getConstraints(haConstraint):
            timeFrame, homeAway, offDef = constraints
            conditions = {}
            for key, value in (("item_type", self.getItemType()),
                               ("item_id", itemId),
                               ("stat_id", self.statId),
                               # proj_id is a lambda?
                               ("proj_id", proj.getProjId()),
                               ("check_id", proj.getCheckId()),
                               ("time_frame", timeFrame),
                               ("home_away", homeAway),
                               ("off_def", offDef),
                               ("gdCmd", getGDCmd(timeFrame)),
                               ("haCmd", getHACmd(homeAway)),
                               # giCmd is a lambda
                               ("gameGroup", proj.getGameGroup(self.getItem())),
                               ("selectCmd", self.getSelectCmd(offDef)),
                               ("gbCmd", ""),
                               ("whereCmd", proj.getWhereCmd()),
                               ("oppJoin", ""),
                               ("posJoin", posJoin),
                               # label is a lambda
                               ("label",proj.getLabel(timeFrame,homeAway)),
                               ):
                conditions[key] = value
            conditionsLists.append(conditions.copy())
        return conditionsLists
           
                
    def getItem(self):
        return self.player


    def getItemId(self):
        return self.player.getPlayerId()


    def getItemType(self):
        return "player"


    def getMatchProj(self):
        return playerMatchProj


    def getMatchupGames(self):
        return self.player.team.getMatchupGames()


    def getProjections(self):
        return PlayerStat.PlayerProjections


    def getSelectCmd(self, offDef):
        # {0} is filled with stats when on offense, opp when on defense
        formatting = ("stats", ) 
        cmd = ", ".join(self.getDesiredStats())
        return cmd.format(*formatting)


    def getSimProj(self):
        return playerSimProj


    def getTotalsTable(self):
        return playerTotalsTable


    def insertResults(self, table, conditions):
        
        #pprint(selectStatsCmd.format(conditions))
        
        totals = [self.computeGame(x) for x in self.db.curs.execute(selectStatsCmd.format(conditions)).fetchall()]
        
        #pprint(totals)
        ##  calculate num, min, 15qtr, 40qtr, avg, 60qtr, 85qtr, max of totals
        formatting = self.calcItemList(totals, conditions)
        if formatting["num"]:
            try:
                self.db.insert(table, formatting)
            except IntegrityError:
                pass


    def makeBuckets(self, proj):

        for conditions in self.getGameConditions(proj):
            conditions["proj_id"] = conditions["proj_id"](proj)
            conditions["bucketTable"] = "player"
            for pos, start in self.getPlayerConditions():
                newConditions = conditions.copy()
                newConditions["pos"] = pos
                newConditions["start"] = start
                
                posComponent = "_{}".format(pos) if pos else ""
                startComponent = "_{}".format(start) if start else ""

                newConditions["proj_id"] = conditions["proj_id"]+posComponent+startComponent
                newConditions["label"] = newConditions["proj_id"]+"-{}-{}".format(conditions["time_frame"], conditions["home_away"])
                newConditions["whereCmd"] = ""

                totals = [x[0] for x in self.db.curs.execute(allAvgCmd.format(newConditions)).fetchall()]
                formatting = self.calcItemList(totals, newConditions)

                try:
                    self.db.insert(playerTotalsTable, formatting)
                except IntegrityError:
                    pass


    def setB2bStats(self, proj):
        for conditions in self.getGameConditions(self.getB2bProj(), itemId=self.getItemId(), haConstraint=self.getItem().getHomeAway()):
            games = None
            conditions["proj_id"] = conditions["proj_id"](proj)

            for pos, start in self.getPlayerConditions():
                newConditions = conditions.copy()
                newConditions["pos"] = pos
                newConditions["start"] = start
                newConditions["oppJoin"] = ""
                newConditions["posJoin"] = posJoin
                
                posComponent = "_{}".format(pos) if pos else ""
                startComponent = "_{}".format(start) if start else ""

                newConditions["proj_id"] = conditions["proj_id"]+posComponent+startComponent
                newConditions["check_id"] = conditions["check_id"] + posComponent+startComponent
                newConditions["label"] = newConditions["proj_id"]+"-{}-{}".format(conditions["time_frame"], conditions["home_away"])                         

                whereCmd = ""
                if pos:
                    if pos in ("PG","SG"):
                        whereCmd += " AND (position = '{}' OR position = 'G')".format(pos)
                    if pos in ("SF","PF"):
                        whereCmd += " AND (position = '{}' OR position = 'F')".format(pos)
                    else:
                        whereCmd += " AND position = '{}'".format(pos)
                if start:
                    whereCmd += " AND starter = {}".format(start)
                    
                if proj.getGameGroup(self.getItem()):
                    games = tuple(set(proj.getGameGroup(self.getItem())).intersection(set(conditions["gameGroup"])))
                else:
                    games = conditions["gameGroup"]
                newConditions["whereCmd"] = conditions["whereCmd"](self.getItemId(), getGICmd(games)) + whereCmd

                
                try:
                    self.insertResults(playerTotalsTable, newConditions.copy())
                except OperationalError:
                    pprint(newConditions)
                    print()
                    pprint(selectStatsCmd.format(newConditions))
                    raise AssertionError
        
                

    def setBaselineTendencies(self, proj):
        ##  For each team_id in database
        ##  item_type allows for players or teams
        for itemId in [x[0] for x in self.db.curs.execute("SELECT DISTINCT {0[item_type]}_id FROM {0[item_type]}_stats AS stats INNER JOIN ({0[gdCmd]}) AS gd ON stats.game_id = gd.game_id".format({"item_type":self.getItemType(), "gdCmd": seasonCmd})).fetchall()]:
            for conditions in self.getGameConditions(proj, itemId=itemId):
                conditions["bucketTable"] = "player"
                if conditions["off_def"] == "offense":
                    conditions["proj_id"] = conditions["proj_id"](proj)            
                    for pos, start in self.getPlayerConditions():
                        newConditions = conditions.copy()
                        newConditions["pos"] = pos
                        newConditions["start"] = start
                        newConditions["oppJoin"] = ""
                        newConditions["posJoin"] = posJoin
                        
                        posComponent = "_{}".format(pos) if pos else ""
                        startComponent = "_{}".format(start) if start else ""

                        newConditions["proj_id"] = conditions["proj_id"]+posComponent+startComponent
                        newConditions["check_id"] = conditions["proj_id"]+posComponent+startComponent
                        newConditions["label"] = newConditions["proj_id"]+"-{}-{}".format(conditions["time_frame"], conditions["home_away"])

                        whereCmd = "WHERE stats.player_id = {}".format(itemId)
                        if pos:
                            if pos in ("PG","SG"):
                                whereCmd += " AND (position = '{}' OR position = 'G')".format(pos)
                            if pos in ("SF","PF"):
                                whereCmd += " AND (position = '{}' OR position = 'F')".format(pos)
                            else:
                                whereCmd += " AND position = '{}'".format(pos)
                        if start:
                            whereCmd += " AND starter = {}".format(start)

                        newConditions["whereCmd"] = whereCmd

                        ##  Compile offensive game stats for every player in each player group
                        ##   played under these conditions
                        try:
                            self.insertResults(playerTotalsTable, newConditions.copy())
                        except OperationalError:
                            pprint(newConditions)
                            print()
                            pprint(selectStatsCmd.format(newConditions))
                            raise AssertionError



    def setBuckets(self, proj):
        ##  For each team_id in database
        ##  item_type allows for players or teams
        for itemId in [x[0] for x in self.db.curs.execute("SELECT DISTINCT {0[item_type]}_id FROM {0[item_type]}_stats AS stats INNER JOIN ({0[gdCmd]}) AS gd ON stats.game_id = gd.game_id".format({"item_type":self.getItemType(), "gdCmd": seasonCmd})).fetchall()]:
            for conditions in self.getGameConditions(proj, itemId=itemId):
                conditions["bucketTable"] = "player"
                conditions["proj_id"] = conditions["proj_id"](proj)            
                for pos, start in self.getPlayerConditions():
                    newConditions = conditions.copy()
                    newConditions["pos"] = pos
                    newConditions["start"] = start
                    
                    posComponent = "_{}".format(pos) if pos else ""
                    startComponent = "_{}".format(start) if start else ""

                    newConditions["proj_id"] = conditions["proj_id"]+posComponent+startComponent
                    newConditions["check_id"] = conditions["check_id"]+posComponent+startComponent
                    newConditions["label"] = newConditions["proj_id"]+"-{}-{}".format(conditions["time_frame"], conditions["home_away"])

                    whereCmd = "WHERE stats.opp_id = {}".format(itemId)
                    if pos:
                        if pos in ("PG","SG"):
                            whereCmd += " AND (position = '{}' OR position = 'G')".format(pos)
                        if pos in ("SF","PF"):
                            whereCmd += " AND (position = '{}' OR position = 'F')".format(pos)
                        else:
                            whereCmd += " AND position = '{}'".format(pos)
                    if start:
                        whereCmd += " AND starter = {}".format(start)

                    newConditions["whereCmd"] = whereCmd
                
                    formatting = self.getNewBucket(newConditions)
                    try:
                        if formatting["bucket"] != "n/a":
                            self.db.insert(playerBucketTable, formatting)
                    except IntegrityError:
                        pass


    def setLineupStats(self, proj):
        for conditions in self.getGameConditions(proj, itemId=self.getItemId(), haConstraint=self.getItem().getHomeAway()):

            conditions["bucketTable"] = "player"
            conditions["proj_id"] = conditions["proj_id"](proj)

            for pos, start in self.getPlayerConditions():
                newConditions = conditions.copy()
                newConditions["pos"] = pos
                newConditions["start"] = start
                newConditions["oppJoin"] = ""
                newConditions["posJoin"] = posJoin
                
                posComponent = "_{}".format(pos) if pos else ""
                startComponent = "_{}".format(start) if start else ""

                newConditions["proj_id"] = conditions["proj_id"]+posComponent+startComponent
                newConditions["check_id"] = conditions["check_id"] + posComponent+startComponent
                newConditions["label"] = newConditions["proj_id"]+"-{}-{}".format(conditions["time_frame"], conditions["home_away"])

                whereCmd = "WHERE stats.player_id = {}".format(self.getItemId())
                if pos:
                    if pos in ("PG","SG"):
                        whereCmd += " AND (position = '{}' OR position = 'G')".format(pos)
                    if pos in ("SF","PF"):
                        whereCmd += " AND (position = '{}' OR position = 'F')".format(pos)
                    else:
                        whereCmd += " AND position = '{}'".format(pos)
                if start:
                    whereCmd += " AND starter = {}".format(start)

                newConditions["whereCmd"] = whereCmd + " AND " + getGICmd(conditions["gameGroup"])

                try:
                    self.insertResults(playerTotalsTable, newConditions.copy())
                except OperationalError:
                    pprint(newConditions)
                    print()
                    pprint(selectStatsCmd.format(newConditions))
                    raise AssertionError

                formatting = self.getNewBucket(newConditions)

                try:
                    if formatting["bucket"] != "n/a":
                        self.db.insert(playerBucketTable, formatting)
                except IntegrityError:
                    pass


    def setMatchupStats(self, proj):
        for conditions in self.getGameConditions(self.getMatchProj(), itemId=self.getItemId(), haConstraint=self.getItem().getHomeAway()):
            games = None
            
            conditions["proj_id"] = conditions["proj_id"](proj)

            for pos, start in self.getPlayerConditions():
                newConditions = conditions.copy()
                newConditions["pos"] = pos
                newConditions["start"] = start
                newConditions["oppJoin"] = ""
                newConditions["posJoin"] = posJoin
                
                posComponent = "_{}".format(pos) if pos else ""
                startComponent = "_{}".format(start) if start else ""

                newConditions["proj_id"] = conditions["proj_id"]+posComponent+startComponent
                newConditions["check_id"] = conditions["check_id"] + posComponent+startComponent
                newConditions["label"] = newConditions["proj_id"]+"-{}-{}".format(conditions["time_frame"], conditions["home_away"])                         

                whereCmd = ""
                if pos:
                    if pos in ("PG","SG"):
                        whereCmd += " AND (position = '{}' OR position = 'G')".format(pos)
                    if pos in ("SF","PF"):
                        whereCmd += " AND (position = '{}' OR position = 'F')".format(pos)
                    else:
                        whereCmd += " AND position = '{}'".format(pos)
                if start:
                    whereCmd += " AND starter = {}".format(start)
                    
                if proj.getGameGroup(self.getItem()):
                    games = tuple(set(proj.getGameGroup(self.getItem())).intersection(set(conditions["gameGroup"])))
                else:
                    games = conditions["gameGroup"]
                newConditions["whereCmd"] = conditions["whereCmd"](self.getItemId(), getGICmd(games)) + whereCmd

                
                try:
                    self.insertResults(playerTotalsTable, newConditions.copy())
                except OperationalError:
                    pprint(newConditions)
                    print()
                    pprint(selectStatsCmd.format(newConditions))
                    raise AssertionError
                    

    def setPlayer(self, player):
        self.player = player


    def setSimilarStats(self, proj):

        for conditions in self.getSimGameConditions(self.getSimProj(), haConstraint=self.getItem().getHomeAway()):
            conditions["check_id"] = proj.getCheckId()
            
            for pos, start in self.getPlayerConditions():
                offConditions = conditions.copy()
                offConditions["bucketTable"] = "player"
                offConditions["item_id"] = self.getItemId()
                offConditions["off_def"] = "offense"
                offConditions["pos"] = pos
                offConditions["start"] = start
                
                posComponent = "_{}".format(pos) if pos else ""
                startComponent = "_{}".format(start) if start else ""

                offConditions["proj_id"] = proj.getProjId()(proj)+posComponent+startComponent
                offConditions["check_id"] = conditions["check_id"] + posComponent+startComponent


                defConditions = offConditions.copy()
                defConditions["bucketTable"] = "vs"
                if defConditions["home_away"] != "all":
                    defConditions["home_away"] = "away" if conditions["home_away"] == "home" else "home"
                defConditions["proj_id"] = sub("player", "vs_player", proj.getProjId()(proj))+posComponent+startComponent
                defConditions["off_def"] = "defense"
                defConditions["item_id"] = self.getItem().getOppId()
                defConditions["check_id"] = sub("player", "vs_player", offConditions["check_id"] + posComponent+startComponent)

                try:
                    offBucket = self.db.curs.execute(bucketCmd.format(offConditions)).fetchone()[0]
                    offConditions["bucket"] = offBucket
                    
                    defBucket = self.db.curs.execute(bucketCmd.format(defConditions)).fetchone()[0]
                    defConditions["bucket"] = defBucket

                
                    offPlayers = tuple([x[0] for x in self.db.curs.execute(similarCmd.format(offConditions)).fetchall() if x[0] != str(self.getItemId())]) 
                    defTeams = tuple([x[0] for x in self.db.curs.execute(similarCmd.format(defConditions)).fetchall() if x[0] != str(self.player.getOppId())]) 
                
                    playerCmd = getPlayerCmd(offPlayers)
                    oppCmd = getOppCmd(defTeams)
                    offConditions["proj_id"] = conditions["proj_id"](proj)
                    offConditions["item_id"] = self.getItemId()
                    offConditions["whereCmd"] = similarWhereCmd.format({"itemCmd":playerCmd, "oppCmd":oppCmd})               
                    
                    # enter into team_totals
                    self.insertResults(self.getTotalsTable(), offConditions.copy())
                    
                    # make similar bucket 
                    formatting = self.getNewBucket(offConditions.copy())
                    
                    try:
                        # enter bucket into team_bucket
                        self.db.insert(playerBucketTable, formatting)
                    except IntegrityError:
                        pass
                    

                    # similar defenses vs Player
                    playerCmd = getPlayerCmd((self.getItemId(),))
                    oppCmd = getOppCmd(defTeams)
                    offConditions["proj_id"] = "vs_"+conditions["proj_id"](proj)
                    offConditions["whereCmd"] = similarWhereCmd.format({"itemCmd":playerCmd, "oppCmd":oppCmd})
                    # enter into team_totals
                    self.insertResults(self.getTotalsTable(), offConditions)

                    # similar offenses vs Defense team
                    playerCmd = getPlayerCmd(offPlayers)
                    oppCmd = getOppCmd((self.player.getOppId(),))
                    defConditions["proj_id"] = "vs_"+conditions["proj_id"](proj)
                    defConditions["whereCmd"] = similarWhereCmd.format({"itemCmd":playerCmd, "oppCmd":oppCmd})
                    
                    # enter into team_totals
                    self.insertResults(teamTotalsTable, defConditions)

                except TypeError:
                    pass
                except IndexError:
                    pass


    def setStatsEst(self):        
        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
            if conditions["off_def"] == "offense":
                conditions["proj_id"] = conditions["proj_id"](proj)
                conditions["label"] = conditions["label"](proj)
                
                label = conditions["label"]
                pprint(conditions)
                raise AssertionError
                self.statProj[label] = round(self.negotiate(conditions))


#----------------------------------------------


class Player2ptAttempt(PlayerStat):

    baselineSet = []

    def __init__(self, teamStat):
        super().__init__(teamStat, "2pta")


    def computeGame(self, game):
        result = 0
        gameMins = game[0]
        fga = game[1]
        tpa = game[2]
        try:
            result = ((fga-tpa)/gameMins)*48
        except ZeroDivisionError:
            pass
        return result


    def getDesiredStats(self):
        return ("{0}.fga", "{0}.tpa")


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in Player2ptAttempt.baselineSet


    def setBaseline(self, proj):
        Player2ptAttempt.baselineSet.append(proj.getBaseLine())


##    def setStats(self, proj):        
##        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
##            if conditions["off_def"] == "offense":
##                conditions["proj_id"] = conditions["proj_id"](proj)
##                conditions["label"] = conditions["label"](proj)
##                
##                label = conditions["label"]
##                
##                p,t,h = label.split("-")
##                if h != "all":
##                    h = "home" if h == "away" else "away"
##                oppLabel = "-".join((p,t,h))
##                
##                poss = self.team.teamStats["poss"].getStatProj(label)
##                turn = self.team.teamStats["turn"].getStatProj(label)
##                fouls = self.team.matchup.getOpp(self.team).teamStats["fouls"].getStatProj(oppLabel)
##                fga = poss - turn - fouls
##            
##                twoPerFga = self.team.teamStats["2pt_per_fga"].getStatProj(label)
##                
##                self.statProj[label] = round(fga * twoPerFga)


#----------------------------------------------


class Player2ptMade(PlayerStat):

    baselineSet = []

    def __init__(self, teamStat):
        super().__init__(teamStat, "2ptm")


    def computeGame(self, game):
        result = 0
        gameMins = game[0]
        fgm = game[1]
        tpm = game[2]
        try:
            result = ((fgm-tpm)/gameMins)*48
        except ZeroDivisionError:
            pass
        return result


    def getDesiredStats(self):
        return ("{0}.fgm", "{0}.tpm")


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in Player2ptMade.baselineSet


    def setBaseline(self, proj):
        Player2ptMade.baselineSet.append(proj.getBaseLine())


##    def setStats(self, proj):        
##        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
##            if conditions["off_def"] == "offense":
##                conditions["proj_id"] = conditions["proj_id"](proj)
##                conditions["label"] = conditions["label"](proj)
##                
##                label = conditions["label"]
##                
##                #pprint(conditions)
##
##                twoAtt = self.team.teamStats["2pta"].getStatProj(label)
##                twoPct = self.team.teamStats["2pt_pct"].getStatProj(label)
##                
##                self.statProj[label] = round(twoAtt * twoPct)
##
        
#----------------------------------------------


class Player2ptPct(PlayerStat):

    baselineSet = []

    def __init__(self, teamStat):
        super().__init__(teamStat, "2pt_pct")


    def computeGame(self, game):
        result = 0
        gameMins = game[0]
        fga = game[1]
        fgm = game[2]
        tpa = game[3]
        tpm = game[4]

        twoatt = fga-tpa
        twomad = fgm-tpm
        try:
            result = twomad/twoatt
        except ZeroDivisionError:
            pass
        return result


    def getDesiredStats(self):
        return ("{0}.fga", "{0}.fgm", "{0}.tpa", "{0}.tpm")


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in Player2ptPct.baselineSet


    def setBaseline(self, proj):
        Player2ptPct.baselineSet.append(proj.getBaseLine())


    def setStats(self, proj):        
        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
            if conditions["off_def"] == "offense":
                conditions["proj_id"] = conditions["proj_id"](proj)
                conditions["label"] = conditions["label"](proj)
                
                label = conditions["label"]
                self.statProj[label] = self.negotiate(conditions)

        
#----------------------------------------------


class Player3ptAttempt(PlayerStat):

    baselineSet = []

    def __init__(self, teamStat):
        super().__init__(teamStat, "3pta")


    def getDesiredStats(self):
        return ("{0}.tpa",)


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in Player3ptAttempt.baselineSet


    def setBaseline(self, proj):
        Player3ptAttempt.baselineSet.append(proj.getBaseLine())


##    def setStats(self, proj):        
##        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
##            if conditions["off_def"] == "offense":
##                conditions["proj_id"] = conditions["proj_id"](proj)
##                conditions["label"] = conditions["label"](proj)
##                
##                label = conditions["label"]
##                
##
##                p,t,h = label.split("-")
##                if h != "all":
##                    h = "home" if h == "away" else "away"
##                oppLabel = "-".join((p,t,h))
##                
##                poss = self.team.teamStats["poss"].getStatProj(label)
##                turn = self.team.teamStats["turn"].getStatProj(label)
##                fouls = self.team.matchup.getOpp(self.team).teamStats["fouls"].getStatProj(oppLabel)
##                fga = poss - turn - fouls
##            
##                threePerFga = self.team.teamStats["3pt_per_fga"].getStatProj(label)
##                
##                self.statProj[label] = round(fga * threePerFga)

        
#----------------------------------------------


class Player3ptMade(PlayerStat):

    baselineSet = []

    def __init__(self, teamStat):
        super().__init__(teamStat, "3ptm")


    def getDesiredStats(self):
        return ("{0}.tpm", )


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in Player3ptMade.baselineSet


    def setBaseline(self, proj):
        Player3ptMade.baselineSet.append(proj.getBaseLine())


##    def setStats(self, proj):        
##        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
##            if conditions["off_def"] == "offense":
##                conditions["proj_id"] = conditions["proj_id"](proj)
##                conditions["label"] = conditions["label"](proj)
##                
##                label = conditions["label"]
##                
##
##                threeAtt = self.team.teamStats["3pta"].getStatProj(label)
##                threePct = self.team.teamStats["3pt_pct"].getStatProj(label)
##                
##                self.statProj[label] = round(threeAtt * threePct)

        
#----------------------------------------------


class Player3ptPct(PlayerStat):

    baselineSet = []

    def __init__(self, teamStat):
        super().__init__(teamStat, "3pt_pct")


    def computeGame(self, game):
        result = 0
        gameMins = game[0]
        tpa = game[1]
        tpm = game[2]
        
        try:
            result = tpm/tpa
        except ZeroDivisionError:
            pass
        return result


    def getDesiredStats(self):
        return ("{0}.tpa", "{0}.tpm")


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in Player3ptPct.baselineSet


    def setBaseline(self, proj):
        Player3ptPct.baselineSet.append(proj.getBaseLine())


##    def setStats(self, proj):        
##        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
##            if conditions["off_def"] == "offense":
##                conditions["proj_id"] = conditions["proj_id"](proj)
##                conditions["label"] = conditions["label"](proj)
##                
##                label = conditions["label"]
##                self.statProj[label] = self.negotiate(conditions)

        
#----------------------------------------------


class PlayerAssists(PlayerStat):

    baselineSet = []

    def __init__(self, teamStat):
        super().__init__(teamStat, "ast")


    def getDesiredStats(self):
        return ("{0}.ast", )


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in PlayerAssists.baselineSet


    def setBaseline(self, proj):
        PlayerAssists.baselineSet.append(proj.getBaseLine())


##    def setStats(self, proj):        
##        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
##            if conditions["off_def"] == "offense":
##                conditions["proj_id"] = conditions["proj_id"](proj)
##                conditions["label"] = conditions["label"](proj)
##                
##                label = conditions["label"]
##                
##                    
##                astPer = self.team.teamStats["ast_per_fgm"].getStatProj(label)
##                fgm = self.team.teamStats["fgm"].getStatProj(label)
##                
##                self.statProj[label] = round(fgm * astPer)



#----------------------------------------------


class PlayerBlocks(PlayerStat):

    baselineSet = []

    def __init__(self, teamStats):
        super().__init__(teamStats, "blk")


    def getDesiredStats(self):
        return ("{0}.blk", )


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in PlayerBlocks.baselineSet


    def setBaseline(self, proj):
        PlayerBlocks.baselineSet.append(proj.getBaseLine())


##    def setStats(self, proj):        
##        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
##            if conditions["off_def"] == "offense":
##                conditions["proj_id"] = conditions["proj_id"](proj)
##                conditions["label"] = conditions["label"](proj)
##                
##                label = conditions["label"]
##                
##                    
##                p,t,h = label.split("-")
##                if h != "all":
##                    h = "home" if h == "away" else "away"
##                oppLabel = "-".join((p,t,h))
##
##                blkPer = self.team.teamStats["blk_per_fga"].getStatProj(label)
##                fga = self.team.matchup.getOpp(self.team).teamStats["fga"].getStatProj(oppLabel)
##                
##                self.statProj[label] = round(fga * blkPer)



#----------------------------------------------


class PlayerDReb(PlayerStat):

    baselineSet = []

    def __init__(self, teamStat):
        super().__init__(teamStat, "dreb")


    def getDesiredStats(self):
        return ("{0}.dreb", )


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in PlayerDReb.baselineSet


    def setBaseline(self, proj):
        PlayerDReb.baselineSet.append(proj.getBaseLine())


##    def setStats(self, proj):        
##        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
##            if conditions["off_def"] == "offense":
##                conditions["proj_id"] = conditions["proj_id"](proj)
##                conditions["label"] = conditions["label"](proj)
##                
##                label = conditions["label"]
##                
##                    
##                p,t,h = label.split("-")
##                if h != "all":
##                    h = "home" if h == "away" else "away"
##                oppLabel = "-".join((p,t,h))
##
##                drebPer = self.team.teamStats["dreb_per_miss"].getStatProj(label)
##                fga = self.team.matchup.getOpp(self.team).teamStats["fga"].getStatProj(oppLabel)
##                fgm = self.team.matchup.getOpp(self.team).teamStats["fgm"].getStatProj(oppLabel)
##
##                self.statProj[label] = round((fga-fgm) * drebPer)



#----------------------------------------------


class PlayerFga(PlayerStat):

    baselineSet = []

    def __init__(self, teamStat):
        super().__init__(teamStat, "fga")


    def getDesiredStats(self):
        return ("{0}.fga", )


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in PlayerFga.baselineSet


    def setBaseline(self, proj):
        PlayerFga.baselineSet.append(proj.getBaseLine())


##    def setStats(self, proj):        
##        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
##            if conditions["off_def"] == "offense":
##                conditions["proj_id"] = conditions["proj_id"](proj)
##                conditions["label"] = conditions["label"](proj)
##                
##                label = conditions["label"]
##                
##
##                twoPta = self.team.teamStats["2pta"].getStatProj(label)
##                threePta = self.team.teamStats["3pta"].getStatProj(label)
##                
##                self.statProj[label] = round(twoPta + threePta)

        
#----------------------------------------------


class PlayerFgm(PlayerStat):

    baselineSet = []

    def __init__(self, teamStat):
        super().__init__(teamStat, "fgm")


    def getDesiredStats(self):
        return ("{0}.fgm", )


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in PlayerFgm.baselineSet


    def setBaseline(self, proj):
        PlayerFgm.baselineSet.append(proj.getBaseLine())


##    def setStats(self, proj):        
##        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
##            if conditions["off_def"] == "offense":
##                conditions["proj_id"] = conditions["proj_id"](proj)
##                conditions["label"] = conditions["label"](proj)
##                
##                label = conditions["label"]
##                
##
##                twoPtm = self.team.teamStats["2ptm"].getStatProj(label)
##                threePtm = self.team.teamStats["3ptm"].getStatProj(label)
##                
##                self.statProj[label] = round(twoPtm + threePtm)

        
#----------------------------------------------


class PlayerFta(PlayerStat):

    baselineSet = []

    def __init__(self, teamStat):
        super().__init__(teamStat, "fta")


    def getDesiredStats(self):
        return ("{0}.fta", )


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in PlayerFta.baselineSet


    def setBaseline(self, proj):
        PlayerFta.baselineSet.append(proj.getBaseLine())


##    def setStats(self, proj):        
##        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
##            if conditions["off_def"] == "offense":
##                conditions["proj_id"] = conditions["proj_id"](proj)
##                conditions["label"] = conditions["label"](proj)
##                
##                label = conditions["label"]
##                
##                    
##                p,t,h = label.split("-")
##                if h != "all":
##                    h = "home" if h == "away" else "away"
##                oppLabel = "-".join((p,t,h))
##
##                ftaPer = self.team.teamStats["fta_per_foul"].getStatProj(label)
##                fouls = self.team.matchup.getOpp(self.team).teamStats["fouls"].getStatProj(oppLabel)
##                
##                self.statProj[label] = round(fouls * ftaPer)

        
#----------------------------------------------


class PlayerFtm(PlayerStat):

    baselineSet = []

    def __init__(self, teamStat):
        super().__init__(teamStat, "ftm")


    def getDesiredStats(self):
        return ("{0}.ftm", )


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in PlayerFtm.baselineSet


    def setBaseline(self, proj):
        PlayerFtm.baselineSet.append(proj.getBaseLine())


##    def setStats(self, proj):        
##        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
##            if conditions["off_def"] == "offense":
##                conditions["proj_id"] = conditions["proj_id"](proj)
##                conditions["label"] = conditions["label"](proj)
##                
##                label = conditions["label"]
##                
##
##                fta = self.team.teamStats["fta"].getStatProj(label)
##                ftPct = self.team.teamStats["ft_pct"].getStatProj(label)
##                
##                self.statProj[label] = round(fta * ftPct)

        
#----------------------------------------------


class PlayerFtPct(PlayerStat):

    baselineSet = []

    def __init__(self, teamStat):
        super().__init__(teamStat, "ft_pct")


    def computeGame(self, game):
        result = 0
        gameMins = game[0]
        fta = game[1]
        ftm = game[2]
        try:
            result = ftm/fta
        except ZeroDivisionError:
            pass
        return result


    def getDesiredStats(self):
        return ("{0}.fta", "{0}.ftm" )


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in PlayerFtPct.baselineSet


    def negotiate(self, formatting):
        # Initiate variables
        raise AssertionError
##        totals = []
##        index = 3
##        result = 0
##       
##        teamResult = self.db.curs.execute(teamNegotiateCmd.format(formatting)).fetchone()
####        print(teamNegotiateCmd.format(formatting))
####        print("\n\nteamResult")
####        print(teamResult)
##        
##
##        matchFormat = formatting.copy()
##        matchFormat["proj_id"] = "matchup"
##        matchResult = self.db.curs.execute(teamNegotiateCmd.format(matchFormat)).fetchone()
####        print(teamNegotiateCmd.format(matchFormat))
####        print("\nmatchResult")
####        print(matchResult)
##
##
##        b2bFormat = formatting.copy()
##        b2bFormat["proj_id"] = "b2b"
##        b2bResult = self.db.curs.execute(teamNegotiateCmd.format(b2bFormat)).fetchone()
####        print(teamNegotiateCmd.format(b2bFormat))
####        print("\nb2bResult")
####        print(b2bResult)
##
##    
##        if teamResult:
##            totals.append(teamResult[index])
##
##        if matchResult:
##            totals.append(matchResult[index])
##
##        if b2bResult:
##            totals.append(b2bResult[index])
##
##        if len(totals):
##            result = numpy.mean(totals)
##
####        print("\nresult")
####        print(result)
####        print("\n"+("-"*50)+"\n")
##        return result



    def setBaseline(self, proj):
        PlayerFtPct.baselineSet.append(proj.getBaseLine())


    def setStats(self, proj):        
        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
            if conditions["off_def"] == "offense":
                conditions["proj_id"] = conditions["proj_id"](proj)
                conditions["label"] = conditions["label"](proj)
                
                label = conditions["label"]
                self.statProj[label] = self.negotiate(conditions)

        
#----------------------------------------------


class PlayerFouls(PlayerStat):

    baselineSet = []

    def __init__(self, teamStat):
        super().__init__(teamStat, "fouls")


    def getDesiredStats(self):
        return ("{0}.fouls", )


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in PlayerFouls.baselineSet


    def setBaseline(self, proj):
        PlayerFouls.baselineSet.append(proj.getBaseLine())


#----------------------------------------------


class PlayerMinutes(PlayerStat):

    baselineSet = []

    def __init__(self, teamStat):
        super().__init__(teamStat, "mins")


    def getDesiredStats(self):
        return ("{0}.mins", )
        

    def isBaselineSet(self, proj):
        return proj.getBaseLine() in PlayerMinutes.baselineSet


    def setBaseline(self, proj):
        PlayerMinutes.baselineSet.append(proj.getBaseLine())


##    def setStats(self, proj):        
##        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
##            if conditions["off_def"] == "offense":
##                conditions["proj_id"] = conditions["proj_id"](proj)
##                conditions["label"] = conditions["label"](proj)
##                
##                label = conditions["label"]
##                self.statProj[label] = 48.0*5
##
##
##    def updateMins(self, label, newMins):
##        self.statProj[label] = newMins
        

#----------------------------------------------


class PlayerOReb(PlayerStat):

    baselineSet = []

    def __init__(self, teamStat):
        super().__init__(teamStat, "oreb")


    def getDesiredStats(self):
        return ("{0}.oreb", )


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in PlayerOReb.baselineSet


    def setBaseline(self, proj):
        PlayerOReb.baselineSet.append(proj.getBaseLine())


##    def setStats(self, proj):        
##        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
##            if conditions["off_def"] == "offense":
##                conditions["proj_id"] = conditions["proj_id"](proj)
##                conditions["label"] = conditions["label"](proj)
##                
##                label = conditions["label"]
##                
##                orebPer = self.team.teamStats["oreb_per_miss"].getStatProj(label)
##                fga = self.team.teamStats["fga"].getStatProj(label)
##                fgm = self.team.teamStats["fgm"].getStatProj(label)
##
##                self.statProj[label] = round((fga-fgm) * orebPer)



#----------------------------------------------


class PlayerPoints(PlayerStat):

    baselineSet = []

    def __init__(self, teamStat):
        super().__init__(teamStat, "points")


    def getDesiredStats(self):
        return ("{0}.points",  )


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in PlayerPoints.baselineSet


    def setBaseline(self, proj):
        PlayerPoints.baselineSet.append(proj.getBaseLine())


##    def setStats(self, proj):        
##        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
##            if conditions["off_def"] == "offense":
##                conditions["proj_id"] = conditions["proj_id"](proj)
##                conditions["label"] = conditions["label"](proj)
##                
##                label = conditions["label"]
##                
##                    
##                ftm = self.team.teamStats["ftm"].getStatProj(label)
##                fgm = self.team.teamStats["fgm"].getStatProj(label)
##                tpm = self.team.teamStats["3ptm"].getStatProj(label)
##                
##                self.statProj[label] = round((fgm*2) + ftm + tpm)


#----------------------------------------------


class PlayerSteals(PlayerStat):

    baselineSet = []

    def __init__(self, teamStat):
        super().__init__(teamStat, "stl")


    def getDesiredStats(self):
        return ("{0}.stl",  )


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in PlayerSteals.baselineSet


    def setBaseline(self, proj):
        PlayerSteals.baselineSet.append(proj.getBaseLine())


##    def setStats(self, proj):        
##        for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
##            if conditions["off_def"] == "offense":
##                conditions["proj_id"] = conditions["proj_id"](proj)
##                conditions["label"] = conditions["label"](proj)
##                
##                label = conditions["label"]
##                
##                    
##                p,t,h = label.split("-")
##                if h != "all":
##                    h = "home" if h == "away" else "away"
##                oppLabel = "-".join((p,t,h))
##
##                stealPer = self.team.teamStats["stl_per_turn"].getStatProj(label)
##                turn = self.team.matchup.getOpp(self.team).teamStats["turn"].getStatProj(oppLabel)
##                
##                self.statProj[label] = round(turn * stealPer)


#----------------------------------------------


class PlayerTurnovers(PlayerStat):

    baselineSet = []

    def __init__(self, team):
        super().__init__(team, "turn")


    def getDesiredStats(self):
        return ("{0}.turn", )


    def isBaselineSet(self, proj):
        return proj.getBaseLine() in PlayerTurnovers.baselineSet


    def setBaseline(self, proj):
        PlayerTurnovers.baselineSet.append(proj.getBaseLine())




        
#################################################################################


teamStats = (FtaPerFoul, Possessions, Team2ptAttempt, Team2ptMade, Team2ptPct,
             Team2ptPerFga, Team3ptAttempt, Team3ptMade, Team3ptPct,
             Team3ptPerFga, TeamAssists, TeamAssistsPerFgm, TeamBlocks, TeamBlocksPerFga, TeamDReb,
             TeamDRebPerMiss, TeamFga, TeamFgm, TeamFouls, TeamFta, TeamFtPct,
             TeamFtm, TeamMinutes, TeamOReb, TeamORebPerMiss, TeamPoints,
             TeamSteals, TeamStealsPerTurn, TeamTurnovers, )

playerStats = ()


#################################################################################


if __name__ == "__main__":

    class Team:
        def getOppId(self):
            return 3
        def getTeamId(self):
            return 27
        def getHomeAway(self):
            return "home"
        def getMatchupGames(self):
            return tuple([g[0] for g in db.curs.execute("SELECT stats.game_id FROM team_stats AS stats INNER JOIN ("+seasonCmd+") AS gd ON stats.game_id = gd.game_id WHERE team_id = ? AND opp_id = ?",(self.getTeamId(),self.getOppId())).fetchall()])
        def getB2bGames(self):
            return tuple([g[0] for g in db.curs.execute("SELECT b2b.game_id FROM back_to_back AS b2b INNER JOIN ("+seasonCmd+") AS gd ON b2b.game_id = gd.game_id WHERE team_id = ?",(self.getTeamId(),)).fetchall()])
        def getLineupGames(self):
            return tuple([g[0] for g in db.curs.execute("SELECT stats.game_id FROM team_stats AS stats INNER JOIN ("+seasonCmd+") AS gd ON stats.game_id = gd.game_id WHERE team_id = ?",(self.getTeamId(),)).fetchall() if g[0][-1] in ("0","1","2","3")])            

        
    sm = SportsManager()
    nba = sm.getLeague("nba")
    nba.databaseManager.openDB("season")
    db = nba.databaseManager.db["season"]

    createTempTables(db)

    team = Team()


    obj = Team3ptPct(team)
    obj.setDB(db)
    obj.crunchNumbers()
    for proj in TeamStat.TeamProjections:
        obj.setStats(proj)
    pprint(obj.getJson())
    
