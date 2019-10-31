from SportsDB.DB.NBA import gameDateCmd
from SportsDB.Models.SportsManager import SportsManager

from datetime import date, timedelta
import numpy
from pprint import pprint
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
    giCmd += " IN "+str(gameTuple) if len(gameTuple) > 1 else " = "+str(gameTuple[0])
    return giCmd


def getHACmd(homeAway):
    return {"home": homeCmd, "away": awayCmd, "all": allCmd }[homeAway]


def getOppCmd(teamTuple):
    teamCmd = "stats.opp_id"
    teamCmd += " IN "+str(teamTuple) if len(teamTuple) > 1 else " = "+str(teamTuple[0])
    return teamCmd


def getTeamCmd(teamTuple):
    teamCmd = "stats.team_id"
    teamCmd += " IN "+str(teamTuple) if len(teamTuple) > 1 else " = "+str(teamTuple[0])
    return teamCmd
    
 
allCmd = " stats.game_id = gd.game_id"
awayCmd = allCmd + " AND stats.team_id = gd.away_id"
homeCmd = allCmd + " AND stats.team_id = gd.home_id"


#################################################################################

baseTeamBucketCmd = "SELECT stat_15, stat_85, stat_60, stat_40 FROM team_totals WHERE stat_id = '{0[stat_id]}' AND proj_id = 'team' AND time_frame = '{0[time_frame]}' AND home_away = '{0[home_away]}' AND off_def = '{0[off_def]}' and item_id = 'all'"
bucketCmd = "SELECT bucket FROM {0[item_type]}_buckets WHERE stat_id = '{0[stat_id]}' AND proj_id = '{0[proj_id]}' AND time_frame = '{0[time_frame]}' AND home_away = '{0[home_away]}' AND off_def = '{0[off_def]}' AND item_id = {0[item_id]}"
gameListWhereCmd = "WHERE {0[itCmd]} AND {0[giCmd]}"
oppJoin = "INNER JOIN team_stats AS opp ON stats.game_id = opp.game_id AND stats.opp_id = opp.team_id"
selectStatsCmd = "SELECT gd.mins, {0[selectCmd]} FROM {0[item_type]}_stats AS stats {0[oppJoin]} INNER JOIN ({0[gdCmd]}) AS gd ON {0[haCmd]} {0[whereCmd]}" 
similarCmd = "SELECT DISTINCT item_id FROM {0[item_type]}_buckets WHERE stat_id = '{0[stat_id]}' AND proj_id = '{0[check_id]}' AND time_frame = '{0[time_frame]}' AND home_away = '{0[home_away]}' AND off_def = '{0[off_def]}' AND bucket = '{0[bucket]}'"
similarWhereCmd = "WHERE {0[teamCmd]} AND {0[oppCmd]}"
statTeamAvgCmd = "SELECT stat_avg FROM team_totals WHERE stat_id = '{0[stat_id]}' AND proj_id = '{0[proj_id]}' AND time_frame = '{0[time_frame]}' AND home_away = '{0[home_away]}' AND off_def = '{0[off_def]}'" 
statPlayerAvgCmd = "SELECT stat_avg FROM player_totals WHERE stat_id = '{0[stat_id]}' AND proj_id = '{0[proj_id]}' AND time_frame = '{0[time_frame]}' AND home_away = '{0[home_away]}'" 
teamAvgCmd = "SELECT stat_avg FROM team_totals WHERE proj_id = '{0[proj_id]}' AND stat_id = '{0[stat_id]}' AND time_frame = '{0[time_frame]}' AND home_away = '{0[home_away]}' AND off_def = '{0[off_def]}' AND item_id = {0[item_id]}"
teamNegotiateCmd = "SELECT num, stat_85, stat_60, stat_avg, stat_40, stat_15, stat_max, stat_min FROM team_totals WHERE stat_id = '{0[stat_id]}' AND proj_id = '{0[proj_id]}' AND time_frame = '{0[time_frame]}' AND home_away = '{0[home_away]}' AND off_def = '{0[off_def]}' AND item_id = {0[item_id]}"
        

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
    index = int(pct*num)
    return sorted(numList)[index] 


#################################################################################


class Projection:

    def __init__(self, title):
        self.title = title


    def getCheckId(self):
        raise AssertionError


    def getConstraints(self, homeConstraint):
        raise AssertionError


    def getProjId(self):
        return self.title


class PlayerProjection(Projection):

    def __init__(self, title):
        super().__init__(title)



class TeamProjection(Projection):

    def __init__(self, title):
        super().__init__(title)


    def getConstraints(self, homeConstraint):
        homeAwayList = allHomeAway if not homeConstraint else ("all", homeConstraint)
        for timeFrame in timeFrameList:
            for homeAway in homeAwayList:
                for offDef in ("offense", "defense"):
                    yield (timeFrame, homeAway, offDef)


    def getCheckId(self):
        return "team"


teamProj = TeamProjection("team")
lineupProj = TeamProjection("lineup")
teamMatchProj = TeamProjection("matchup")
teamB2bProj = TeamProjection("b2b")
teamSimProj = TeamProjection("similar")


#################################################################################
    


class Stat:

    TeamProjections = (teamProj,)# lineupProj)
    PlayerProjections = ()

    def __init__(self, statId, db):

        self.statId = statId
        self.db = db

        self.statProj = {}

        if not self.isBaselineSet():
            print("Setting Baselines {}\n".format(self.statId))
            self.setBaselineTendencies()
            self.makeBuckets()
            self.setBuckets()
            self.setBaseline()

        if self.getMatchupGames():
            self.setMatchupStats()

        if self.getB2bGames():
            self.setB2bStats()

        self.setSimilarStats()


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


    def getB2bGames(self):
        raise AssertionError


    def getB2bProj(self):
        raise AssertionError

    
    def getGameConditions(self, proj, itemId="all", haConstraint=None):
        conditionsLists = []
        for constraints in proj.getConstraints(haConstraint):
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
                               ("oppJoin", oppJoin),
                               ("label","{}-{}-{}".format(proj.getProjId(),timeFrame,homeAway))
                               ):
                conditions[key] = value
            conditionsLists.append(conditions.copy())
        return conditionsLists


    def getItCmd(self):
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


    def getMatchupGames(self):
        raise AssertionError


    def getMatchProj(self):
        raise AssertionError

    
    def getNewBucket(self, formatting):
        #pprint(formatting)
        bucket = "n/a"

        if self.getItemType() == "team":
            baseBucketCmd = baseTeamBucketCmd
            itemAvgCmd = teamAvgCmd
            
        try:
            baseLow, baseHigh, base60, base40 = self.db.curs.execute(baseBucketCmd.format(formatting)).fetchone()
        except TypeError:
            print(baseBucketCmd.format(formatting))
            print()
            pprint(formatting)
            raise AssertionError
        try:
            statAvg = formatting["stat_avg"]
        except KeyError:
            statAvg = self.db.curs.execute(itemAvgCmd.format(formatting)).fetchone()[0]
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
                               ("oppJoin", oppJoin),
                               ("label","{}-{}-{}".format(proj.getProjId(),timeFrame,homeAway))
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
    

    def makeBuckets(self):
        
        if self.getItemType() == "team":
            statAvgCmd = statTeamAvgCmd
            table = teamTotalsTable

        for conditions in self.getGameConditions(teamProj):
            conditions["whereCmd"] = ""
            totals = [x[0] for x in self.db.curs.execute(statAvgCmd.format(conditions)).fetchall()]
            formatting = self.calcItemList(totals, conditions)
            try:
                self.db.insert(table, formatting)
            except IntegrityError:
                pass
        self.db.conn.commit()


    def negotiate(self, formatting):
        raise AssertionError


    def setMatchupStats(self):
        for conditions in self.getGameConditions(self.getMatchProj(), itemId=self.getItemId()):
            if conditions["off_def"] == "offense":                
                itCmd = "stats.{0[item_type]}_id = {0[item_id]}".format({"item_type": self.getItemType(), "item_id": self.getItemId()})
                giCmd = getGICmd(self.getMatchupGames())
                conditions["whereCmd"] = gameListWhereCmd.format({"itCmd": itCmd, "giCmd": giCmd})       
                self.insertResults(self.getTotalsTable(), conditions)


    def setB2bStats(self):
        raise AssertionError


    def setSimilarStats(self):
        raise AssertionError
   

    def setStats(self):
        raise AssertionError


###############################################


class TeamStat(Stat):

    def __init__(self, team, statId, db):
        self.team = team
        super().__init__(statId, db)

        
    def getB2bGames(self):
        return self.team.getB2bGames()


    def getB2bProj(self):
        return teamB2bProj
    

    def getItemId(self):
        return self.team.getTeamId()

    
    def getItemType(self):
        return "team"


    def getMatchupGames(self):
        return self.team.getMatchupGames()


    def getMatchProj(self):
        return teamMatchProj


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
##        
        
        
        oppResult =  self.db.curs.execute(teamNegotiateCmd.format(dFormatting)).fetchone()
##        print(teamNegotiateCmd.format(dFormatting))
##        print("\noppResult")
##        print(oppResult)


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


        b2bDFormat = dFormatting.copy()
        b2bDFormat["proj_id"] = "b2b"
        b2bDResult = self.db.curs.execute(teamNegotiateCmd.format(b2bDFormat)).fetchone()
##        print(teamNegotiateCmd.format(b2bDFormat))
##        print("\nb2bDResult")
##        print(b2bDResult)


        simOffFormat = formatting.copy()
        simOffFormat["proj_id"] = simOffFormat["proj_id"]+"_vs_similar"
        simOffResult = self.db.curs.execute(teamNegotiateCmd.format(simOffFormat)).fetchone()
##        print(teamNegotiateCmd.format(simOffFormat))
##        print("\nsimOffResult")
##        print(simOffResult)


        simDefFormat = dFormatting.copy()
        simDefFormat["proj_id"] = simDefFormat["proj_id"]+"_vs_similar"
        simDefResult = self.db.curs.execute(teamNegotiateCmd.format(simDefFormat)).fetchone()
##        print(teamNegotiateCmd.format(simDefFormat))
##        print("\nsimDefResult")
##        print(simDefResult)



        simFormat = formatting.copy()
        simFormat["proj_id"] = simFormat["proj_id"]+"_similar"
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


    def setB2bStats(self):
        for conditions in self.getGameConditions(self.getB2bProj(), itemId=self.getItemId()):                            
            itCmd = "stats.{0[item_type]}_id = {0[item_id]}".format({"item_type": self.getItemType(), "item_id": self.getItemId()})
            giCmd = getGICmd(self.getB2bGames())
            conditions["whereCmd"] = gameListWhereCmd.format({"itCmd": itCmd, "giCmd": giCmd})       
            try:
                self.insertResults(self.getTotalsTable(), conditions)
            except OperationalError:
                pprint(conditions)
                print()
                pprint(selectStatsCmd.format(conditions))
                raise AssertionError


    def setBaselineTendencies(self):
        ##  For each team_id in database
        for teamId in [x[0] for x in self.db.curs.execute("SELECT team_id FROM pro_teams").fetchall()]:
            for conditions in self.getGameConditions(teamProj, itemId=teamId):
                conditions["whereCmd"] = "WHERE stats.team_id = {}".format(teamId)
                ##  Compile game stats offense/defense for every game teamId
                ##   played under these conditions
                self.insertResults(teamTotalsTable, conditions)
                

    def setBuckets(self):
        ##  For each team_id in database
        for teamId in [x[0] for x in self.db.curs.execute("SELECT team_id FROM pro_teams").fetchall()]:
            for conditions in self.getGameConditions(teamProj, itemId=teamId):                            
                formatting = self.getNewBucket(conditions)
                try:
                    self.db.insert(teamBucketTable, formatting)
                except IntegrityError:
                    pass


    def setSimilarStats(self):
        for proj in super().TeamProjections:
            for conditions in self.getSimGameConditions(proj, haConstraint=self.team.getHomeAway()):
                offConditions = conditions.copy()
                offConditions["off_def"] = "offense"
                offConditions["item_id"] = self.getItemId()

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

                    offTeams = tuple([x[0] for x in self.db.curs.execute(similarCmd.format(offConditions)).fetchall() if x[0] != str(self.getItemId())]) 
                    defTeams = tuple([x[0] for x in self.db.curs.execute(similarCmd.format(defConditions)).fetchall() if x[0] != str(self.team.getOppId())]) 


                    teamCmd = getTeamCmd(offTeams)
                    oppCmd = getOppCmd(defTeams)
                    conditions["proj_id"] = conditions["proj_id"]+"_similar"
                    conditions["off_def"] = "offense"
                    conditions["item_id"] = self.getItemId()
                    conditions["whereCmd"] = similarWhereCmd.format({"teamCmd":teamCmd, "oppCmd":oppCmd})
                    # enter into team_totals
                    self.insertResults(self.getTotalsTable(), conditions)
                    
                    # make similar bucket 
                    formatting = self.getNewBucket(conditions)
                    try:
                        # enter bucket into team_bucket
                        self.db.insert(teamBucketTable, formatting)
                    except IntegrityError:
                        pass

                    # similar defenses vs Offense team
                    teamCmd = getTeamCmd((self.getItemId(),))
                    oppCmd = getOppCmd(defTeams)
                    offConditions["proj_id"] = offConditions["proj_id"]+"_vs_similar"
                    offConditions["whereCmd"] = similarWhereCmd.format({"teamCmd":teamCmd, "oppCmd":oppCmd})
                    # enter into team_totals
                    self.insertResults(self.getTotalsTable(), offConditions)

                    # similar offenses vs Defense team
                    teamCmd = getTeamCmd(offTeams)
                    oppCmd = getOppCmd((self.team.getOppId(),))
                    defConditions["proj_id"] = defConditions["proj_id"]+"_vs_similar"
                    defConditions["whereCmd"] = similarWhereCmd.format({"teamCmd":teamCmd, "oppCmd":oppCmd})
                    # enter into team_totals
                    self.insertResults(self.getTotalsTable(), defConditions)

                except TypeError:
                    pass
                except IndexError:
                    pass



                


    def setStats(self):
        for proj in super().TeamProjections:
            for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
                if conditions["off_def"] == "offense":
                    label = conditions["label"]
                    #pprint(conditions)
                    self.statProj[label] = round(self.negotiate(conditions))
            
        
#----------------------------------------------


class FtaPerFoul(TeamStat):

    baselineSet = False

    def __init__(self, team, db):
        super().__init__(team, "fta_per_foul", db)


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


    def isBaselineSet(self):
        return FtaPerFoul.baselineSet


    def setBaseline(self):
        FtaPerFoul.baselineSet = True


    def setStats(self):
        for proj in super().TeamProjections:
            for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
                if conditions["off_def"] == "offense":
                    label = conditions["label"]
                    #pprint(conditions)
                    self.statProj[label] = self.negotiate(conditions)


#----------------------------------------------


class Possessions(TeamStat):

    baselineSet = False

    def __init__(self, team, db):
        super().__init__(team, "poss", db)


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


    def isBaselineSet(self):
        return Possessions.baselineSet


    def setBaseline(self):
        Possessions.baselineSet = True


#----------------------------------------------


class Team2ptAttempt(TeamStat):

    baselineSet = False

    def __init__(self, team, db):
        super().__init__(team, "2pta", db)


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


    def isBaselineSet(self):
        return Team2ptAttempt.baselineSet


    def setBaseline(self):
        Team2ptAttempt.baselineSet = True


    def setStats(self):
        for proj in super().TeamProjections:
            for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
                if conditions["off_def"] == "offense":
                    label = conditions["label"]
                    #pprint(conditions)

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

    baselineSet = False

    def __init__(self, team, db):
        super().__init__(team, "2ptm", db)


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


    def isBaselineSet(self):
        return Team2ptMade.baselineSet


    def setBaseline(self):
        Team2ptMade.baselineSet = True


    def setStats(self):
        for proj in super().TeamProjections:
            for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
                if conditions["off_def"] == "offense":
                    label = conditions["label"]
                    #pprint(conditions)

                    twoAtt = self.team.teamStats["2pta"].getStatProj(label)
                    twoPct = self.team.teamStats["2pt_pct"].getStatProj(label)
                    
                    self.statProj[label] = round(twoAtt * twoPct)

        
#----------------------------------------------


class Team2ptPct(TeamStat):

    baselineSet = False

    def __init__(self, team, db):
        super().__init__(team, "2pt_pct", db)


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


    def isBaselineSet(self):
        return Team2ptPct.baselineSet


    def setBaseline(self):
        Team2ptPct.baselineSet = True


    def setStats(self):
        for proj in super().TeamProjections:
            for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
                if conditions["off_def"] == "offense":
                    label = conditions["label"]
                    #pprint(conditions)
                    self.statProj[label] = self.negotiate(conditions)

        
#----------------------------------------------


class Team2ptPerFga(TeamStat):

    baselineSet = False

    def __init__(self, team, db):
        super().__init__(team, "2pt_per_fga", db)


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


    def isBaselineSet(self):
        return Team2ptPerFga.baselineSet


    def setBaseline(self):
        Team2ptPerFga.baselineSet = True


    def setStats(self):
        for proj in super().TeamProjections:
            for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
                if conditions["off_def"] == "offense":
                    label = conditions["label"]
                    #pprint(conditions)
                    self.statProj[label] = self.negotiate(conditions)

        
#----------------------------------------------


class Team3ptAttempt(TeamStat):

    baselineSet = False

    def __init__(self, team, db):
        super().__init__(team, "3pta", db)


    def getDesiredStats(self):
        return ("{0}.tpa",)


    def isBaselineSet(self):
        return Team3ptAttempt.baselineSet


    def setBaseline(self):
        Team3ptAttempt.baselineSet = True


    def setStats(self):
        for proj in super().TeamProjections:
            for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
                if conditions["off_def"] == "offense":
                    label = conditions["label"]
                    #pprint(conditions)

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

    baselineSet = False

    def __init__(self, team, db):
        super().__init__(team, "3ptm", db)


    def getDesiredStats(self):
        return ("{0}.tpm", )


    def isBaselineSet(self):
        return Team3ptMade.baselineSet


    def setBaseline(self):
        Team3ptMade.baselineSet = True


    def setStats(self):
        for proj in super().TeamProjections:
            for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
                if conditions["off_def"] == "offense":
                    label = conditions["label"]
                    #pprint(conditions)

                    threeAtt = self.team.teamStats["3pta"].getStatProj(label)
                    threePct = self.team.teamStats["3pt_pct"].getStatProj(label)
                    
                    self.statProj[label] = round(threeAtt * threePct)

        
#----------------------------------------------


class Team3ptPct(TeamStat):

    baselineSet = False

    def __init__(self, team, db):
        super().__init__(team, "3pt_pct", db)


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


    def isBaselineSet(self):
        return Team3ptPct.baselineSet


    def setBaseline(self):
        Team3ptPct.baselineSet = True


    def setStats(self):
        for proj in super().TeamProjections:
            for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
                if conditions["off_def"] == "offense":
                    label = conditions["label"]
                    #pprint(conditions)
                    self.statProj[label] = self.negotiate(conditions)

        
#----------------------------------------------


class Team3ptPerFga(TeamStat):

    baselineSet = False

    def __init__(self, team, db):
        super().__init__(team, "3pt_per_fga", db)


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


    def isBaselineSet(self):
        return Team3ptPerFga.baselineSet


    def setBaseline(self):
        Team3ptPerFga.baselineSet = True


    def setStats(self):
        for proj in super().TeamProjections:
            for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
                if conditions["off_def"] == "offense":
                    label = conditions["label"]
                    #pprint(conditions)
                    self.statProj[label] = self.negotiate(conditions)


#----------------------------------------------


class TeamAssists(TeamStat):

    baselineSet = False

    def __init__(self, team, db):
        super().__init__(team, "ast", db)


    def getDesiredStats(self):
        return ("{0}.ast", )


    def isBaselineSet(self):
        return TeamAssists.baselineSet


    def setBaseline(self):
        TeamAssists.baselineSet = True


    def setStats(self):
        for proj in super().TeamProjections:
            for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
                if conditions["off_def"] == "offense":
                    label = conditions["label"]
                    #pprint(conditions)
                    
                    astPer = self.team.teamStats["ast_per_fgm"].getStatProj(label)
                    fgm = self.team.teamStats["fgm"].getStatProj(label)
                    
                    self.statProj[label] = round(fgm * astPer)



#----------------------------------------------


class TeamAssistsPerFgm(TeamStat):

    baselineSet = False

    def __init__(self, team, db):
        super().__init__(team, "ast_per_fgm", db)


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


    def isBaselineSet(self):
        return TeamAssistsPerFgm.baselineSet


    def setBaseline(self):
        TeamAssistsPerFgm.baselineSet = True


    def setStats(self):
        for proj in super().TeamProjections:
            for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
                if conditions["off_def"] == "offense":
                    label = conditions["label"]
                    #pprint(conditions)
                    self.statProj[label] = self.negotiate(conditions)


#----------------------------------------------


class TeamBlocks(TeamStat):

    baselineSet = False

    def __init__(self, team, db):
        super().__init__(team, "blk", db)


    def getDesiredStats(self):
        return ("{0}.blk", )


    def isBaselineSet(self):
        return TeamBlocks.baselineSet


    def setBaseline(self):
        TeamBlocks.baselineSet = True


    def setStats(self):
        for proj in super().TeamProjections:
            for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
                if conditions["off_def"] == "offense":
                    label = conditions["label"]
                    #pprint(conditions)
                    
                    p,t,h = label.split("-")
                    if h != "all":
                        h = "home" if h == "away" else "away"
                    oppLabel = "-".join((p,t,h))

                    blkPer = self.team.teamStats["blk_per_fga"].getStatProj(label)
                    fga = self.team.matchup.getOpp(self.team).teamStats["fga"].getStatProj(oppLabel)
                    
                    self.statProj[label] = round(fga * blkPer)



#----------------------------------------------


class TeamBlocksPerFga(TeamStat):

    baselineSet = False

    def __init__(self, team, db):
        super().__init__(team, "blk_per_fga", db)


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


    def isBaselineSet(self):
        return TeamBlocksPerFga.baselineSet


    def setBaseline(self):
        TeamBlocksPerFga.baselineSet = True


    def setStats(self):
        for proj in super().TeamProjections:
            for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
                if conditions["off_def"] == "offense":
                    label = conditions["label"]
                    #pprint(conditions)
                    self.statProj[label] = self.negotiate(conditions)


#----------------------------------------------


class TeamDReb(TeamStat):

    baselineSet = False

    def __init__(self, team, db):
        super().__init__(team, "dreb", db)


    def getDesiredStats(self):
        return ("{0}.dreb", )


    def isBaselineSet(self):
        return TeamDReb.baselineSet


    def setBaseline(self):
        TeamDReb.baselineSet = True


    def setStats(self):
        for proj in super().TeamProjections:
            for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
                if conditions["off_def"] == "offense":
                    label = conditions["label"]
                    #pprint(conditions)
                    
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

    baselineSet = False

    def __init__(self, team, db):
        super().__init__(team, "dreb_per_miss", db)


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


    def isBaselineSet(self):
        return TeamDRebPerMiss.baselineSet


    def setBaseline(self):
        TeamDRebPerMiss.baselineSet = True


    def setStats(self):
        for proj in super().TeamProjections:
            for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
                if conditions["off_def"] == "offense":
                    label = conditions["label"]
                    #pprint(conditions)
                    self.statProj[label] = self.negotiate(conditions)


#----------------------------------------------


class TeamFga(TeamStat):

    baselineSet = False

    def __init__(self, team, db):
        super().__init__(team, "fga", db)


    def getDesiredStats(self):
        return ("{0}.fga", )


    def isBaselineSet(self):
        return TeamFga.baselineSet


    def setBaseline(self):
        TeamFga.baselineSet = True


    def setStats(self):
        for proj in super().TeamProjections:
            for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
                if conditions["off_def"] == "offense":
                    label = conditions["label"]
                    #pprint(conditions)

                    twoPta = self.team.teamStats["2pta"].getStatProj(label)
                    threePta = self.team.teamStats["3pta"].getStatProj(label)
                    
                    self.statProj[label] = round(twoPta + threePta)

        
#----------------------------------------------


class TeamFgm(TeamStat):

    baselineSet = False

    def __init__(self, team, db):
        super().__init__(team, "fgm", db)


    def getDesiredStats(self):
        return ("{0}.fgm", )


    def isBaselineSet(self):
        return TeamFgm.baselineSet


    def setBaseline(self):
        TeamFgm.baselineSet = True


    def setStats(self):
        for proj in super().TeamProjections:
            for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
                if conditions["off_def"] == "offense":
                    label = conditions["label"]
                    #pprint(conditions)

                    twoPtm = self.team.teamStats["2ptm"].getStatProj(label)
                    threePtm = self.team.teamStats["3ptm"].getStatProj(label)
                    
                    self.statProj[label] = round(twoPtm + threePtm)

        
#----------------------------------------------


class TeamFta(TeamStat):

    baselineSet = False

    def __init__(self, team, db):
        super().__init__(team, "fta", db)


    def getDesiredStats(self):
        return ("{0}.fta", )


    def isBaselineSet(self):
        return TeamFta.baselineSet


    def setBaseline(self):
        TeamFta.baselineSet = True


    def setStats(self):
        for proj in super().TeamProjections:
            for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
                if conditions["off_def"] == "offense":
                    label = conditions["label"]
                    #pprint(conditions)
                    
                    p,t,h = label.split("-")
                    if h != "all":
                        h = "home" if h == "away" else "away"
                    oppLabel = "-".join((p,t,h))

                    ftaPer = self.team.teamStats["fta_per_foul"].getStatProj(label)
                    fouls = self.team.matchup.getOpp(self.team).teamStats["fouls"].getStatProj(oppLabel)
                    
                    self.statProj[label] = round(fouls * ftaPer)

        
#----------------------------------------------


class TeamFtm(TeamStat):

    baselineSet = False

    def __init__(self, team, db):
        super().__init__(team, "ftm", db)


    def getDesiredStats(self):
        return ("{0}.ftm", )


    def isBaselineSet(self):
        return TeamFtm.baselineSet


    def setBaseline(self):
        TeamFtm.baselineSet = True


    def setStats(self):
        for proj in super().TeamProjections:
            for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
                if conditions["off_def"] == "offense":
                    label = conditions["label"]
                    #pprint(conditions)

                    fta = self.team.teamStats["fta"].getStatProj(label)
                    ftPct = self.team.teamStats["ft_pct"].getStatProj(label)
                    
                    self.statProj[label] = round(fta * ftPct)

        
#----------------------------------------------


class TeamFtPct(TeamStat):

    baselineSet = False

    def __init__(self, team, db):
        super().__init__(team, "ft_pct", db)


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


    def isBaselineSet(self):
        return TeamFtPct.baselineSet


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



    def setBaseline(self):
        TeamFtPct.baselineSet = True


    def setStats(self):
        for proj in super().TeamProjections:
            for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
                if conditions["off_def"] == "offense":
                    label = conditions["label"]
                    #pprint(conditions)
                    self.statProj[label] = self.negotiate(conditions)

        
#----------------------------------------------


class TeamFouls(TeamStat):

    baselineSet = False

    def __init__(self, team, db):
        super().__init__(team, "fouls", db)


    def getDesiredStats(self):
        return ("{0}.fouls", )


    def isBaselineSet(self):
        return TeamFouls.baselineSet


    def setBaseline(self):
        TeamFouls.baselineSet = True


#----------------------------------------------


class TeamMinutes(TeamStat):

    def __init__(self, team, db):
        super().__init__(team, "mins", db)


    def getDesiredStats(self):
        return ("{0}.fga", )
        

    def isBaselineSet(self):
        return True


    def setStats(self):
        for proj in super().TeamProjections:
            for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
                if conditions["off_def"] == "offense":
                    label = conditions["label"]
                    self.statProj[label] = 48.0*5


    def updateMins(self, label, newMins):
        self.statProj[label] = newMins
        

#----------------------------------------------


class TeamOReb(TeamStat):

    baselineSet = False

    def __init__(self, team, db):
        super().__init__(team, "oreb", db)


    def getDesiredStats(self):
        return ("{0}.oreb", )


    def isBaselineSet(self):
        return TeamOReb.baselineSet


    def setBaseline(self):
        TeamOReb.baselineSet = True


    def setStats(self):
        for proj in super().TeamProjections:
            for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
                if conditions["off_def"] == "offense":
                    label = conditions["label"]
                    orebPer = self.team.teamStats["oreb_per_miss"].getStatProj(label)
                    fga = self.team.teamStats["fga"].getStatProj(label)
                    fgm = self.team.teamStats["fgm"].getStatProj(label)

                    self.statProj[label] = round((fga-fgm) * orebPer)



#----------------------------------------------


class TeamORebPerMiss(TeamStat):

    baselineSet = False

    def __init__(self, team, db):
        super().__init__(team, "oreb_per_miss", db)


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


    def isBaselineSet(self):
        return TeamORebPerMiss.baselineSet


    def setBaseline(self):
        TeamORebPerMiss.baselineSet = True


    def setStats(self):
        for proj in super().TeamProjections:
            for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
                if conditions["off_def"] == "offense":
                    label = conditions["label"]
                    #pprint(conditions)
                    self.statProj[label] = self.negotiate(conditions)


#----------------------------------------------


class TeamPoints(TeamStat):

    baselineSet = False

    def __init__(self, team, db):
        super().__init__(team, "points", db)


    def getDesiredStats(self):
        return ("{0}.points",  )


    def isBaselineSet(self):
        return TeamPoints.baselineSet


    def setBaseline(self):
        TeamPoints.baselineSet = True


    def setStats(self):
        for proj in super().TeamProjections:
            for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
                if conditions["off_def"] == "offense":
                    label = conditions["label"]
                    #pprint(conditions)
                    
                    ftm = self.team.teamStats["ftm"].getStatProj(label)
                    fgm = self.team.teamStats["fgm"].getStatProj(label)
                    tpm = self.team.teamStats["3ptm"].getStatProj(label)
                    
                    self.statProj[label] = round((fgm*2) + ftm + tpm)



#----------------------------------------------


class TeamSteals(TeamStat):

    baselineSet = False

    def __init__(self, team, db):
        super().__init__(team, "stl", db)


    def getDesiredStats(self):
        return ("{0}.stl",  )


    def isBaselineSet(self):
        return TeamSteals.baselineSet


    def setBaseline(self):
        TeamSteals.baselineSet = True


    def setStats(self):
        for proj in super().TeamProjections:
            for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
                if conditions["off_def"] == "offense":
                    label = conditions["label"]
                    #pprint(conditions)
                    
                    p,t,h = label.split("-")
                    if h != "all":
                        h = "home" if h == "away" else "away"
                    oppLabel = "-".join((p,t,h))

                    stealPer = self.team.teamStats["stl_per_turn"].getStatProj(label)
                    turn = self.team.matchup.getOpp(self.team).teamStats["turn"].getStatProj(oppLabel)
                    
                    self.statProj[label] = round(turn * stealPer)


#----------------------------------------------


class TeamStealsPerTurn(TeamStat):

    baselineSet = False

    def __init__(self, team, db):
        super().__init__(team, "stl_per_turn", db)


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


    def isBaselineSet(self):
        return TeamStealsPerTurn.baselineSet


    def setBaseline(self):
        TeamStealsPerTurn.baselineSet = True


    def setStats(self):
        for proj in super().TeamProjections:
            for conditions in self.getGameConditions(proj, itemId=self.team.getTeamId(), haConstraint=self.team.getHomeAway()):
                if conditions["off_def"] == "offense":
                    label = conditions["label"]
                    #pprint(conditions)
                    self.statProj[label] = self.negotiate(conditions)


#----------------------------------------------


class TeamTurnovers(TeamStat):

    baselineSet = False

    def __init__(self, team, db):
        super().__init__(team, "turn", db)


    def getDesiredStats(self):
        return ("{0}.turn", )


    def isBaselineSet(self):
        return TeamTurnovers.baselineSet


    def setBaseline(self):
        TeamTurnovers.baselineSet = True

        
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

    sm = SportsManager()
    nba = sm.getLeague("nba")
    nba.databaseManager.openDB("season")
    db = nba.databaseManager.db["season"]

    createTempTables(db)

    team = Team()


    obj = Team3ptPct(team, db)
    obj.setStats()
    pprint(obj.getJson())
    
