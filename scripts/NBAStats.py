from SportsDB.DB.NBA import gameDateCmd
from SportsDB.Models.SportsManager import SportsManager

from datetime import date, timedelta
import numpy
from itertools import chain
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


timeFrameList = ("season", "sixWeeks", "twoWeeks")
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


def getPosWhere(pos):
    posWhere = " AND (position = '{}'".format(pos)
    if pos != "C":
        posWhere += " OR position = '{}'".format(pos[-1])
    posWhere += ")"
    return posWhere


def getTeamCmd(teamTuple):
    teamCmd = "stats.team_id"
    teamCmd += " IN "+str(teamTuple) if len(teamTuple) > 1 else " = "+str(teamTuple[0])
    return teamCmd
    
 
allCmd = " stats.game_id = gd.game_id"
awayCmd = allCmd + " AND stats.team_id = gd.away_id"
homeCmd = allCmd + " AND stats.team_id = gd.home_id"


#################################################################################

baseBucketCmd = "SELECT stat_15, stat_85, stat_60, stat_40 FROM {0[bucketTable]}_totals WHERE stat_id = '{0[stat_id]}' AND proj_id = '{0[check_id]}' AND time_frame = '{0[time_frame]}' AND home_away = '{0[home_away]}' AND off_def = '{0[off_def]}' AND item_id = 'all'"
bucketCmd = "SELECT bucket FROM {0[bucketTable]}_buckets WHERE stat_id = '{0[stat_id]}' AND proj_id = '{0[proj_id]}' AND time_frame = '{0[time_frame]}' AND home_away = '{0[home_away]}' AND off_def = '{0[off_def]}' AND item_id = '{0[item_id]}'"
oppJoin = "INNER JOIN team_stats AS opp ON stats.game_id = opp.game_id AND stats.opp_id = opp.team_id"
posJoin = "INNER JOIN positions AS pos ON stats.game_id = pos.game_id AND stats.player_id = pos.player_id"
selectStatsCmd = "SELECT gd.mins, {0[selectCmd]} FROM {0[item_type]}_stats AS stats {0[oppJoin]}{0[posJoin]} INNER JOIN ({0[gdCmd]}) AS gd ON {0[haCmd]} {0[whereCmd]}" 
similarCmd = "SELECT DISTINCT item_id FROM {0[bucketTable]}_buckets WHERE stat_id = '{0[stat_id]}' AND proj_id = '{0[check_id]}' AND time_frame = '{0[time_frame]}' AND home_away = '{0[home_away]}' AND off_def = '{0[off_def]}' AND bucket = '{0[bucket]}'"
similarWhereCmd = "WHERE {0[itemCmd]} AND {0[oppCmd]}"

itemAvgCmd = "SELECT stat_avg FROM {0[bucketTable]}_totals WHERE proj_id = '{0[proj_id]}' AND stat_id = '{0[stat_id]}' AND time_frame = '{0[time_frame]}' AND home_away = '{0[home_away]}' AND off_def = '{0[off_def]}' AND item_id = '{0[item_id]}'"
allAvgCmd = "SELECT stat_avg FROM {0[bucketTable]}_totals WHERE proj_id = '{0[proj_id]}' AND stat_id = '{0[stat_id]}' AND time_frame = '{0[time_frame]}' AND home_away = '{0[home_away]}' AND off_def = '{0[off_def]}'"


negotiateCmd = "SELECT num, stat_85, stat_60, stat_avg, stat_40, stat_15, stat_max, stat_min FROM {0[item_type]}_totals WHERE stat_id = '{0[stat_id]}' AND proj_id = '{0[proj_id]}' AND time_frame = '{0[time_frame]}' AND home_away = '{0[home_away]}' AND off_def = '{0[off_def]}' AND item_id = {0[item_id]}"
        

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
        createCmd = "CREATE TEMP TABLE IF NOT EXISTS {0[name]} (" + table["cmd"] + ")"
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


teamStatAbrvs = ["fga","fgm","fta","ftm","tpa","tpm","oreb","dreb","ast","stl","blk","turn","points","fouls"]
playerStatAbrvs = ["mins","fga","fgm","fta","ftm","tpa","tpm","oreb","dreb","ast","stl","blk","turn","fouls","points"]
ts_proc = lambda tp_abrv, tp_index: 1 + (teamStatAbrvs.index(tp_abrv) * 2) + tp_index
ps_proc = lambda pp_abrv: 1 + playerStatAbrvs.index(pp_abrv)


#################################################################################


def calcItemList(itemList, formatting):
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


def getGameConditions(itemId="all", haConstraint=None):
        conditionsLists = []
        for constraints in getGameConstraints(haConstraint):
            timeFrame, homeAway = constraints
            conditions = {}
            for key, value in (("item_id", itemId),
                               ("time_frame", timeFrame),
                               ("home_away", homeAway),
                               ("gdCmd", getGDCmd(timeFrame)),
                               ("haCmd", getHACmd(homeAway)),
                               ("label","{}-{}".format(timeFrame,homeAway)),
                               ):
                conditions[key] = value
            yield conditions.copy()


def getGameConstraints(homeConstraint=None):
        homeAwayList = allHomeAway if not homeConstraint else ("all", homeConstraint)
        for homeAway in homeAwayList:
            for timeFrame in timeFrameList:
                yield (timeFrame, homeAway)


def getNewBucket(db, formatting):
        
        bucket = "n/a"
        try:
            baseLow, baseHigh, base60, base40 = db.curs.execute(baseBucketCmd.format(formatting)).fetchone()
        except TypeError:
            print(baseBucketCmd.format(formatting))
            print()
            pprint(formatting)
            raise AssertionError
        statAvg = db.curs.execute(itemAvgCmd.format(formatting)).fetchone()
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


def getOppLabel(label):
    p,t,h = label.split("-")
    if h != "all":
        h = "home" if h == "away" else "away"
    oppLabel = "-".join((p,t,h))
    return oppLabel


def getPlayerConditions(db=None, playerId=None, player=None):
        posList = ("","PG", "SG", "SF", "PF", "C")
        starterList = ("0","1")
        if playerId:
            cmd = "SELECT DISTINCT position FROM positions AS pos INNER JOIN ("+seasonCmd+") AS gd ON pos.game_id = gd.game_id WHERE player_id = {}".format(playerId)
            posList = ["",]+[x[0] for x in db.curs.execute(cmd).fetchall() if x[0] in posList]
            cmd = "SELECT DISTINCT starter FROM player_stats AS stats INNER JOIN ("+seasonCmd+") AS gd ON stats.game_id = gd.game_id WHERE player_id = {}".format(playerId)
            starterList = [str(x[0]) for x in db.curs.execute(cmd).fetchall() if str(x[0]) in starterList]           

        if player:
            posList = ("",player.pos)
            starterList = (str(player.starter))
        
        for pos in posList:
            for starter in starterList:
                yield(pos, starter)


def makeTeamBuckets(db):
    for conditions in getGameConditions():
        conditions["proj_id"] = "team"
        conditions["bucketTable"] = "team"
        conditions["whereCmd"] = ""

        for stat in teamStatList:
            conditions["stat_id"] = stat.statId
            for off_def in ("offense", "defense"):
                conditions["off_def"] = off_def
                
                totals = [x[0] for x in db.curs.execute(allAvgCmd.format(conditions)).fetchall()]
                formatting = calcItemList(totals, conditions.copy())
                try:
                    db.insert(teamTotalsTable, formatting)
                except IntegrityError:
                    pass


def makeTeamVsBuckets(db):
    for pos, starter in getPlayerConditions():
        posComponent = "_{}".format(pos) if pos else ""
        startComponent = "_{}".format(starter) if starter else ""
      
        for conditions in getGameConditions():
            conditions["proj_id"] = "team_vs_player"+posComponent+startComponent
            conditions["bucketTable"] = "vs"

            for stat in playerStatList:
                conditions["stat_id"] = stat.statId
                conditions["off_def"] = "defense"

                totals = [x[0] for x in db.curs.execute(allAvgCmd.format(conditions)).fetchall()]
                
                formatting = calcItemList(totals, conditions.copy())
                
                try:
                    db.insert(vsTotalsTable, formatting)
                except IntegrityError:
                    pass


def setTeamBaselines(db):
    ##  For each team_id in database
    for teamId in [x[0] for x in db.curs.execute("SELECT team_id FROM pro_teams").fetchall()]:
        gameStats = teamGameStats(TeamStat.teamProj, db, teamId)
        for stat in teamStatList:
            for timeFrame, homeAway in getGameConstraints():
                gameGroup = gameStats["{}-{}".format(timeFrame,homeAway)]                
                conditions = gameGroup["conditions"].copy()
                conditions["stat_id"] = stat.statId
                for off_def in ("offense", "defense"):
                    conditions["off_def"] = off_def
                    results = [stat.computeGame(game, off_def) for game in gameGroup["stats"]]
                    formatting = calcItemList(results, conditions.copy())
                    if formatting["num"]:
                        try:
                            db.insert(teamTotalsTable, formatting)
                        except IntegrityError:
                            pass


def setTeamVsBaselines(db):
    ##  For each team_id in database
    for teamId in [x[0] for x in db.curs.execute("SELECT team_id FROM pro_teams").fetchall()]:
        vsStats = teamVsStats(TeamStat.teamProj, db, teamId)

        for pos, starter in getPlayerConditions():
            posComponent = "_{}".format(pos) if pos else ""
            startComponent = "_{}".format(starter) if starter else ""

            for stat in playerStatList:
                      
                for timeFrame, homeAway in getGameConstraints():
                    gameGroup = vsStats["{}-{}".format(timeFrame,homeAway)+"-player"+posComponent+startComponent]                  
                    conditions = gameGroup["conditions"].copy()
                    conditions["stat_id"] = stat.statId

                    conditions["off_def"] = "defense"
                    results = [stat.computeGame(game) for game in gameGroup["stats"]]
                    formatting = calcItemList(results, conditions.copy())
                    if formatting["num"]:
                        try:
                            db.insert(vsTotalsTable, formatting)
                        except IntegrityError:
                            pass
                        

def setTeamBuckets(db):
    ##  For each team_id in database
    for teamId in [x[0] for x in db.curs.execute("SELECT team_id FROM pro_teams").fetchall()]:
        for conditions in getGameConditions(itemId=teamId):
            conditions["bucketTable"] = "team"
            conditions["proj_id"] = "team"
            conditions["check_id"] = "team"

            for stat in teamStatList:
                conditions["stat_id"] = stat.statId

                for off_def in ("offense", "defense"):
                    conditions["off_def"] = off_def
                    formatting = getNewBucket(db, conditions.copy())
                    try:
                        db.insert(teamBucketTable, formatting)
                    except IntegrityError:
                        pass


def setTeamVsBuckets(db):
    ##  For each team_id in database
    for teamId in [x[0] for x in db.curs.execute("SELECT team_id FROM pro_teams").fetchall()]:
        for pos, starter in getPlayerConditions():
            posComponent = "_{}".format(pos) if pos else ""
            startComponent = "_{}".format(starter) if starter else ""
      
            for conditions in getGameConditions(itemId=teamId):
                conditions["bucketTable"] = "vs"
                conditions["proj_id"] = "team_vs_player"+posComponent+startComponent
                conditions["check_id"] = "team_vs_player"+posComponent+startComponent

                for stat in playerStatList:
                    conditions["stat_id"] = stat.statId

                    conditions["off_def"] = "defense"
                    formatting = getNewBucket(db, conditions.copy())
                    try:
                        db.insert(vsBucketTable, formatting)
                    except IntegrityError:
                        pass


def teamGameStats(proj, db, teamId, team=None):
    gameStats = {}
    for conditions in getGameConditions(itemId=teamId):
        label = conditions["label"]
        conditions["item_type"] = proj["item_type"]
        conditions["proj_id"] = proj["proj_id"]
        conditions["check_id"] = proj["check_id"]
        conditions["bucketTable"] = proj["bucketTable"]
        conditions["oppJoin"] = oppJoin
        conditions["gameGroup"] = proj["gameGroup"]
        conditions["posJoin"] = ""
        conditions["selectCmd"] = ", ".join(["stats.{0}, opp.{0}".format(x) for x in teamStatAbrvs])
        if proj["gameGroup"]:
            conditions["whereCmd"] = proj["whereCmd"](teamId, getGICmd(proj["gameGroup"](team)))
        else:
            conditions["whereCmd"] = proj["whereCmd"](teamId)

        newGroup = {}
        newGroup["conditions"] = conditions.copy()
        newGroup["stats"] = db.curs.execute(selectStatsCmd.format(conditions)).fetchall()
        gameStats[label] = newGroup.copy()

    return gameStats


def teamVsStats(proj, db, teamId, team=None):
    gameStats = {}

    for pos, starter in getPlayerConditions():
        posComponent = "_{}".format(pos) if pos else ""
        startComponent = "_{}".format(starter) if starter else ""
        posWhere = getPosWhere(pos) if pos else ""
        startWhere = " AND starter = {}".format(starter) if starter else ""
        
        for conditions in getGameConditions(itemId=teamId):
            label = conditions["label"] + "-player"+posComponent+startComponent
            vsConditions = conditions.copy()
            vsConditions["item_type"] = "player"
            vsConditions["proj_id"] = proj["proj_id"]+"_vs_player"+posComponent+startComponent
            vsConditions["check_id"] = proj["check_id"]+"_vs_player"+posComponent+startComponent
            vsConditions["bucketTable"] = "vs"
            vsConditions["posJoin"] = posJoin
            vsConditions["oppJoin"] = ""
            vsConditions["selectCmd"] = ", ".join(["stats.{0}".format(x) for x in playerStatAbrvs])
            if proj["gameGroup"]:
                vsConditions["whereCmd"] = "WHERE stats.opp_id = {0[teamId]}{0[posWhere]}{0[startWhere]} AND {0[giCmd]}".format({"teamId":teamId, "posWhere":posWhere, "startWhere":startWhere, "giCmd":getGICmd(proj["gameGroup"](team))})
            else:
                vsConditions["whereCmd"] = "WHERE stats.opp_id = {0[teamId]}{0[posWhere]}{0[startWhere]}".format({"teamId":teamId, "posWhere":posWhere, "startWhere":startWhere})
            newGroup = {}
            newGroup["conditions"] = vsConditions.copy()
            newGroup["stats"] = db.curs.execute(selectStatsCmd.format(vsConditions)).fetchall()

            gameStats[label] = newGroup.copy()
    return gameStats





def playerGameStats(proj, db, playerId, player=None):
    gameStats = {}

    for pos, starter in getPlayerConditions(db, playerId):
        posComponent = "_{}".format(pos) if pos else ""
        startComponent = "_{}".format(starter) if starter else ""
        posWhere = getPosWhere(pos) if pos else ""
        startWhere = " AND starter = {}".format(starter) if starter else ""
        
        for conditions in getGameConditions(itemId=playerId):
            label = conditions["label"]+"-player"+posComponent+startComponent
            newConditions = conditions.copy()
            newConditions["item_type"] = "player"
            newConditions["proj_id"] = proj["proj_id"]+posComponent+startComponent
            newConditions["check_id"] = proj["check_id"]+posComponent+startComponent
            newConditions["bucketTable"] = "player"
            newConditions["posJoin"] = posJoin
            newConditions["oppJoin"] = ""
            newConditions["selectCmd"] = ", ".join(["stats.{0}".format(x) for x in playerStatAbrvs])
            whereCmd = ""

            if proj["gameGroup"]:
                whereCmd = proj["whereCmd"](playerId, getGICmd(proj["gameGroup"](player)))
            else:
                whereCmd = proj["whereCmd"](playerId)
            
            newConditions["whereCmd"] = whereCmd + " {0[posWhere]}{0[startWhere]}".format({"playerId":playerId, "posWhere":posWhere, "startWhere":startWhere})

            newGroup = {}
            newGroup["conditions"] = newConditions.copy()
            newGroup["stats"] = db.curs.execute(selectStatsCmd.format(newConditions)).fetchall()

            gameStats[label] = newGroup.copy()
    return gameStats


                        
def setPlayerBaselines(db):
    ##  For each player_id that played this season
    for playerId in [x[0] for x in db.curs.execute("SELECT DISTINCT player_id FROM player_stats AS stats INNER JOIN ({0[gdCmd]}) AS gd ON stats.game_id = gd.game_id".format({"gdCmd": seasonCmd})).fetchall()]:
        gameStats = playerGameStats(PlayerStat.teamProj, db, playerId)

        for pos, starter in getPlayerConditions(db, playerId):
            posComponent = "_{}".format(pos) if pos else ""
            startComponent = "_{}".format(starter) if starter else ""

            for stat in playerStatList:
        
                for timeFrame, homeAway in getGameConstraints():
                    gameGroup = gameStats["{}-{}".format(timeFrame,homeAway)+"-player"+posComponent+startComponent]                 
                    conditions = gameGroup["conditions"].copy()
                    conditions["stat_id"] = stat.statId
                    conditions["off_def"] = "offense"
                    
                    results = [stat.computeGame(game) for game in gameGroup["stats"]]
                    formatting = calcItemList(results, conditions.copy())
                    if formatting["num"]:
                        try:
                            db.insert(playerTotalsTable, formatting)
                        except IntegrityError:
                            pass


def makePlayerBuckets(db):
    for pos, starter in getPlayerConditions():
        posComponent = "_{}".format(pos) if pos else ""
        startComponent = "_{}".format(starter) if starter else ""
      
        for conditions in getGameConditions():
            conditions["proj_id"] = "team_player"+posComponent+startComponent
            conditions["bucketTable"] = "player"

            for stat in playerStatList:
                conditions["stat_id"] = stat.statId
                conditions["off_def"] = "offense"

                totals = [x[0] for x in db.curs.execute(allAvgCmd.format(conditions)).fetchall()]
                formatting = calcItemList(totals, conditions.copy())
                try:
                    db.insert(playerTotalsTable, formatting)
                except IntegrityError:
                    pass


def setPlayerBuckets(db):
    ##  For each player_id that played this season
    for playerId in [x[0] for x in db.curs.execute("SELECT DISTINCT player_id FROM player_stats AS stats INNER JOIN ({0[gdCmd]}) AS gd ON stats.game_id = gd.game_id".format({"gdCmd": seasonCmd})).fetchall()]:
        for pos, starter in getPlayerConditions(db, playerId):
            posComponent = "_{}".format(pos) if pos else ""
            startComponent = "_{}".format(starter) if starter else ""
      
            for conditions in getGameConditions(itemId=playerId):
                conditions["bucketTable"] = "player"
                conditions["proj_id"] = "team_player"+posComponent+startComponent
                conditions["check_id"] = "team_player"+posComponent+startComponent

                for stat in playerStatList:
                    conditions["stat_id"] = stat.statId

                    conditions["off_def"] = "offense"
                    formatting = getNewBucket(db, conditions.copy())
                    if formatting["bucket"] != "n/a":
                        try:
                            db.insert(playerBucketTable, formatting)
                        except IntegrityError:
                            pass


#################################################################################


class Stat:


    def __init__(self):

        self.db = None


    def computeGame(game, off_def):
        raise AssertionError


    def crunchNumbers(self):
        for proj in self.getProjections():
            if "lineup" in proj["proj_id"]:
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
            self.db.conn.commit()


    def getB2bGames(self):
        raise AssertionError


    def getProjections(self):
        raise AssertionError


    def getMatchupGames(self):
        raise AssertionError


    def negotiate(self, formatting):
        raise AssertionError


    def setDB(self, db):
        self.db = db


    def setB2bStats(self, proj):
        raise AssertionError


    def setLineupStats(self, proj):
        raise AssertionError


    def setMatchupStats(self, proj):
        raise AssertionError


    def setStats(self, proj):
        raise AssertionError
        

###############################################


class TeamStat(Stat):

    teamProj = {"bucketTable":"team", "check_id":"team", "gameGroup":None, "item_type":"team", "oppJoin":"", "posJoin":"", "proj_id":"team", "whereCmd": lambda teamId: "WHERE stats.team_id = {}".format(teamId)}
    lineupProj = {"bucketTable":"team", "check_id":"team", "gameGroup":lambda team: team.getLineupGames(), "item_type":"team", "oppJoin":"", "posJoin":"", "proj_id":"lineup", "whereCmd": lambda teamId, giCmd: "WHERE stats.team_id = {}".format(teamId) + " AND {}".format(giCmd)}
    projections = (teamProj, lineupProj,)
                       
    def __init__(self, team):
        self.team = team
        self.statProj = {}
        self.estTotal = {}
        super().__init__()


    def addToTotal(self, label, value):
        total = self.estTotal.get(label,0)
        self.estTotal[label] = total + value


    def getJson(self):
        jsonDict = {"statId":self.getStatId(),
                    "statProj":self.statProj,
                    "estTotal":self.estTotal}        
        return jsonDict


    def getB2bGames(self):
        return self.team.getB2bGames()


    def getForPlayerProj(self, label):
        answer = None
        try:
            answer = self.statProj[label]
        except KeyError:
            newLabel = "-".join( label.split("-")[1:] )
            if "team" in label:
                newLabel = "team-"+newLabel
            else:
                newLabel = "lineup-"+newLabel
            self.statProj[label] = self.statProj[newLabel]
            answer = self.statProj[label]
        return answer


    def getProjections(self):
        return TeamStat.projections


    def getMatchupGames(self):
        return self.team.getMatchupGames()


    def getStatProj(self, label):
        return self.statProj[label]


    def getTotal(self, label):
        return self.estTotal[label]


    def negotiate(self, formatting):
        # Initiate variables
        totals = []
        index = 3
        result = 0

##        print(formatting["label"])
        formatting["item_type"] = "team"
        formatting["off_def"] = "offense"
        formatting["stat_id"] = self.getStatId()
        
        dFormatting = formatting.copy()
        dFormatting["item_id"] = self.team.getOppId()
        dFormatting["off_def"] = "defense"
        if dFormatting["home_away"] != "all":
            dFormatting["home_away"] = "away" if formatting["home_away"] == "home" else "home"

        teamResult = self.db.curs.execute(negotiateCmd.format(formatting)).fetchone()
##        print(teamNegotiateCmd.format(formatting))
##        print("\n\nteamResult")
##        print(teamResult)
        

        oppResult =  self.db.curs.execute(negotiateCmd.format(dFormatting)).fetchone()
##        print(teamNegotiateCmd.format(dFormatting))
##        print("\noppResult")
##        print(oppResult)


        matchFormat = formatting.copy()
        matchFormat["proj_id"] = "matchup_{}".format(formatting["proj_id"])
        matchResult = self.db.curs.execute(negotiateCmd.format(matchFormat)).fetchone()
##        print(teamNegotiateCmd.format(matchFormat))
##        print("\nmatchResult")
##        print(matchResult)


        b2bFormat = formatting.copy()
        b2bFormat["proj_id"] = "b2b_{}".format(formatting["proj_id"])
        b2bResult = self.db.curs.execute(negotiateCmd.format(b2bFormat)).fetchone()
##        print(teamNegotiateCmd.format(b2bFormat))
##        print("\nb2bResult")
##        print(b2bResult)


        b2bDFormat = dFormatting.copy()
        b2bDFormat["proj_id"] = "b2b_vs_{}".format(formatting["proj_id"])
        b2bDResult = self.db.curs.execute(negotiateCmd.format(b2bDFormat)).fetchone()
##        print(teamNegotiateCmd.format(b2bDFormat))
##        print("\nb2bDResult")
##        print(b2bDResult)


        simOffFormat = formatting.copy()
        simOffFormat["proj_id"] = "similar_vs_{}".format(formatting["proj_id"])
        simOffResult = self.db.curs.execute(negotiateCmd.format(simOffFormat)).fetchone()
##        print(teamNegotiateCmd.format(simOffFormat))
##        print("\nsimOffResult")
##        print(simOffResult)


        simDefFormat = dFormatting.copy()
        simDefFormat["proj_id"] = "vs_similar_{}".format(formatting["proj_id"])
        simDefResult = self.db.curs.execute(negotiateCmd.format(simDefFormat)).fetchone()
##        print(teamNegotiateCmd.format(simDefFormat))
##        print("\nsimDefResult")
##        print(simDefResult)



        simFormat = formatting.copy()
        simFormat["proj_id"] = "similar_{}".format(formatting["proj_id"])
        simResult = self.db.curs.execute(negotiateCmd.format(simFormat)).fetchone()
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


    def setB2bStats(self, proj):
        if self.db.curs.execute("SELECT stat_avg FROM team_totals WHERE proj_id = 'b2b_{}' AND item_id = ? AND stat_id = ?".format(proj["proj_id"]), (self.team.getTeamId(), self.getStatId())).fetchone() == None:
       
            gameStats = teamGameStats(proj, self.db, self.team.getTeamId(), self.team)
            for stat in teamStatList:
                for timeFrame, homeAway in getGameConstraints(self.team.getHomeAway()):
                    gameGroup = gameStats["{}-{}".format(timeFrame,homeAway)]                
                    conditions = gameGroup["conditions"].copy()
                    conditions["proj_id"] = "b2b_"+conditions["proj_id"]
                    conditions["stat_id"] = stat.statId
                    conditions["off_def"] = "offense"
                    if proj["gameGroup"]:
                        games = tuple(set(self.team.getB2bGames()).intersection(set(conditions["gameGroup"](self.team))))
                    else:
                        games = self.team.getB2bGames()

                    
                    conditions["whereCmd"] = "WHERE stats.team_id = {}".format(self.team.getTeamId()) + " AND {}".format(getGICmd(games))
                    results = [stat.computeGame(game, "offense") for game in self.db.curs.execute(selectStatsCmd.format(conditions)).fetchall()]
                    formatting = calcItemList(results, conditions.copy())

                    if formatting["num"]:
                        try:
                            self.db.insert(teamTotalsTable, formatting)
                        except IntegrityError:
                            pass
                        bucketFormatting = getNewBucket(self.db, conditions.copy())
                        try:
                            self.db.insert(teamBucketTable, bucketFormatting)
                        except IntegrityError:
                            pass


    def setB2bVsStats(self, proj):
        if self.db.curs.execute("SELECT stat_avg FROM vs_totals WHERE proj_id = 'b2b_vs_{}' AND item_id = ? AND stat_id = ?".format(proj["proj_id"]), (self.team.getTeamId(), self.getStatId())).fetchone() == None:
       
            vsStats = teamVsStats(proj, self.db, self.team.getTeamId(), self.team)

            for pos, starter in getPlayerConditions():
                posComponent = "_{}".format(pos) if pos else ""
                startComponent = "_{}".format(starter) if starter else ""

                for stat in playerStatList:
                          
                    for timeFrame, homeAway in getGameConstraints(self.team.getHomeAway()):
                        gameGroup = vsStats["{}-{}".format(timeFrame,homeAway)+"-player"+posComponent+startComponent]                  
                        vsConditions = gameGroup["conditions"].copy()
                        vsConditions["proj_id"] = "b2b_vs_"+vsConditions["proj_id"]
                        vsConditions["stat_id"] = stat.statId
                        vsConditions["off_def"] = "defense"

                        if proj["gameGroup"]:
                            games = tuple(set(self.team.getB2bGames()).intersection(set(proj["gameGroup"](self.team))))
                        else:
                            games = self.team.getB2bGames()

                        
                        vsConditions["whereCmd"] = "WHERE stats.opp_id = {}".format(self.team.getTeamId()) + " AND {}".format(getGICmd(games))

                        results = [stat.computeGame(game) for game in self.db.curs.execute(selectStatsCmd.format(vsConditions)).fetchall()]
                        formatting = calcItemList(results, vsConditions.copy())
                        if formatting["num"]:
                            try:
                                self.db.insert(vsTotalsTable, formatting)
                            except IntegrityError:
                                pass
                            bucketFormatting = getNewBucket(self.db, vsConditions.copy())
                            try:
                                self.db.insert(vsBucketTable, bucketFormatting)
                            except IntegrityError:
                                pass


    def setMatchupStats(self, proj):
        if self.db.curs.execute("SELECT stat_avg FROM team_totals WHERE proj_id = 'matchup_{}' AND item_id = ? AND stat_id = ?".format(proj["proj_id"]), (self.team.getTeamId(), self.getStatId())).fetchone() == None:
       
            gameStats = teamGameStats(proj, self.db, self.team.getTeamId(), self.team)
            for stat in teamStatList:
                for timeFrame, homeAway in getGameConstraints(self.team.getHomeAway()):
                    gameGroup = gameStats["{}-{}".format(timeFrame,homeAway)]                
                    conditions = gameGroup["conditions"].copy()
                    conditions["proj_id"] = "matchup_"+conditions["proj_id"]
                    conditions["stat_id"] = stat.statId
                    conditions["off_def"] = "offense"
                    if proj["gameGroup"]:                    
                        games = tuple(set(self.team.getMatchupGames()).intersection(set(conditions["gameGroup"](self.team))))
                    else:
                        games = self.team.getMatchupGames()
                    
                    
                    conditions["whereCmd"] = "WHERE stats.team_id = {}".format(self.team.getTeamId()) + " AND {}".format(getGICmd(games))
                    results = [stat.computeGame(game, "offense") for game in self.db.curs.execute(selectStatsCmd.format(conditions)).fetchall()]
                    formatting = calcItemList(results, conditions.copy())

                    if formatting["num"]:
                        try:
                            self.db.insert(teamTotalsTable, formatting)
                        except IntegrityError:
                            pass
                        bucketFormatting = getNewBucket(self.db, conditions.copy())
                        try:
                            self.db.insert(teamBucketTable, bucketFormatting)
                        except IntegrityError:
                            pass
        


    def setLineupStats(self, proj):
        if self.db.curs.execute("SELECT stat_avg FROM team_totals WHERE proj_id = 'lineup' AND item_id = ? AND stat_id = ?".format(proj["proj_id"]), (self.team.getTeamId(), self.getStatId())).fetchone() == None:
       
            gameStats = teamGameStats(proj, self.db, self.team.getTeamId(), self.team)
            for stat in teamStatList:
                for timeFrame, homeAway in getGameConstraints(self.team.getHomeAway()):
                    gameGroup = gameStats["{}-{}".format(timeFrame,homeAway)]                
                    conditions = gameGroup["conditions"].copy()
                    conditions["stat_id"] = stat.statId
                    for off_def in ("offense", "defense"):
                        conditions["off_def"] = off_def
                        results = [stat.computeGame(game, off_def) for game in gameGroup["stats"]]
                        formatting = calcItemList(results, conditions.copy())
                        if formatting["num"]:
                            try:
                                self.db.insert(teamTotalsTable, formatting)
                            except IntegrityError:
                                pass
                            bucketFormatting = getNewBucket(self.db, conditions.copy())
                            try:
                                self.db.insert(teamBucketTable, bucketFormatting)
                            except IntegrityError:
                                pass


    def setLineupVsStats(self, proj):
        if self.db.curs.execute("SELECT stat_avg FROM vs_totals WHERE proj_id = 'lineup_vs_player' AND item_id = ? AND stat_id = ?".format(proj["proj_id"]), (self.team.getTeamId(), self.getStatId())).fetchone() == None:
       
            vsStats = teamVsStats(proj, self.db, self.team.getTeamId(), self.team)

            for pos, starter in getPlayerConditions():
                posComponent = "_{}".format(pos) if pos else ""
                startComponent = "_{}".format(starter) if starter else ""

                for stat in playerStatList:
                          
                    for timeFrame, homeAway in getGameConstraints(self.team.getHomeAway()):
                        gameGroup = vsStats["{}-{}".format(timeFrame,homeAway)+"-player"+posComponent+startComponent]                  
                        vsConditions = gameGroup["conditions"].copy()
                        vsConditions["stat_id"] = stat.statId
                        vsConditions["off_def"] = "defense"
                        
                        results = [stat.computeGame(game) for game in gameGroup["stats"]]
                        formatting = calcItemList(results, vsConditions.copy())
                        if formatting["num"]:
                            try:
                                self.db.insert(vsTotalsTable, formatting)
                            except IntegrityError:
                                pass
                            bucketFormatting = getNewBucket(self.db, vsConditions.copy())
                            try:
                                self.db.insert(vsBucketTable, bucketFormatting)
                            except IntegrityError:
                                pass


    def setSimilarStats(self, proj):
        if self.db.curs.execute("SELECT stat_avg FROM team_totals WHERE proj_id = 'similar_{}' AND item_id = ? AND stat_id = ?".format(proj["proj_id"]), (self.team.getTeamId(), self.getStatId())).fetchone() == None:
       
            for conditions in getGameConditions(itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
                label = conditions["label"]
                conditions["stat_id"] = self.getStatId()
                conditions["proj_id"] = proj["proj_id"]
                conditions["check_id"] = proj["check_id"]
                conditions["bucketTable"] = proj["bucketTable"]
                conditions["item_type"] = proj["item_type"]
                conditions["oppJoin"] = oppJoin
                conditions["posJoin"] = ""
                conditions["selectCmd"] = ", ".join(["stats.{0}, opp.{0}".format(x) for x in teamStatAbrvs])

                offConditions = conditions.copy()
                offConditions["off_def"] = "offense"
                offConditions["item_id"] = self.team.getTeamId()
                
                defConditions = conditions.copy()
                if defConditions["home_away"] != "all":
                    defConditions["home_away"] = "away" if conditions["home_away"] == "home" else "home"
                defConditions["off_def"] = "defense"
                defConditions["item_id"] = self.team.getOppId()


                try:
                    offBucket = self.db.curs.execute(bucketCmd.format(offConditions)).fetchone()[0]
                    offConditions["bucket"] = offBucket
                    
                    defBucket = self.db.curs.execute(bucketCmd.format(defConditions)).fetchone()[0]
                    defConditions["bucket"] = defBucket
                    
                    offTeams = tuple([x[0] for x in self.db.curs.execute(similarCmd.format(offConditions)).fetchall() if x[0] != str(self.team.getTeamId())]) 
                    defTeams = tuple([x[0] for x in self.db.curs.execute(similarCmd.format(defConditions)).fetchall() if x[0] != str(self.team.getOppId())]) 


                    teamCmd = getTeamCmd(offTeams)
                    oppCmd = getOppCmd(defTeams)
                    offConditions["proj_id"] = "similar_"+conditions["proj_id"]
                    offConditions["whereCmd"] = similarWhereCmd.format({"itemCmd":teamCmd, "oppCmd":oppCmd})

                    results = [type(self).computeGame(game, "offense") for game in self.db.curs.execute(selectStatsCmd.format(offConditions)).fetchall()]
                    formatting = calcItemList(results, offConditions.copy())
                    
                    if formatting["num"]:
                        try:
                            self.db.insert(teamTotalsTable, formatting)
                        except IntegrityError:
                            pass

                    # make similar bucket 
                    bucketFormatting = getNewBucket(self.db, offConditions.copy())
                    try:
                        self.db.insert(teamBucketTable, bucketFormatting)
                    except IntegrityError:
                        pass

                    # similar defenses vs Offense team
                    teamCmd = getTeamCmd((self.team.getTeamId(),))
                    oppCmd = getOppCmd(defTeams)
                
                    offConditions["proj_id"] = "similar_vs_"+conditions["proj_id"]
                    offConditions["whereCmd"] = similarWhereCmd.format({"itemCmd":teamCmd, "oppCmd":oppCmd})
                    
                    results = [type(self).computeGame(game, "offense") for game in self.db.curs.execute(selectStatsCmd.format(offConditions)).fetchall()]
                    formatting = calcItemList(results, offConditions.copy())
                    
                    if formatting["num"]:
                        try:
                            self.db.insert(teamTotalsTable, formatting)
                        except IntegrityError:
                            pass

                    # similar offenses vs Defense team
                    teamCmd = getTeamCmd(offTeams)
                    oppCmd = getOppCmd((self.team.getOppId(),))
                    defConditions["proj_id"] = "vs_similar_"+conditions["proj_id"]
                    defConditions["whereCmd"] = similarWhereCmd.format({"itemCmd":teamCmd, "oppCmd":oppCmd})
                    # enter into team_totals

                    results = [type(self).computeGame(game, "defense") for game in self.db.curs.execute(selectStatsCmd.format(defConditions)).fetchall()]
                    formatting = calcItemList(results, defConditions.copy())
                    
                    if formatting["num"]:
                        try:
                            self.db.insert(teamTotalsTable, formatting)
                        except IntegrityError:
                            pass

                except TypeError:
                    pass           
                except IndexError:
                    pass


    def setStats(self, proj):
        for conditions in getGameConditions(itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
            label = proj["proj_id"]+"-"+conditions["label"]
            conditions["proj_id"] = proj["proj_id"]
                
            self.statProj[label] = self.negotiate(conditions)

  
#----------------------------------------------


class FtaPerFoul(TeamStat):

    statId = "fta_per_foul"

    def __init__(self, team):
        super().__init__(team)


    def computeGame(game, off_def):
        teamIndex = 0 if off_def == "offense" else 1
        oppIndex = 1 if off_def == "offense" else 0
        
        result = 0
        fta = game[ts_proc("fta",teamIndex)]
        oppFouls = game[ts_proc("fouls",oppIndex)]
        try:
            result = fta/oppFouls
        except ZeroDivisionError:
            pass
        return result


    def getNewPlayerStat(self):
        return False


    def getStatId(self):
        return FtaPerFoul.statId


#----------------------------------------------


class Possessions(TeamStat):
    statId = "poss"

    def __init__(self, team):
        super().__init__(team)


    def computeGame(game, off_def):
        teamIndex = 0 if off_def == "offense" else 1

        result = 0
        gameMins = game[0]
        turn = game[ts_proc("turn",teamIndex)]
        fga = game[ts_proc("fga",teamIndex)]
        
        try:
            result = (turn+fga)
        except ZeroDivisionError:
            pass
        return result

        
    def getNewPlayerStat(self):
        return False


    def getStatId(self):
        return Possessions.statId


    def setStats(self, proj):
        for conditions in getGameConditions(itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
            label = proj["proj_id"]+"-"+conditions["label"]
            conditions["proj_id"] = proj["proj_id"]
                
            self.statProj[label] = round(self.negotiate(conditions))


#----------------------------------------------


class Team2ptAttempt(TeamStat):
    
    statId = "2pta"

    def __init__(self, team):
        super().__init__(team)


    def computeGame(game, off_def):
        teamIndex = 0 if off_def == "offense" else 1

        result = 0
        gameMins = game[0]
        fga = game[ts_proc("fga",teamIndex)]
        tpa = game[ts_proc("tpa",teamIndex)]
        try:
            result = fga-tpa
        except ZeroDivisionError:
            pass
        return result

        
    def getNewPlayerStat(self):
        newStat = Player2ptAttempt(self)
        return newStat


    def getStatId(self):
        return Team2ptAttempt.statId


##    def setStats(self, proj):
##        for conditions in getGameConditions(itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
##            conditions["proj_id"] = proj["proj_id"]
##            label = proj["proj_id"]+"-"+conditions["label"]
##            oppLabel = getOppLabel(label)
##
##            poss = self.team.teamStats["poss"].getStatProj(label)
##            turn = self.team.teamStats["turn"].getStatProj(label)
##            fga = poss - turn 
##        
##            threePerFga = self.team.teamStats["3pt_per_fga"].getStatProj(label)
##
##            self.statProj[label] = round(fga-(fga * threePerFga))


#----------------------------------------------

class Team2ptMade(TeamStat):

    statId = "2ptm"

    def __init__(self, team):
        super().__init__(team)


    def computeGame(game, off_def):
        teamIndex = 0 if off_def == "offense" else 1
        
        result = 0
        gameMins = game[0]
        fgm = game[ts_proc("fgm",teamIndex)]
        tpm = game[ts_proc("tpm",teamIndex)]
        try:
            result = fgm-tpm
        except ZeroDivisionError:
            pass
        return result


    def getNewPlayerStat(self):
        newStat = Player2ptMade(self)
        return newStat


    def getStatId(self):
        return Team2ptMade.statId


    def setStats(self, proj):
        
        for conditions in getGameConditions(itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
    
            for player in chain(self.team.starters, self.team.bench):
                
                for pos, starter in getPlayerConditions(player=player):
                    posLabelComponent = "_pos" if pos else ""
                    startLabelComponent = "_start"

                    label = proj["proj_id"]+"_player"+posLabelComponent+startLabelComponent+"-"+conditions["label"]
                    twoMade = player.playerStats["2ptm"].getStatAdj(label)
                    
                    statValue = self.statProj.get(label, 0)
                    statValue += twoMade
                    self.statProj[label] = statValue                
                


#----------------------------------------------

class Team2ptPct(TeamStat):

    statId = "2pt_pct"

    def __init__(self, team):
        super().__init__(team)


    def computeGame(game, off_def):
        teamIndex = 0 if off_def == "offense" else 1
        
        result = 0
        gameMins = game[0]
        fga = game[ts_proc("fga",teamIndex)]
        fgm = game[ts_proc("fgm",teamIndex)]
        tpa = game[ts_proc("tpa",teamIndex)]
        tpm = game[ts_proc("tpm",teamIndex)]
        twoatt = fga-tpa
        twomad = fgm-tpm
        try:
            result = twomad/twoatt
        except ZeroDivisionError:
            pass
        return result


    def getNewPlayerStat(self):
        newStat = Player2ptPct(self)
        return newStat

   
    def getStatId(self):
        return Team2ptPct.statId


#----------------------------------------------

class Team3ptAttempt(TeamStat):

    statId = "3pta"

    def __init__(self, team):
        super().__init__(team)


    def computeGame(game, off_def):
        teamIndex = 0 if off_def == "offense" else 1
        
        result = 0
        gameMins = game[0]
        tpa = game[ts_proc("tpa",teamIndex)]
        try:
            result = (tpa/gameMins)*48
        except ZeroDivisionError:
            pass
        return result


    def getNewPlayerStat(self):
        newStat = Player3ptAttempt(self)
        return newStat

   
    def getStatId(self):
        return Team3ptAttempt.statId


##    def setStats(self, proj):
##        for conditions in getGameConditions(itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
##            conditions["proj_id"] = proj["proj_id"]
##            label = proj["proj_id"]+"-"+conditions["label"]
##
##            poss = self.team.teamStats["poss"].getStatProj(label)
##            turn = self.team.teamStats["turn"].getStatProj(label)
##            fga = poss - turn
##        
##            threePerFga = self.team.teamStats["3pt_per_fga"].getStatProj(label)
##            
##            self.statProj[label] = round(fga * threePerFga)


#----------------------------------------------

class Team3ptMade(TeamStat):

    statId = "3ptm"

    def __init__(self, team):
        super().__init__(team)


    def computeGame(game, off_def):
        teamIndex = 0 if off_def == "offense" else 1
        
        result = 0
        gameMins = game[0]
        tpm = game[ts_proc("tpm",teamIndex)]
        try:
            result = (tpm/gameMins)*48
        except ZeroDivisionError:
            pass
        return result


    def getNewPlayerStat(self):
        newStat = Player3ptMade(self)
        return newStat

   
    def getStatId(self):
        return Team3ptMade.statId


    def setStats(self, proj):
        
        for conditions in getGameConditions(itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
    
            for player in chain(self.team.starters, self.team.bench):
                
                for pos, starter in getPlayerConditions(player=player):
                    posLabelComponent = "_pos" if pos else ""
                    startLabelComponent = "_start"

                    label = proj["proj_id"]+"_player"+posLabelComponent+startLabelComponent+"-"+conditions["label"]
                    threeMade = player.playerStats["3ptm"].getStatAdj(label)
                    statValue = self.statProj.get(label, 0)
                    statValue += threeMade
                    self.statProj[label] = statValue          




#----------------------------------------------

class Team3ptPct(TeamStat):

    statId = "3pt_pct"

    def __init__(self, team):
        super().__init__(team)


    def computeGame(game, off_def):
        teamIndex = 0 if off_def == "offense" else 1
        
        result = 0
        gameMins = game[0]
        tpa = game[ts_proc("tpa",teamIndex)]
        tpm = game[ts_proc("tpm",teamIndex)]
        try:
            result = tpm/tpa
        except ZeroDivisionError:
            pass
        return result


    def getNewPlayerStat(self):
        newStat = Player3ptPct(self)
        return newStat

   
    def getStatId(self):
        return Team3ptPct.statId


#----------------------------------------------

class Team3ptPerFga(TeamStat):

    statId = "3pt_per_fga"

    def __init__(self, team):
        super().__init__(team)


    def computeGame(game, off_def):
        teamIndex = 0 if off_def == "offense" else 1
        
        result = 0
        gameMins = game[0]
        fga = game[ts_proc("fga",teamIndex)]
        tpa = game[ts_proc("tpa",teamIndex)]
        try:
            result = tpa/fga
        except ZeroDivisionError:
            pass
        return result


    def getNewPlayerStat(self):
        return None

   
    def getStatId(self):
        return Team3ptPerFga.statId


#----------------------------------------------

class TeamAssists(TeamStat):

    statId = "ast"

    def __init__(self, team):
        super().__init__(team)


    def computeGame(game, off_def):
        teamIndex = 0 if off_def == "offense" else 1
        
        result = 0
        gameMins = game[0]
        ast= game[ts_proc("ast",teamIndex)]
        try:
            result = ast
        except ZeroDivisionError:
            pass
        return result


    def getNewPlayerStat(self):
        newStat = PlayerAssists(self)
        return newStat

   
    def getStatId(self):
        return TeamAssists.statId


    def setStats(self, proj):
        for conditions in getGameConditions(itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
            for posLabelComponent in ("", "_pos"):
                for startLabelComponent  in ("_start",):
                    
                    label = proj["proj_id"]+"_player"+posLabelComponent+startLabelComponent+"-"+conditions["label"]
                    
                    astPer = self.team.teamStats["ast_per_fgm"].getForPlayerProj(label)
                    fgm = self.team.teamStats["fgm"].getStatProj(label)
                    
                    self.statProj[label] = round(fgm * astPer)


#----------------------------------------------

class TeamAssistsPerFgm(TeamStat):

    statId = "ast_per_fgm"

    def __init__(self, team):
        super().__init__(team)


    def computeGame(game, off_def):
        teamIndex = 0 if off_def == "offense" else 1
        
        result = 0
        gameMins = game[0]
        ast = game[ts_proc("ast",teamIndex)]
        fgm = game[ts_proc("fgm",teamIndex)]
        try:
            result = ast/fgm
        except ZeroDivisionError:
            pass
        return result


    def getNewPlayerStat(self):
        return False

   
    def getStatId(self):
        return TeamAssistsPerFgm.statId


#----------------------------------------------


class TeamBlocks(TeamStat):

    statId = "blk"

    def __init__(self, team):
        super().__init__(team)


    def computeGame(game, off_def):
        teamIndex = 0 if off_def == "offense" else 1
        
        result = 0
        gameMins = game[0]
        blk = game[ts_proc("blk",teamIndex)]
        try:
            result = blk
        except ZeroDivisionError:
            pass
        return result


    def getNewPlayerStat(self):
        newStat = PlayerBlocks(self)
        return newStat

   
    def getStatId(self):
        return TeamBlocks.statId


    def setStats(self, proj):
        for conditions in getGameConditions(itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
            label = proj["proj_id"]+"-"+conditions["label"]
            conditions["proj_id"] = proj["proj_id"]
            oppLabel = getOppLabel(label)

            blkPer = self.team.teamStats["blk_per_fga"].getStatProj(label)
            fga = self.team.matchup.getOpp(self.team).teamStats["fga"].getStatProj(oppLabel)
            
            self.statProj[label] = round(fga * blkPer)

            


#----------------------------------------------


class TeamBlocksPerFga(TeamStat):

    statId = "blk_per_fga"

    def __init__(self, team):
        super().__init__(team)


    def computeGame(game, off_def):
        teamIndex = 0 if off_def == "offense" else 1
        oppIndex = 1 if off_def == "offense" else 0
        
        result = 0
        gameMins = game[0]
        blk = game[ts_proc("blk",teamIndex)]
        oppFga = game[ts_proc("fga",oppIndex)]
        try:
            result = blk/oppFga
        except ZeroDivisionError:
            pass
        return result


    def getNewPlayerStat(self):
        return None

   
    def getStatId(self):
        return TeamBlocksPerFga.statId


#----------------------------------------------


class TeamDReb(TeamStat):

    statId = "dreb"

    def __init__(self, team):
        super().__init__(team)


    def computeGame(game, off_def):
        teamIndex = 0 if off_def == "offense" else 1
        
        result = 0
        gameMins = game[0]
        dreb = game[ts_proc("dreb",teamIndex)]
        try:
            result = dreb
        except ZeroDivisionError:
            pass
        return result


    def getNewPlayerStat(self):
        newStat = PlayerDReb(self)
        return newStat

   
    def getStatId(self):
        return TeamDReb.statId


    def setStats(self, proj):
        for conditions in getGameConditions(itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
            for posLabelComponent in ("", "_pos"):
                for startLabelComponent  in ("_start",):
                    
                    label = proj["proj_id"]+"_player"+posLabelComponent+startLabelComponent+"-"+conditions["label"]
                    oppLabel = getOppLabel(label)
                    drebPer = self.team.teamStats["dreb_per_miss"].getForPlayerProj(label)
                    fga = self.team.matchup.getOpp(self.team).teamStats["fga"].getForPlayerProj(oppLabel)
                    fgm = self.team.matchup.getOpp(self.team).teamStats["fgm"].getStatProj(oppLabel)
                    
                    self.statProj[label] = round((fga-fgm) * drebPer)


#----------------------------------------------


class TeamDRebPerMiss(TeamStat):

    statId = "dreb_per_miss"

    def __init__(self, team):
        super().__init__(team)


    def computeGame(game, off_def):
        teamIndex = 0 if off_def == "offense" else 1
        oppIndex = 1 if off_def == "offense" else 0
        
        result = 0
        gameMins = game[0]
        dreb = game[ts_proc("dreb",teamIndex)]
        oppFga =  game[ts_proc("fga",oppIndex)]
        oppFgm =  game[ts_proc("fgm",oppIndex)]
        try:
            result = dreb/(oppFga - oppFgm)
        except ZeroDivisionError:
            pass
        return result


    def getNewPlayerStat(self):
        return None

   
    def getStatId(self):
        return TeamDRebPerMiss.statId


#----------------------------------------------


class TeamFga(TeamStat):

    statId = "fga"

    def __init__(self, team):
        super().__init__(team)


    def computeGame(game, off_def):
        teamIndex = 0 if off_def == "offense" else 1
        
        result = 0
        gameMins = game[0]
        fga = game[ts_proc("fga",teamIndex)]
        try:
            result = fga
        except ZeroDivisionError:
            pass
        return result


    def getNewPlayerStat(self):
        newStat = PlayerFga(self)
        return newStat

   
    def getStatId(self):
        return TeamFga.statId


    def setStats(self, proj):
        for conditions in getGameConditions(itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
            label = proj["proj_id"]+"-"+conditions["label"]
            conditions["proj_id"] = proj["proj_id"]

            twoPta = self.team.teamStats["2pta"].getStatProj(label)
            threePta = self.team.teamStats["3pta"].getStatProj(label)
            
            self.statProj[label] = round(twoPta + threePta)


#----------------------------------------------


class TeamFgm(TeamStat):

    statId = "fgm"

    def __init__(self, team):
        super().__init__(team)


    def computeGame(game, off_def):
        teamIndex = 0 if off_def == "offense" else 1
        
        result = 0
        gameMins = game[0]
        fgm = game[ts_proc("fgm",teamIndex)]
        try:
            result = fgm
        except ZeroDivisionError:
            pass
        return result


    def getNewPlayerStat(self):
        newStat = PlayerFgm(self)
        return newStat

   
    def getStatId(self):
        return TeamFgm.statId


    def setStats(self, proj):
        
        for conditions in getGameConditions(itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
    
            for player in chain(self.team.starters, self.team.bench):
                
                for pos, starter in getPlayerConditions(player=player):
                    posLabelComponent = "_pos" if pos else ""
                    startLabelComponent = "_start"

                    label = proj["proj_id"]+"_player"+posLabelComponent+startLabelComponent+"-"+conditions["label"]
                    twoMade = player.playerStats["2ptm"].getStatAdj(label)
                    threeMade = player.playerStats["3ptm"].getStatAdj(label)
                    statValue = self.statProj.get(label, 0)
                    statValue += twoMade + threeMade
                    self.statProj[label] = statValue               


    

#----------------------------------------------


class TeamFta(TeamStat):

    statId = "fta"

    def __init__(self, team):
        super().__init__(team)


    def computeGame(game, off_def):
        teamIndex = 0 if off_def == "offense" else 1
        
        result = 0
        gameMins = game[0]
        fta = game[ts_proc("fta",teamIndex)]
        try:
            result = (fta/gameMins)*48
        except ZeroDivisionError:
            pass
        return result


    def getNewPlayerStat(self):
        newStat = PlayerFta(self)
        return newStat

   
    def getStatId(self):
        return TeamFta.statId


    def setStats(self, proj):
        for conditions in getGameConditions(itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
            label = proj["proj_id"]+"-"+conditions["label"]
            conditions["proj_id"] = proj["proj_id"]
            oppLabel = getOppLabel(label)
            
            ftaPer = self.team.teamStats["fta_per_foul"].getStatProj(label)
            fouls = self.team.matchup.getOpp(self.team).teamStats["fouls"].getStatProj(oppLabel)
            
            self.statProj[label] = round(fouls * ftaPer)


#----------------------------------------------


class TeamFtm(TeamStat):

    statId = "ftm"

    def __init__(self, team):
        super().__init__(team)


    def computeGame(game, off_def):
        teamIndex = 0 if off_def == "offense" else 1
        
        result = 0
        gameMins = game[0]
        ftm = game[ts_proc("ftm",teamIndex)]
        try:
            result = ftm
        except ZeroDivisionError:
            pass
        return result


    def getNewPlayerStat(self):
        newStat = PlayerFtm(self)
        return newStat

   
    def getStatId(self):
        return TeamFtm.statId


    def setStats(self, proj):
        
        for conditions in getGameConditions(itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
    
            for player in chain(self.team.starters, self.team.bench):
                
                for pos, starter in getPlayerConditions(player=player):
                    posLabelComponent = "_pos" if pos else ""
                    startLabelComponent = "_start"

                    label = proj["proj_id"]+"_player"+posLabelComponent+startLabelComponent+"-"+conditions["label"]
                    ftMade = player.playerStats["ftm"].getStatAdj(label)
                    statValue = self.statProj.get(label, 0)
                    statValue += ftMade
                    self.statProj[label] = statValue               



#----------------------------------------------


class TeamFtPct(TeamStat):

    statId = "ft_pct"

    def __init__(self, team):
        super().__init__(team)


    def computeGame(game, off_def):
        teamIndex = 0 if off_def == "offense" else 1
        
        result = 0
        gameMins = game[0]
        fta = game[ts_proc("fta",teamIndex)]
        ftm = game[ts_proc("ftm",teamIndex)]
        try:
            result = ftm/fta
        except ZeroDivisionError:
            pass
        return result


    def negotiate(self, formatting):
        # Initiate variables
        totals = []
        index = 3
        result = 0

##        print(formatting["label"])
        formatting["item_type"] = "team"
        formatting["off_def"] = "offense"
        formatting["stat_id"] = self.getStatId()
        
        dFormatting = formatting.copy()
        dFormatting["item_id"] = self.team.getOppId()
        dFormatting["off_def"] = "defense"
        if dFormatting["home_away"] != "all":
            dFormatting["home_away"] = "away" if formatting["home_away"] == "home" else "home"

        teamResult = self.db.curs.execute(negotiateCmd.format(formatting)).fetchone()
##        print(teamNegotiateCmd.format(formatting))
##        print("\n\nteamResult")
##        print(teamResult)
        
        matchFormat = formatting.copy()
        matchFormat["proj_id"] = "matchup_{}".format(formatting["proj_id"])
        matchResult = self.db.curs.execute(negotiateCmd.format(matchFormat)).fetchone()
##        print(teamNegotiateCmd.format(matchFormat))
##        print("\nmatchResult")
##        print(matchResult)


        b2bFormat = formatting.copy()
        b2bFormat["proj_id"] = "b2b_{}".format(formatting["proj_id"])
        b2bResult = self.db.curs.execute(negotiateCmd.format(b2bFormat)).fetchone()
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


    def getNewPlayerStat(self):
        newStat = PlayerFtPct(self)
        return newStat

   
    def getStatId(self):
        return TeamFtPct.statId


#----------------------------------------------


class TeamFouls(TeamStat):

    statId = "fouls"

    def __init__(self, team):
        super().__init__(team)


    def computeGame(game, off_def):
        teamIndex = 0 if off_def == "offense" else 1
        
        result = 0
        gameMins = game[0]
        fouls = game[ts_proc("fouls",teamIndex)]
        try:
            result = fouls
        except ZeroDivisionError:
            pass
        return result


    def getNewPlayerStat(self):
        newStat = PlayerFouls(self)
        return newStat

   
    def getStatId(self):
        return TeamFouls.statId


    def setStats(self, proj):
        for conditions in getGameConditions(itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
            label = proj["proj_id"]+"-"+conditions["label"]
            conditions["proj_id"] = proj["proj_id"]

            self.statProj[label] = round(self.negotiate(conditions))

            


#----------------------------------------------


class TeamMinutes(TeamStat):

    statId = "mins"

    def __init__(self, team):
        super().__init__(team)


    def computeGame(game, off_def):
        result = 0
        gameMins = game[0]
        try:
            result = gameMins
        except ZeroDivisionError:
            pass
        return result


    def crunchNumbers(self):
        pass


    def getNewPlayerStat(self):
        newStat = PlayerMinutes(self)
        return newStat


    def getStatId(self):
        return TeamMinutes.statId


    def setStats(self, proj):
        for conditions in getGameConditions(itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
            label = proj["proj_id"]+"-"+conditions["label"]
            self.statProj[label] = 48*5


    def updateMins(self, label, newMins):
        self.statProj[label] = newMins


#----------------------------------------------


class TeamOReb(TeamStat):

    statId = "oreb"

    def __init__(self, team):
        super().__init__(team)


    def computeGame(game, off_def):
        teamIndex = 0 if off_def == "offense" else 1
        
        result = 0
        gameMins = game[0]
        oreb = game[ts_proc("oreb",teamIndex)]
        try:
            result = (oreb/gameMins)*48
        except ZeroDivisionError:
            pass
        return result


    def getNewPlayerStat(self):
        newStat = PlayerOReb(self)
        return newStat

   
    def getStatId(self):
        return TeamOReb.statId


    def setStats(self, proj):
        for conditions in getGameConditions(itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
            for posLabelComponent in ("", "_pos"):
                for startLabelComponent  in ("_start",):
                    
                    label = proj["proj_id"]+"_player"+posLabelComponent+startLabelComponent+"-"+conditions["label"]

                    orebPer = self.team.teamStats["oreb_per_miss"].getForPlayerProj(label)
                    fga = self.team.teamStats["fga"].getForPlayerProj(label)
                    fgm = self.team.teamStats["fgm"].getStatProj(label)
                    
                    self.statProj[label] = round((fga-fgm) * orebPer)


#----------------------------------------------


class TeamORebPerMiss(TeamStat):

    statId = "oreb_per_miss"

    def __init__(self, team):
        super().__init__(team)


    def computeGame(game, off_def):
        teamIndex = 0 if off_def == "offense" else 1
        
        result = 0
        gameMins = game[0]
        oreb = game[ts_proc("oreb",teamIndex)]
        fga = game[ts_proc("fga",teamIndex)]
        fgm = game[ts_proc("fgm",teamIndex)]
        try:
            result = oreb/(fga-fgm)
        except ZeroDivisionError:
            pass
        return result


    def getNewPlayerStat(self):
        return None

   
    def getStatId(self):
        return TeamORebPerMiss.statId


#----------------------------------------------


class TeamPoints(TeamStat):

    statId = "points"

    def __init__(self, team):
        super().__init__(team)


    def computeGame(game, off_def):
        teamIndex = 0 if off_def == "offense" else 1
        
        result = 0
        gameMins = game[0]
        points = game[ts_proc("points",teamIndex)]
        try:
            result = points
        except ZeroDivisionError:
            pass
        return result


    def getNewPlayerStat(self):
        newStat = PlayerPoints(self)
        return newStat

   
    def getStatId(self):
        return TeamPoints.statId


    def setStats(self, proj):
        
        for conditions in getGameConditions(itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
    
            for player in chain(self.team.starters, self.team.bench):
                
                for pos, starter in getPlayerConditions(player=player):
                    posLabelComponent = "_pos" if pos else ""
                    startLabelComponent = "_start"

                    label = proj["proj_id"]+"_player"+posLabelComponent+startLabelComponent+"-"+conditions["label"]
                    twoMade = player.playerStats["2ptm"].getStatAdj(label)
                    threeMade = player.playerStats["3ptm"].getStatAdj(label)
                    ftMade = player.playerStats["ftm"].getStatAdj(label)
                    statValue = self.statProj.get(label, 0)
                    statValue += (twoMade*2) + (threeMade*3) + ftMade
                    self.statProj[label] = statValue               

            
#----------------------------------------------


class TeamSteals(TeamStat):

    statId = "stl"

    def __init__(self, team):
        super().__init__(team)


    def computeGame(game, off_def):
        teamIndex = 0 if off_def == "offense" else 1
        
        result = 0
        gameMins = game[0]
        stl = game[ts_proc("stl",teamIndex)]
        try:
            result = stl
        except ZeroDivisionError:
            pass
        return result


    def getNewPlayerStat(self):
        newStat = PlayerSteals(self)
        return newStat

   
    def getStatId(self):
        return TeamSteals.statId


    def setStats(self, proj):
        for conditions in getGameConditions(itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
            label = proj["proj_id"]+"-"+conditions["label"]
            conditions["proj_id"] = proj["proj_id"]
            oppLabel = getOppLabel(label)

            stealPer = self.team.teamStats["stl_per_turn"].getStatProj(label)
            turn = self.team.matchup.getOpp(self.team).teamStats["turn"].getStatProj(oppLabel)
            
            self.statProj[label] = round(turn * stealPer)


#----------------------------------------------


class TeamStealsPerTurn(TeamStat):

    statId = "stl_per_turn"

    def __init__(self, team):
        super().__init__(team)


    def computeGame(game, off_def):
        teamIndex = 0 if off_def == "offense" else 1
        oppIndex = 1 if off_def == "offense" else 0
        
        result = 0
        gameMins = game[0]
        stl = game[ts_proc("stl",teamIndex)]
        turn = game[ts_proc("turn",oppIndex)]
        try:
            result = stl/turn
        except ZeroDivisionError:
            pass
        return result


    def getNewPlayerStat(self):
        return None

   
    def getStatId(self):
        return TeamStealsPerTurn.statId


#----------------------------------------------


class TeamTurnovers(TeamStat):

    statId = "turn"

    def __init__(self, team):
        super().__init__(team)


    def computeGame(game, off_def):
        teamIndex = 0 if off_def == "offense" else 1
        
        result = 0
        gameMins = game[0]
        turn = game[ts_proc("turn",teamIndex)]
        try:
            result = turn
        except ZeroDivisionError:
            pass
        return result


    def getNewPlayerStat(self):
        newStat = PlayerTurnovers(self)
        return newStat

   
    def getStatId(self):
        return TeamTurnovers.statId


    def setStats(self, proj):
        for conditions in getGameConditions(itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
            label = proj["proj_id"]+"-"+conditions["label"]
            conditions["proj_id"] = proj["proj_id"]

            self.statProj[label] = round(self.negotiate(conditions))

   
###############################################


class PlayerStat(Stat):

    teamProj = {"bucketTable":"player", "check_id":"team_player", "gameGroup":None, "item_type":"player", "oppJoin":"", "posJoin":"", "proj_id":"team_player", "whereCmd": lambda playerId: "WHERE stats.player_id = {}".format(playerId)}
    lineupProj = {"bucketTable":"player", "check_id":"team_player", "gameGroup":lambda player: player.team.getLineupGames(), "item_type":"player", "oppJoin":"", "posJoin":"", "proj_id":"lineup_player", "whereCmd": lambda playerId, giCmd: "WHERE stats.player_id = {}".format(playerId) + " AND {}".format(giCmd)}
    projections = (teamProj, lineupProj, )
    
                       
    def __init__(self, teamStat):
        self.teamStat = teamStat
        self.player = None
        self.statEst = {}
        self.statAdj = {}
        super().__init__()
                               

    def getB2bGames(self):
       return self.player.team.getB2bGames()


    def getMatchupGames(self):
        return self.player.team.getMatchupGames()


    def getNewPlayerStat(self):
        return False


    def getProjections(self):
        return PlayerStat.projections


    def getStatAdj(self, label):
        return self.statAdj[label]


    def getStatEst(self, label):
        return self.statEst[label]


    def getJson(self):
        jsonDict = {"statId":self.getStatId(),
                    "statEst":self.statEst,
                    "statAdj":self.statAdj}        
        return jsonDict


    def negotiate(self, formatting):
        # Initiate variables
        totals = []
        index = 3
        result = 0

##        print(formatting["label"])
        formatting["item_type"] = "player"
        formatting["off_def"] = "offense"
        formatting["stat_id"] = self.getStatId()
        
        dFormatting = formatting.copy()
        dFormatting["item_id"] = self.player.team.getOppId()
        dFormatting["off_def"] = "defense"
        dFormatting["item_type"] = "vs"
        dFormatting["proj_id"] = sub("player","vs_player",formatting["proj_id"])
        if dFormatting["home_away"] != "all":
            dFormatting["home_away"] = "away" if formatting["home_away"] == "home" else "home"

        
        playerResult = self.db.curs.execute(negotiateCmd.format(formatting)).fetchone()
##        print(negotiateCmd.format(formatting))
##        print("\n\nplayerResult")
##        print(playerResult)
        

        oppResult =  self.db.curs.execute(negotiateCmd.format(dFormatting)).fetchone()
##        print(negotiateCmd.format(dFormatting))
##        print("\noppResult")
##        print(oppResult)


        matchFormat = formatting.copy()
        matchFormat["proj_id"] = "matchup_{}".format(formatting["proj_id"])
        matchResult = self.db.curs.execute(negotiateCmd.format(matchFormat)).fetchone()
##        print(negotiateCmd.format(matchFormat))
##        print("\nmatchResult")
##        print(matchResult)


        b2bFormat = formatting.copy()
        b2bFormat["proj_id"] = "b2b_{}".format(formatting["proj_id"])
        b2bResult = self.db.curs.execute(negotiateCmd.format(b2bFormat)).fetchone()
##        print(negotiateCmd.format(b2bFormat))
##        print("\nb2bResult")
##        print(b2bResult)


        b2bDFormat = dFormatting.copy()
        b2bDFormat["proj_id"] = "b2b_vs_{}".format(formatting["proj_id"])
        b2bDResult = self.db.curs.execute(negotiateCmd.format(b2bDFormat)).fetchone()
##        print(negotiateCmd.format(b2bDFormat))
##        print("\nb2bDResult")
##        print(b2bDResult)


        simOffFormat = formatting.copy()
        simOffFormat["proj_id"] = "similar_vs_{}".format(formatting["proj_id"])
        simOffResult = self.db.curs.execute(negotiateCmd.format(simOffFormat)).fetchone()
##        print(negotiateCmd.format(simOffFormat))
##        print("\nsimOffResult")
##        print(simOffResult)


        simDefFormat = dFormatting.copy()
        simDefFormat["item_type"] = "player"
        simDefFormat["proj_id"] = "vs_similar_{}".format(formatting["proj_id"])
        simDefResult = self.db.curs.execute(negotiateCmd.format(simDefFormat)).fetchone()
##        print(negotiateCmd.format(simDefFormat))
##        print("\nsimDefResult")
##        print(simDefResult)



        simFormat = formatting.copy()
        simFormat["proj_id"] = "similar_{}".format(formatting["proj_id"])
        simResult = self.db.curs.execute(negotiateCmd.format(simFormat)).fetchone()
##        print(negotiateCmd.format(simFormat))
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
    
        if playerResult:
            totals.append(playerResult[index])

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


    def setB2bStats(self, proj):
        if self.db.curs.execute("SELECT stat_avg FROM player_totals WHERE proj_id = 'b2b_{}' AND item_id = ? AND stat_id = ?".format(proj["proj_id"]), (self.player.getPlayerId(), self.getStatId())).fetchone() == None:
                
            gameStats = playerGameStats(proj, self.db, self.player.playerId, self.player)
            for pos, starter in getPlayerConditions(player=self.player):
                posComponent = "_{}".format(pos) if pos else ""
                startComponent = "_{}".format(starter) if starter else ""
                posWhere = getPosWhere(pos) if pos else ""
                startWhere = " AND starter = {}".format(starter) if starter else ""

                for stat in playerStatList:
                          
                    for timeFrame, homeAway in getGameConstraints(self.player.team.getHomeAway()):
                        try:
                            gameGroup = gameStats["{}-{}".format(timeFrame,homeAway)+"-player"+posComponent+startComponent]                  

                            conditions = gameGroup["conditions"].copy()
                            conditions["proj_id"] = "b2b_"+conditions["proj_id"]
                            conditions["stat_id"] = stat.statId
                            conditions["off_def"] = "offense"           
           
                            if proj["gameGroup"]:                    
                                games = tuple(set(self.player.team.getB2bGames()).intersection(set(proj["gameGroup"](self.player))))
                            else:
                                games = self.player.team.getB2bGames()

                            conditions["whereCmd"] = "WHERE stats.player_id = {0[playerId]} AND {0[giCmd]} {0[posWhere]}{0[startWhere]}".format({"playerId":self.player.playerId, "giCmd": getGICmd(games), "posWhere":posWhere, "startWhere":startWhere})
                            
                            results = [stat.computeGame(game) for game in self.db.curs.execute(selectStatsCmd.format(conditions)).fetchall()]
                            formatting = calcItemList(results, conditions.copy())
                            
                            if formatting["num"]:
                                try:
                                    self.db.insert(playerTotalsTable, formatting)
                                except IntegrityError:
                                    pass
                                bucketFormatting = getNewBucket(self.db, conditions.copy())
                                try:
                                    self.db.insert(playerBucketTable, bucketFormatting)
                                except IntegrityError:
                                    pass
                        except KeyError:
                            pass



    def setLineupStats(self, proj):
        if not self.db.curs.execute("SELECT stat_avg FROM player_totals WHERE proj_id = '{}' AND item_id = ? AND stat_id = ?".format(proj["proj_id"]), (self.player.getPlayerId(), self.getStatId())).fetchone():
            gameStats = playerGameStats(proj, self.db, self.player.playerId, self.player)
            for pos, starter in getPlayerConditions(player=self.player):
                posComponent = "_{}".format(pos) if pos else ""
                startComponent = "_{}".format(starter) if starter else ""

                for stat in playerStatList:
                          
                    for timeFrame, homeAway in getGameConstraints(self.player.team.getHomeAway()):
                        try:
                            gameGroup = gameStats["{}-{}".format(timeFrame,homeAway)+"-player"+posComponent+startComponent]                  
                            conditions = gameGroup["conditions"].copy()
                            conditions["stat_id"] = stat.statId
                            conditions["off_def"] = "offense"
                            
                            results = [stat.computeGame(game) for game in gameGroup["stats"]]
                            formatting = calcItemList(results, conditions.copy())
                            if formatting["num"]:
                                try:
                                    self.db.insert(playerTotalsTable, formatting)
                                except IntegrityError:
                                    pass
                                bucketFormatting = getNewBucket(self.db, conditions.copy())
                                try:
                                    self.db.insert(playerBucketTable, bucketFormatting)
                                except IntegrityError:
                                    pass
                        except KeyError:
                            pass


    def setMatchupStats(self, proj):
        if not self.db.curs.execute("SELECT stat_avg FROM player_totals WHERE proj_id = 'matchup_{}' AND item_id = ? AND stat_id = ?".format(proj["proj_id"]), (self.player.getPlayerId(), self.getStatId())).fetchone():
       
            gameStats = playerGameStats(proj, self.db, self.player.playerId, self.player)
            for pos, starter in getPlayerConditions(player=self.player):
                posComponent = "_{}".format(pos) if pos else ""
                startComponent = "_{}".format(starter) if starter else ""
                posWhere = getPosWhere(pos) if pos else ""
                startWhere = " AND starter = {}".format(starter) if starter else ""

                for stat in playerStatList:
                          
                    for timeFrame, homeAway in getGameConstraints(self.player.team.getHomeAway()):
                        try:
                            gameGroup = gameStats["{}-{}".format(timeFrame,homeAway)+"-player"+posComponent+startComponent]                  


                            conditions = gameGroup["conditions"].copy()
                            conditions["proj_id"] = "matchup_"+conditions["proj_id"]
                            conditions["stat_id"] = stat.statId
                            conditions["off_def"] = "offense"           
           
                            if proj["gameGroup"]:                    
                                games = tuple(set(self.player.team.getMatchupGames()).intersection(set(proj["gameGroup"](self.player))))
                            else:
                                games = self.player.team.getMatchupGames()

                            conditions["whereCmd"] = "WHERE stats.player_id = {0[playerId]} AND {0[giCmd]} {0[posWhere]}{0[startWhere]}".format({"playerId":self.player.playerId, "giCmd": getGICmd(games), "posWhere":posWhere, "startWhere":startWhere})
                            results = [stat.computeGame(game) for game in self.db.curs.execute(selectStatsCmd.format(conditions)).fetchall()]
                            formatting = calcItemList(results, conditions.copy())
                            
                            if formatting["num"]:
                                try:
                                    self.db.insert(playerTotalsTable, formatting)
                                except IntegrityError:
                                    pass
                                bucketFormatting = getNewBucket(self.db, conditions.copy())
                                try:
                                    self.db.insert(playerBucketTable, bucketFormatting)
                                except IntegrityError:
                                    pass
                        except KeyError:
                            pass


    def setSimilarStats(self, proj):
        if not self.db.curs.execute("SELECT stat_avg FROM player_totals WHERE proj_id = 'similar_{}' AND item_id = ? AND stat_id = ?".format(proj["proj_id"]), (self.player.getPlayerId(), self.getStatId())).fetchone():
       
            for conditions in getGameConditions(itemId=self.player.getPlayerId(), haConstraint=self.player.team.getHomeAway()):
                for pos, starter in getPlayerConditions(player=self.player):
                    posComponent = "_{}".format(pos) if pos else ""
                    startComponent = "_{}".format(starter) if starter else ""
        
                    label = conditions["label"]        
                    conditions["stat_id"] = self.getStatId()
                    conditions["proj_id"] = proj["proj_id"]+posComponent+startComponent
                    conditions["check_id"] = proj["check_id"]+posComponent+startComponent
                    conditions["bucketTable"] = proj["bucketTable"]
                    conditions["item_type"] = proj["item_type"]
                    conditions["oppJoin"] = ""
                    conditions["posJoin"] = ""
                    conditions["selectCmd"] = ", ".join(["stats.{0}".format(x) for x in playerStatAbrvs])
                    conditions["pos"] = pos
                    conditions["start"] = starter
                    
                    offConditions = conditions.copy()
                    offConditions["off_def"] = "offense"
                    offConditions["item_id"] = self.player.getPlayerId()
                    
                    defConditions = conditions.copy()
                    if defConditions["home_away"] != "all":
                        defConditions["home_away"] = "away" if conditions["home_away"] == "home" else "home"
                    defConditions["bucketTable"] = "vs"
                    defConditions["proj_id"] = sub("player", "vs_player", conditions["proj_id"])
                    defConditions["check_id"] = sub("player", "vs_player", conditions["check_id"])
                    defConditions["off_def"] = "defense"
                    defConditions["item_id"] = self.player.team.getOppId()

                    
                    try:
                        offBucket = self.db.curs.execute(bucketCmd.format(offConditions)).fetchone()[0]
                        offConditions["bucket"] = offBucket
                        
                        defBucket = self.db.curs.execute(bucketCmd.format(defConditions)).fetchone()[0]
                        defConditions["bucket"] = defBucket
        
                        offPlayers = tuple([x[0] for x in self.db.curs.execute(similarCmd.format(offConditions)).fetchall() if x[0] != str(self.player.getPlayerId())]) 
                        defTeams = tuple([x[0] for x in self.db.curs.execute(similarCmd.format(defConditions)).fetchall() if x[0] != str(self.player.team.getOppId())])
                        
                        playerCmd = getPlayerCmd(offPlayers)
                        oppCmd = getOppCmd(defTeams)
                        offConditions["proj_id"] = "similar_"+conditions["proj_id"]
                        offConditions["whereCmd"] = similarWhereCmd.format({"itemCmd":playerCmd, "oppCmd":oppCmd})

                        results = [type(self).computeGame(game) for game in self.db.curs.execute(selectStatsCmd.format(offConditions)).fetchall()]
                        formatting = calcItemList(results, offConditions.copy())
                        
                        if formatting["num"]:
                            try:
                                self.db.insert(playerTotalsTable, formatting)
                            except IntegrityError:
                                pass

                        # make similar bucket 
                        bucketFormatting = getNewBucket(self.db, offConditions.copy())
                        try:
                            self.db.insert(playerBucketTable, bucketFormatting)
                        except IntegrityError:
                            pass

                        # similar defenses vs Player
                        playerCmd = getPlayerCmd((self.player.getPlayerId(),))
                        oppCmd = getOppCmd(defTeams)
                    
                        offConditions["proj_id"] = "similar_vs_"+conditions["proj_id"]
                        offConditions["whereCmd"] = similarWhereCmd.format({"itemCmd":playerCmd, "oppCmd":oppCmd})
                        
                        results = [type(self).computeGame(game) for game in self.db.curs.execute(selectStatsCmd.format(offConditions)).fetchall()]
                        formatting = calcItemList(results, offConditions.copy())
                        
                        if formatting["num"]:
                            try:
                                self.db.insert(playerTotalsTable, formatting)
                            except IntegrityError:
                                pass

                        # similar offenses vs Defense team
                        playerCmd = getPlayerCmd(offPlayers)
                        oppCmd = getOppCmd((self.player.team.getOppId(),))
                        defConditions["proj_id"] = "vs_similar_"+conditions["proj_id"]
                        defConditions["whereCmd"] = similarWhereCmd.format({"itemCmd":playerCmd, "oppCmd":oppCmd})
                        # enter into team_totals

                        results = [type(self).computeGame(game) for game in self.db.curs.execute(selectStatsCmd.format(defConditions)).fetchall()]
                        formatting = calcItemList(results, defConditions.copy())
                        if formatting["num"]:
                            try:
                                self.db.insert(playerTotalsTable, formatting)
                            except IntegrityError:
                                pass

                    except TypeError:
                        pass           
                    except IndexError:
                        pass


    def setPlayer(self, player):
        self.player = player


    def setStatAdj(self, proj):
        for conditions in getGameConditions(itemId=self.player.getPlayerId(), haConstraint=self.player.team.getHomeAway()):
    
            for pos, starter in getPlayerConditions(self.player):
                posProjComponent = "_{}".format(pos) if pos else ""
                startProjComponent = "_{}".format(starter) if starter else ""
                posLabelComponent = "_pos" if pos else ""
                startLabelComponent = "_start"

                
                label = proj["proj_id"]+posLabelComponent+startLabelComponent+"-"+conditions["label"]
                if not self.teamStat.getForPlayerProj(label):
                    self.statAdj[label] = 0
                else:
                    self.statAdj[label] = round(self.teamStat.getForPlayerProj(label) * (self.statEst[label]/self.teamStat.getTotal(label)))


    def setStatEst(self, proj):


        for conditions in getGameConditions(itemId=self.player.getPlayerId(), haConstraint=self.player.team.getHomeAway()):
    
            for pos, starter in getPlayerConditions(player=self.player):
                posProjComponent = "_{}".format(pos) if pos else ""
                startProjComponent = "_{}".format(starter) if starter else ""
                posLabelComponent = "_pos" if pos else ""
                startLabelComponent = "_start" 

                label = proj["proj_id"]+posLabelComponent+startLabelComponent+"-"+conditions["label"]
                conditions["proj_id"] = proj["proj_id"]+posProjComponent+startProjComponent

                minutes = self.player.playerStats["mins"].getStatAdj(label)


                try:
                    self.statEst[label] = self.negotiate(conditions)
                    self.teamStat.addToTotal(label, self.statEst[label])
                except TypeError:
                    self.statEst[label] = 0        
  

#----------------------------------------------


class Player2ptAttempt(PlayerStat):

    statId = "2pta"
    
    def __init__(self, teamStat):
        super().__init__(teamStat)


    def computeGame(game):       
        result = 0
        gameMins = game[0]
        fga = game[ps_proc("fga")]
        tpa = game[ps_proc("tpa")]
        try:
            result = fga-tpa
        except ZeroDivisionError:
            pass
        return result


    def getStatId(self):
        return Player2ptAttempt.statId


#----------------------------------------------


class Player2ptMade(PlayerStat):

    statId = "2ptm"
    
    def __init__(self, teamStat):
        super().__init__(teamStat)


    def computeGame(game):       
        result = 0
        gameMins = game[0]
        fgm = game[ps_proc("fgm")]
        tpm = game[ps_proc("tpm")]
        try:
            result = fgm-tpm
        except ZeroDivisionError:
            pass
        return result


    def getStatId(self):
        return Player2ptMade.statId


    def setStatAdj(self, proj):

        for conditions in getGameConditions(itemId=self.player.getPlayerId(), haConstraint=self.player.team.getHomeAway()):
    
            for pos, starter in getPlayerConditions(player=self.player):
                posLabelComponent = "_pos" if pos else ""
                startLabelComponent = "_start"

                label = proj["proj_id"]+posLabelComponent+startLabelComponent+"-"+conditions["label"]

                twoAtt = self.player.playerStats["2pta"].getStatAdj(label)
                twoPct = self.player.playerStats["2pt_pct"].getStatAdj(label)

                try:
                    self.statAdj[label] = round(twoAtt *twoPct)
                except TypeError:
                    self.statAdj[label] = 0 


    def setStatEst(self, proj):
        pass           
  


#----------------------------------------------


class Player2ptPct(PlayerStat):

    statId = "2pt_pct"
    
    def __init__(self, teamStat):
        super().__init__(teamStat)


    def computeGame(game):       
        result = 0
        gameMins = game[0]
        fga = game[ps_proc("fga")]
        fgm = game[ps_proc("fgm")]
        tpa = game[ps_proc("tpa")]
        tpm = game[ps_proc("tpm")]

        twoatt = fga-tpa
        twomad = fgm-tpm

        try:
            result = twomad/twoatt
        except ZeroDivisionError:
            pass
        return result


    def getStatId(self):
        return Player2ptPct.statId


    def setStatAdj(self, proj):
        for conditions in getGameConditions(itemId=self.player.getPlayerId(), haConstraint=self.player.team.getHomeAway()):
    
            for pos, starter in getPlayerConditions(self.player):
                posProjComponent = "_{}".format(pos) if pos else ""
                startProjComponent = "_{}".format(starter) if starter else ""
                posLabelComponent = "_pos" if pos else ""
                startLabelComponent = "_start"

                label = proj["proj_id"]+posLabelComponent+startLabelComponent+"-"+conditions["label"]
                
                self.statAdj[label] = self.statEst[label]


    def setStatEst(self, proj):


        for conditions in getGameConditions(itemId=self.player.getPlayerId(), haConstraint=self.player.team.getHomeAway()):
    
            for pos, starter in getPlayerConditions(player=self.player):
                posProjComponent = "_{}".format(pos) if pos else ""
                startProjComponent = "_{}".format(starter) if starter else ""
                posLabelComponent = "_pos" if pos else ""
                startLabelComponent = "_start"

                label = proj["proj_id"]+posLabelComponent+startLabelComponent+"-"+conditions["label"]
                conditions["proj_id"] = proj["proj_id"]+posProjComponent+startProjComponent



                try:
                    self.statEst[label] = self.negotiate(conditions)
                except TypeError:
                    self.statEst[label] = 0         


#----------------------------------------------


class Player3ptAttempt(PlayerStat):

    statId = "3pta"
    
    def __init__(self, teamStat):
        super().__init__(teamStat)


    def computeGame(game):       
        result = 0
        gameMins = game[0]
        tpa = game[ps_proc("tpa")]
        try:
            result = tpa
        except ZeroDivisionError:
            pass
        return result


    def getStatId(self):
        return Player3ptAttempt.statId


#----------------------------------------------


class Player3ptMade(PlayerStat):

    statId = "3ptm"
    
    def __init__(self, teamStat):
        super().__init__(teamStat)


    def computeGame(game):       
        result = 0
        gameMins = game[0]
        tpm = game[ps_proc("tpm")]
        try:
            result = tpm
        except ZeroDivisionError:
            pass
        return result


    def getStatId(self):
        return Player3ptMade.statId


    def setStatAdj(self, proj):

        for conditions in getGameConditions(itemId=self.player.getPlayerId(), haConstraint=self.player.team.getHomeAway()):
    
            for pos, starter in getPlayerConditions(player=self.player):
                posLabelComponent = "_pos" if pos else ""
                startLabelComponent = "_start"

                label = proj["proj_id"]+posLabelComponent+startLabelComponent+"-"+conditions["label"]

                threeAtt = self.player.playerStats["3pta"].getStatAdj(label)
                threePct = self.player.playerStats["3pt_pct"].getStatAdj(label)

                try:
                    self.statAdj[label] = round(threeAtt *threePct)
                except TypeError:
                    self.statAdj[label] = 0 


    def setStatEst(self, proj):
        pass       
  


#----------------------------------------------


class Player3ptPct(PlayerStat):

    statId = "3pt_pct"
    
    def __init__(self, teamStat):
        super().__init__(teamStat)


    def computeGame(game):       
        result = 0
        gameMins = game[0]
        tpa = game[ps_proc("tpa")]
        tpm = game[ps_proc("tpm")]
        try:
            result = tpm/tpa
        except ZeroDivisionError:
            pass
        return result


    def getStatId(self):
        return Player3ptPct.statId


    def setStatAdj(self, proj):
        for conditions in getGameConditions(itemId=self.player.getPlayerId(), haConstraint=self.player.team.getHomeAway()):
    
            for pos, starter in getPlayerConditions(self.player):
                posProjComponent = "_{}".format(pos) if pos else ""
                startProjComponent = "_{}".format(starter) if starter else ""
                posLabelComponent = "_pos" if pos else ""
                startLabelComponent = "_start"

                label = proj["proj_id"]+posLabelComponent+startLabelComponent+"-"+conditions["label"]
                
                self.statAdj[label] = self.statEst[label]


    def setStatEst(self, proj):

        for conditions in getGameConditions(itemId=self.player.getPlayerId(), haConstraint=self.player.team.getHomeAway()):
    
            for pos, starter in getPlayerConditions(player=self.player):
                posProjComponent = "_{}".format(pos) if pos else ""
                startProjComponent = "_{}".format(starter) if starter else ""
                posLabelComponent = "_pos" if pos else ""
                startLabelComponent = "_start"

                label = proj["proj_id"]+posLabelComponent+startLabelComponent+"-"+conditions["label"]
                conditions["proj_id"] = proj["proj_id"]+posProjComponent+startProjComponent



                try:
                    self.statEst[label] = self.negotiate(conditions)
                except TypeError:
                    self.statEst[label] = 0  


#----------------------------------------------


class PlayerAssists(PlayerStat):

    statId = "ast"
    
    def __init__(self, teamStat):
        super().__init__(teamStat)


    def computeGame(game):       
        result = 0
        gameMins = game[0]
        ast = game[ps_proc("ast")]
        try:
            result = ast
        except ZeroDivisionError:
            pass
        return result


    def getStatId(self):
        return PlayerAssists.statId


#----------------------------------------------


class PlayerBlocks(PlayerStat):

    statId = "blk"
    
    def __init__(self, teamStat):
        super().__init__(teamStat)


    def computeGame(game):       
        result = 0
        gameMins = game[0]
        blk = game[ps_proc("blk")]
        try:
            result = blk
        except ZeroDivisionError:
            pass
        return result


    def getStatId(self):
        return PlayerBlocks.statId


    def setStatAdj(self, proj):
        for conditions in getGameConditions(itemId=self.player.getPlayerId(), haConstraint=self.player.team.getHomeAway()):
    
            for pos, starter in getPlayerConditions(self.player):
                posProjComponent = "_{}".format(pos) if pos else ""
                startProjComponent = "_{}".format(starter) if starter else ""
                posLabelComponent = "_pos" if pos else ""
                startLabelComponent = "_start"

                
                label = proj["proj_id"]+posLabelComponent+startLabelComponent+"-"+conditions["label"]

                if not self.teamStat.getTotal(label):
                    self.statAdj[label] = 0
                else:
                    self.statAdj[label] = round(self.teamStat.getForPlayerProj(label) * (self.statEst[label]/self.teamStat.getTotal(label)))



    def setStatEst(self, proj):


        for conditions in getGameConditions(itemId=self.player.getPlayerId(), haConstraint=self.player.team.getHomeAway()):
    
            for pos, starter in getPlayerConditions(player=self.player):
                posProjComponent = "_{}".format(pos) if pos else ""
                startProjComponent = "_{}".format(starter) if starter else ""
                posLabelComponent = "_pos" if pos else ""
                startLabelComponent = "_start"

                label = proj["proj_id"]+posLabelComponent+startLabelComponent+"-"+conditions["label"]
                conditions["proj_id"] = proj["proj_id"]+posProjComponent+startProjComponent

                minutes = self.player.playerStats["mins"].getStatAdj(label)


                try:
                    self.statEst[label] = self.negotiate(conditions)
                    self.teamStat.addToTotal(label, self.statEst[label])
                except TypeError:
                    self.statEst[label] = .01
                    self.teamStats.addToTotal(label, .01)


#----------------------------------------------


class PlayerDReb(PlayerStat):

    statId = "dreb"
    
    def __init__(self, teamStat):
        super().__init__(teamStat)


    def computeGame(game):       
        result = 0
        gameMins = game[0]
        dreb = game[ps_proc("dreb")]
        try:
            result = dreb
        except ZeroDivisionError:
            pass
        return result


    def getStatId(self):
        return PlayerDReb.statId


#----------------------------------------------


class PlayerFga(PlayerStat):

    statId = "fga"
    
    def __init__(self, teamStat):
        super().__init__(teamStat)


    def computeGame(game):       
        result = 0
        gameMins = game[0]
        fga = game[ps_proc("fga")]
        try:
            result = fga
        except ZeroDivisionError:
            pass
        return result


    def getStatId(self):
        return PlayerFga.statId


    def setStatAdj(self, proj):

        for conditions in getGameConditions(itemId=self.player.getPlayerId(), haConstraint=self.player.team.getHomeAway()):
    
            for pos, starter in getPlayerConditions(player=self.player):
                posLabelComponent = "_pos" if pos else ""
                startLabelComponent = "_start"

                label = proj["proj_id"]+posLabelComponent+startLabelComponent+"-"+conditions["label"]

                twoAtt = self.player.playerStats["2pta"].getStatAdj(label)
                threeAtt = self.player.playerStats["3pta"].getStatAdj(label)

                try:
                    self.statAdj[label] = round(twoAtt + threeAtt)
                except TypeError:
                    self.statAdj[label] = 0    
  


    def setStatEst(self, proj):
        pass       
  


#----------------------------------------------


class PlayerFgm(PlayerStat):

    statId = "fgm"
    
    def __init__(self, teamStat):
        super().__init__(teamStat)


    def computeGame(game):       
        result = 0
        gameMins = game[0]
        fgm = game[ps_proc("fgm")]
        try:
            result = fgm
        except ZeroDivisionError:
            pass
        return result


    def getStatId(self):
        return PlayerFgm.statId


    def setStatAdj(self, proj):

        for conditions in getGameConditions(itemId=self.player.getPlayerId(), haConstraint=self.player.team.getHomeAway()):
    
            for pos, starter in getPlayerConditions(player=self.player):
                posLabelComponent = "_pos" if pos else ""
                startLabelComponent = "_start"

                label = proj["proj_id"]+posLabelComponent+startLabelComponent+"-"+conditions["label"]

                twoMade = self.player.playerStats["2ptm"].getStatAdj(label)
                threeMade = self.player.playerStats["3ptm"].getStatAdj(label)

                try:
                    self.statAdj[label] = round(twoMade + threeMade)
                except TypeError:
                    self.statAdj[label] = 0    
  


    def setStatEst(self, proj):
        pass       


#----------------------------------------------


class PlayerFta(PlayerStat):

    statId = "fta"
    
    def __init__(self, teamStat):
        super().__init__(teamStat)


    def computeGame(game):       
        result = 0
        gameMins = game[0]
        fta = game[ps_proc("fta")]
        try:
            result = fta
        except ZeroDivisionError:
            pass
        return result


    def getStatId(self):
        return PlayerFta.statId


#----------------------------------------------


class PlayerFtm(PlayerStat):

    statId = "ftm"
    
    def __init__(self, teamStat):
        super().__init__(teamStat)


    def computeGame(game):       
        result = 0
        gameMins = game[0]
        ftm = game[ps_proc("ftm")]
        try:
            result = ftm
        except ZeroDivisionError:
            pass
        return result


    def getStatId(self):
        return PlayerFtm.statId


    def setStatAdj(self, proj):

        for conditions in getGameConditions(itemId=self.player.getPlayerId(), haConstraint=self.player.team.getHomeAway()):
    
            for pos, starter in getPlayerConditions(player=self.player):
                posLabelComponent = "_pos" if pos else ""
                startLabelComponent = "_start"

                label = proj["proj_id"]+posLabelComponent+startLabelComponent+"-"+conditions["label"]

                ftAtt = self.player.playerStats["fta"].getStatAdj(label)
                ftPct = self.player.playerStats["ft_pct"].getStatAdj(label)

                try:
                    self.statAdj[label] = round(ftAtt *ftPct)
                except TypeError:
                    self.statAdj[label] = 0 


    def setStatEst(self, proj):
        pass  


#----------------------------------------------


class PlayerFtPct(PlayerStat):

    statId = "ft_pct"
    
    def __init__(self, teamStat):
        super().__init__(teamStat)


    def computeGame(game):       
        result = 0
        gameMins = game[0]
        fta = game[ps_proc("fta")]
        ftm = game[ps_proc("ftm")]
        try:
            result = ftm/fta
        except ZeroDivisionError:
            pass
        return result


    def negotiate(self, formatting):
        # Initiate variables
        totals = []
        index = 3
        result = 0

##        print(formatting["label"])
        formatting["item_type"] = "player"
        formatting["off_def"] = "offense"
        formatting["stat_id"] = self.getStatId()
        
        playerResult = self.db.curs.execute(negotiateCmd.format(formatting)).fetchone()
##        print(negotiateCmd.format(formatting))
##        print("\n\nplayerResult")
##        print(playerResult)
        

        matchFormat = formatting.copy()
        matchFormat["proj_id"] = "matchup_{}".format(formatting["proj_id"])
        matchResult = self.db.curs.execute(negotiateCmd.format(matchFormat)).fetchone()
##        print(negotiateCmd.format(matchFormat))
##        print("\nmatchResult")
##        print(matchResult)


        b2bFormat = formatting.copy()
        b2bFormat["proj_id"] = "b2b_{}".format(formatting["proj_id"])
        b2bResult = self.db.curs.execute(negotiateCmd.format(b2bFormat)).fetchone()
##        print(negotiateCmd.format(b2bFormat))
##        print("\nb2bResult")
##        print(b2bResult)


        if playerResult:
            totals.append(playerResult[index])

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


    def getStatId(self):
        return PlayerFtPct.statId


    def setStatAdj(self, proj):
        for conditions in getGameConditions(itemId=self.player.getPlayerId(), haConstraint=self.player.team.getHomeAway()):
    
            for pos, starter in getPlayerConditions(self.player):
                posProjComponent = "_{}".format(pos) if pos else ""
                startProjComponent = "_{}".format(starter) if starter else ""
                posLabelComponent = "_pos" if pos else ""
                startLabelComponent = "_start"

                label = proj["proj_id"]+posLabelComponent+startLabelComponent+"-"+conditions["label"]
                
                self.statAdj[label] = self.statEst[label]


    def setStatEst(self, proj):


        for conditions in getGameConditions(itemId=self.player.getPlayerId(), haConstraint=self.player.team.getHomeAway()):
    
            for pos, starter in getPlayerConditions(player=self.player):
                posProjComponent = "_{}".format(pos) if pos else ""
                startProjComponent = "_{}".format(starter) if starter else ""
                posLabelComponent = "_pos" if pos else ""
                startLabelComponent = "_start"

                label = proj["proj_id"]+posLabelComponent+startLabelComponent+"-"+conditions["label"]
                conditions["proj_id"] = proj["proj_id"]+posProjComponent+startProjComponent



                try:
                    self.statEst[label] = self.negotiate(conditions)
                except TypeError:
                    self.statEst[label] = 0  


#----------------------------------------------


class PlayerFouls(PlayerStat):

    statId = "fouls"
    
    def __init__(self, teamStat):
        super().__init__(teamStat)


    def computeGame(game):       
        result = 0
        gameMins = game[0]
        fouls = game[ps_proc("fouls")]
        try:
            result = fouls
        except ZeroDivisionError:
            pass
        return result


    def getStatId(self):
        return PlayerFouls.statId


#----------------------------------------------


class PlayerMinutes(PlayerStat):

    statId = "mins"
    
    def __init__(self, teamStat):
        super().__init__(teamStat)


    def computeGame(game):       
        result = 0
        gameMins = game[0]
        mins = game[ps_proc("mins")]
        try:
            result = mins
        except ZeroDivisionError:
            pass
        return result


    def getStatId(self):
        return PlayerMinutes.statId


    def setStatAdj(self, label, newMins):
        self.statAdj[label] = newMins


    def setStatEst(self, proj):
        for conditions in getGameConditions(itemId=self.player.getPlayerId(), haConstraint=self.player.team.getHomeAway()):
    
            for pos, starter in getPlayerConditions(player=self.player):
                posProjComponent = "_{}".format(pos) if pos else ""
                startProjComponent = "_{}".format(starter) if starter else ""
                posLabelComponent = "_pos" if pos else ""
                startLabelComponent = "_start"

                label = proj["proj_id"]+posLabelComponent+startLabelComponent+"-"+conditions["label"]
                conditions["proj_id"] = proj["proj_id"]+posProjComponent+startProjComponent

                self.statEst[label] = round(self.negotiate(conditions))
                


#----------------------------------------------


class PlayerOReb(PlayerStat):

    statId = "oreb"
    
    def __init__(self, teamStat):
        super().__init__(teamStat)


    def computeGame(game):       
        result = 0
        gameMins = game[0]
        oreb = game[ps_proc("oreb")]
        try:
            result = oreb
        except ZeroDivisionError:
            pass
        return result


    def getStatId(self):
        return PlayerOReb.statId


#----------------------------------------------


class PlayerPoints(PlayerStat):

    statId = "points"
    
    def __init__(self, teamStat):
        super().__init__(teamStat)


    def computeGame(game):       
        result = 0
        gameMins = game[0]
        points = game[ps_proc("points")]
        try:
            result = (points/gameMins)*48
        except ZeroDivisionError:
            pass
        return result


    def getStatId(self):
        return PlayerPoints.statId


    def setStatAdj(self, proj):

        for conditions in getGameConditions(itemId=self.player.getPlayerId(), haConstraint=self.player.team.getHomeAway()):
    
            for pos, starter in getPlayerConditions(player=self.player):
                posLabelComponent = "_pos" if pos else ""
                startLabelComponent = "_start"

                label = proj["proj_id"]+posLabelComponent+startLabelComponent+"-"+conditions["label"]

                twoMade = self.player.playerStats["2ptm"].getStatAdj(label)
                threeMade = self.player.playerStats["3ptm"].getStatAdj(label)
                ftMade  = self.player.playerStats["ftm"].getStatAdj(label)

                try:
                    self.statAdj[label] = round((twoMade*2) + (threeMade*3) + ftMade)
                except TypeError:
                    self.statAdj[label] = 0    
  


    def setStatEst(self, proj):
        pass    
    
    
#----------------------------------------------


class PlayerSteals(PlayerStat):

    statId = "stl"
    
    def __init__(self, teamStat):
        super().__init__(teamStat)


    def computeGame(game):       
        result = 0
        gameMins = game[0]
        stl = game[ps_proc("stl")]
        try:
            result = stl
        except ZeroDivisionError:
            pass
        return result


    def getStatId(self):
        return PlayerSteals.statId


    def setStatEst(self, proj):


        for conditions in getGameConditions(itemId=self.player.getPlayerId(), haConstraint=self.player.team.getHomeAway()):
    
            for pos, starter in getPlayerConditions(player=self.player):
                posProjComponent = "_{}".format(pos) if pos else ""
                startProjComponent = "_{}".format(starter) if starter else ""
                posLabelComponent = "_pos" if pos else ""
                startLabelComponent = "_start"

                label = proj["proj_id"]+posLabelComponent+startLabelComponent+"-"+conditions["label"]
                conditions["proj_id"] = proj["proj_id"]+posProjComponent+startProjComponent

                minutes = self.player.playerStats["mins"].getStatAdj(label)


                try:
                    self.statEst[label] = self.negotiate(conditions)
                    self.teamStat.addToTotal(label, self.statEst[label])
                except TypeError:
                    self.statEst[label] = 0



#----------------------------------------------


class PlayerTurnovers(PlayerStat):

    statId = "turn"
    
    def __init__(self, teamStat):
        super().__init__(teamStat)


    def computeGame(game):       
        result = 0
        gameMins = game[0]
        turn = game[ps_proc("turn")]
        try:
            result = turn
        except ZeroDivisionError:
            pass
        return result


    def getStatId(self):
        return PlayerTurnovers.statId
    



   
#################################################################################


teamStatList = (FtaPerFoul, Possessions, Team2ptAttempt, Team2ptMade, Team2ptPct,
                Team3ptAttempt, Team3ptMade, Team3ptPct, Team3ptPerFga, TeamAssists, TeamAssistsPerFgm,
                TeamBlocks, TeamBlocksPerFga, TeamDReb, TeamDRebPerMiss, TeamFga, TeamFgm, TeamFouls,
                TeamFta, TeamFtPct, TeamFtm, TeamMinutes, TeamOReb, TeamORebPerMiss, TeamPoints,
                TeamSteals, TeamStealsPerTurn, TeamTurnovers, )

playerStatList = (Player2ptAttempt, Player2ptMade, Player2ptPct, Player3ptAttempt,
                  Player3ptMade, Player3ptPct, PlayerAssists, PlayerBlocks, PlayerDReb,
                  PlayerFga, PlayerFgm, PlayerFouls, PlayerFta, PlayerFtPct, PlayerFtm, PlayerMinutes,
                  PlayerOReb, PlayerPoints, PlayerSteals, PlayerTurnovers, )


#################################################################################



