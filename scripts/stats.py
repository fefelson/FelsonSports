from SportsDB.DB.NBA import gameDateCmd
from SportsDB.Models.SportsManager import SportsManager

from datetime import date, timedelta
import numpy
from pprint import pprint
from sqlite3 import IntegrityError

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


def getHACmd(homeAway):
    return {"home": homeCmd, "away": awayCmd, "all": allCmd }[homeAway]


allCmd = " stats.game_id = gd.game_id"
awayCmd = allCmd + " AND stats.team_id = gd.away_id"
homeCmd = allCmd + " AND stats.team_id = gd.home_id"


#################################################################################

baseTeamBucketCmd = "SELECT stat_15, stat_85, stat_60, stat_40 FROM team_totals WHERE stat_id = '{0[stat_id]}' AND proj_id = 'team' AND time_frame = '{0[time_frame]}' AND home_away = '{0[home_away]}' AND off_def = '{0[off_def]}' and item_id = 'all'"
oppJoin = "INNER JOIN team_stats AS opp ON stats.game_id = opp.game_id AND stats.opp_id = opp.team_id"
selectStatsCmd = "SELECT gd.mins, {0[selectCmd]} FROM {0[item_type]}_stats AS stats {0[oppCmd]} INNER JOIN ({0[gdCmd]}) AS gd ON {0[haCmd]} {0[whereCmd]}" 
statTeamAvgCmd = "SELECT stat_avg FROM team_totals WHERE stat_id = '{0[stat_id]}' AND proj_id = '{0[proj_id]}' AND time_frame = '{0[time_frame]}' AND home_away = '{0[home_away]}' AND off_def = '{0[off_def]}'" 
statPlayerAvgCmd = "SELECT stat_avg FROM player_totals WHERE stat_id = '{0[stat_id]}' AND proj_id = '{0[proj_id]}' AND time_frame = '{0[time_frame]}' AND home_away = '{0[home_away]}'" 
teamAvgCmd = "SELECT stat_avg FROM team_totals WHERE proj_id = '{0[proj_id]}' AND stat_id = '{0[stat_id]}' AND time_frame = '{0[time_frame]}' AND home_away = '{0[home_away]}' AND off_def = '{0[off_def]}' AND item_id = {0[item_id]}"
        

#################################################################################


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

tableList = (teamTotalsTable, teamBucketTable)

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
    index = round(pct*num)
    index = num-1 if index >= num else index
    return sorted(numList)[index]


#################################################################################


class Projection:

    def __init__(self, title):
        self.title = title      


    def getConstraints(self, homeConstraint=None):
        raise AssertionError


    def getProjId(self):
        return self.title


class PlayerProjection(Projection):

    def __init__(self, title):
        super().__init__(title)



class TeamProjection(Projection):

    def __init__(self, title):
        super().__init__(title)


    def getConstraints(self, homeConstraint=None):
        homeAwayList = allHomeAway if not homeConstraint else ("all", homeConstraint)
        for timeFrame in timeFrameList:
            for homeAway in homeAwayList:
                for offDef in ("offense", "defense"):
                    yield (timeFrame, homeAway, offDef)


teamProj = TeamProjection("team")
lineupProj = TeamProjection("lineup")


#################################################################################
    


class Stat:

    TeamProjections = (teamProj, lineupProj)
    PlayerProjections = ()

    def __init__(self, statId, db):

        self.statId = statId
        self.db = db

        if not self.isBaselineSet():
            print("Setting Baselines {}\n".format(self.statId))
            self.setTendencies()
            self.makeBuckets()
            self.setBuckets()
            self.setBaseline()


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
            for item, value in (("stat_avg", round(numpy.mean(itemList),4)),
                                ("stat_min", round(min(itemList), 4)),
                                ("stat_15", round(quantile(itemList, .25), 4)),
                                ("stat_40", round(quantile(itemList, .4), 4)),
                                ("stat_60", round(quantile(itemList, .6), 4)),
                                ("stat_85", round(quantile(itemList, .85), 4)),
                                ("stat_max", round(max(itemList), 4))):
                formatting[item] = value
       
        return formatting


    def computeGame(self):
        pass
   


    def getGameConditions(self, proj, itemId="all"):
        conditionsLists = []
        for constraints in proj.getConstraints():
            timeFrame, homeAway, offDef = constraints
            conditions = {}
            for key, value in (("item_type", self.getItemType()),
                               ("item_id", itemId),
                               ("stat_id", self.statId),
                               ("proj_id", proj.getProjId()),
                               ("time_frame", timeFrame),
                               ("home_away", homeAway),
                               ("off_def", offDef),
                               ("gdCmd", getGDCmd(timeFrame)),
                               ("haCmd", getHACmd(homeAway)),
                               ("selectCmd", self.getSelectCmd(offDef)),
                               ("oppCmd", oppJoin),
                               ):
                conditions[key] = value
            conditionsLists.append(conditions.copy())
        return conditionsLists


    def getItemType(self):
        return AssertionError
    

    def getNewBucket(self, formatting):
        #pprint(formatting)
        bucket = "n/a"

        if self.getItemType() == "team":
            baseBucketCmd = baseTeamBucketCmd
            itemAvgCmd = teamAvgCmd
            
        try:
            baseLow, baseHigh, base60, base40 = db.curs.execute(baseBucketCmd.format(formatting)).fetchone()
        except TypeError:
            print(baseBucketCmd.format(formatting))
            print()
            pprint(formatting)
            raise AssertionError
        try:
            statAvg = formatting["stat_avg"]
        except KeyError:
            statAvg = db.curs.execute(itemAvgCmd.format(formatting)).fetchone()[0]
        #print(baseLow, baseHigh, base60, base40)
        try:
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


    def makeBuckets(self):
        
        if self.getItemType() == "team":
            statAvgCmd = statTeamAvgCmd
            table = teamTotalsTable

        for conditions in self.getGameConditions(teamProj):
            conditions["whereCmd"] = ""
            totals = [x[0] for x in db.curs.execute(statAvgCmd.format(conditions)).fetchall()]
            formatting = self.calcItemList(totals, conditions)
            try:
                db.insert(table, formatting)
            except IntegrityError:
                pass
        db.conn.commit()       


class TeamStat(Stat):

    def __init__(self, statId, db):
        super().__init__(statId, db)


    def insertResults(self, table, conditions):
        #pprint(selectStatsCmd.format(conditions))
        totals = [self.computeGame(x) for x in db.curs.execute(selectStatsCmd.format(conditions)).fetchall()]
        #pprint(totals)
        ##  calculate num, min, 15qtr, 40qtr, avg, 60qtr, 85qtr, max of totals
        formatting = self.calcItemList(totals, conditions)
        if formatting["num"]:
            try:
                db.insert(table, formatting)
            except IntegrityError:
                pass


    def setTendencies(self):
        ##  For each team_id in database
        for teamId in [x[0] for x in db.curs.execute("SELECT team_id FROM pro_teams").fetchall()]:
            for conditions in self.getGameConditions(teamProj, itemId=teamId):
                conditions["whereCmd"] = "WHERE stats.team_id = {}".format(teamId)
                ##  Compile game stats offense/defense for every game teamId
                ##   played under these conditions
                self.insertResults(teamTotalsTable, conditions)
                


    def getItemType(self):
        return "team"


    def getSelectCmd(self, offDef):
        # {0} is filled with stats when on offense, opp when on defense
        formatting = ("stats", "opp") if offDef == "offense" else ("opp", "stats")
        cmd = ", ".join(self.getDesiredStats())
        return cmd.format(*formatting)


    def setBuckets(self):
        ##  For each team_id in database
        for teamId in [x[0] for x in db.curs.execute("SELECT team_id FROM pro_teams").fetchall()]:
            for conditions in self.getGameConditions(teamProj, itemId=teamId):                            
                formatting = self.getNewBucket(conditions)
                try:
                    db.insert(teamBucketTable, formatting)
                except IntegrityError:
                    pass
                    
                    
 


class Possessions(TeamStat):

    baselineSet = False

    def __init__(self, db):
        super().__init__("poss", db)


    def getDesiredStats(self):
        return ("{0}.fga", "{0}.turn", "{1}.fouls")


    def computeGame(self, result):
        gameMins = result[0]
        poss = sum(result[1:])
        return (poss/gameMins)*48


    def isBaselineSet(self):
        return Possessions.baselineSet


    def setBaseline(self):
        Possessions.baselineSet = True


#################################################################################



if __name__ == "__main__":

    sm = SportsManager()
    nba = sm.getLeague("nba")
    nba.databaseManager.openDB("season")
    db = nba.databaseManager.db["season"]

    createTempTables(db)


    pos = Possessions(db)
    
