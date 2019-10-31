from LineupSetter import createLineupFile
from SportsDB.DB.NBA import gameDateCmd
from SportsDB.Models.SportsManager import SportsManager
import CollegeStats

from datetime import date, timedelta
from json import dump, load
from os import environ
from os.path import exists
from pprint import pprint

################################################################################


mainPath = environ["HOME"] +"/FEFelson/NBA/BoxScores/{}/{}/{}/"
lineupPath = mainPath + "lineups.json"


################################################################################


sm = SportsManager()
nba = sm.getLeague("nba")
nba.databaseManager.openDB("season")
db = nba.databaseManager.db["season"]
gameDate = date.today()
yesterday = gameDate - timedelta(1)
seasonCmd = gameDateCmd(seasons=("2019",))


################################################################################


class Matchup:

    def __init__(self, info):

        
        self.gameId = info["gameId"]
      
        self.homeTeam = Team(matchup=self, info=info["homeTeam"], homeAway="home", oppId=info["awayTeam"]["teamId"])
        self.awayTeam = Team(matchup=self, info=info["awayTeam"], homeAway="away", oppId=info["homeTeam"]["teamId"])

        for team in (self.homeTeam, self.awayTeam):
            for stat in Stats.teamStats:
                team.addStat(stat)

        self.setTeamStatsA()
        self.setTeamStatsB()

        
    def getJson(self):
        jsonDict = {"gameId":self.gameId,
                    "homeTeam":self.homeTeam.getJson(),
                    "awayTeam":self.awayTeam.getJson()}
        return jsonDict


    def getOpp(self, team):        
        return self.homeTeam if team.homeAway == "away" else self.awayTeam


    def setTeamStatsA(self):

        for team in (self.homeTeam, self.awayTeam):
            team.teamStats["mins"].setStats()
            team.teamStats["poss"].setStats()
            team.teamStats["fouls"].setStats()
            team.teamStats["turn"].setStats()
            team.teamStats["stl_per_turn"].setStats()
            team.teamStats["fta_per_foul"].setStats()
            team.teamStats["2pt_per_fga"].setStats()
            team.teamStats["3pt_per_fga"].setStats()
            team.teamStats["blk_per_fga"].setStats()
            team.teamStats["ft_pct"].setStats()
            team.teamStats["2pt_pct"].setStats()
            team.teamStats["3pt_pct"].setStats()
            team.teamStats["oreb_per_miss"].setStats()
            team.teamStats["dreb_per_miss"].setStats()
            team.teamStats["ast_per_fgm"].setStats()
            

            
        for team in (self.homeTeam, self.awayTeam):
            team.teamStats["fta"].setStats()
            team.teamStats["2pta"].setStats()
            team.teamStats["3pta"].setStats()
            team.teamStats["fga"].setStats()
            team.teamStats["stl"].setStats()


        for team in (self.homeTeam, self.awayTeam):
            team.teamStats["blk"].setStats()


    def setTeamStatsB(self):

        for team in (self.homeTeam, self.awayTeam):
            team.teamStats["ftm"].setStats()
            team.teamStats["2ptm"].setStats()
            team.teamStats["3ptm"].setStats()
            team.teamStats["fgm"].setStats()


        for team in (self.homeTeam, self.awayTeam):
            team.teamStats["ast"].setStats()
            team.teamStats["oreb"].setStats()
            team.teamStats["dreb"].setStats()
            team.teamStats["points"].setStats()

        
        
        

################################################################################


class Team:

    def __init__(self, matchup, info, homeAway, oppId):

        self.matchup = matchup         
        self.homeAway = homeAway
        self.teamId = info["teamId"]
        self.abrv = info["abrv"]
        self.name = info["name"]
        self.oppId = oppId
        print(self.abrv)

        self.matchupGames = None
        self.b2bGames = None

        self.setMatchupGames()
        
        if db.curs.execute("SELECT stats.game_id FROM team_stats AS stats INNER JOIN games ON stats.game_id = games.game_id WHERE team_id = ? AND game_year = ? AND game_day = ?",(self.teamId, yesterday.year, ".".join(str(yesterday).split("-")[1:]))).fetchone():
            self.setB2bGames()        


        self.teamStats = {}


    def addStat(self, stat):
        newStat = stat(self, db)
        self.teamStats[newStat.getStatId()] = newStat


    def getB2bGames(self):
        return self.b2bGames


    def getJson(self):
        jsonDict = {"teamId": self.teamId,
                    "abrv": self.abrv,
                    "oppId": self.oppId,
                    #"starters": [],
                    #"bench": [],
                    "teamStats": {}}
##        for player in self.starters:
##            jsonDict["starters"].append(player.getJson())
##
##        for player in self.bench:
##            jsonDict["bench"].append(player.getJson())

        for key, value in self.teamStats.items():
            jsonDict["teamStats"][key] = value.getJson()
        return jsonDict


    def getHomeAway(self):
        return self.homeAway


    def getOppId(self):
        return self.oppId

    
    def getTeamId(self):
        return self.teamId


    def getMatchupGames(self):
        return self.matchupGames


    def setB2bGames(self):
        self.b2bGames = tuple([g[0] for g in db.curs.execute("SELECT b2b.game_id FROM back_to_back AS b2b INNER JOIN ("+seasonCmd+") AS gd ON b2b.game_id = gd.game_id WHERE team_id = ?",(self.teamId,)).fetchall()])


    def setMatchupGames(self):
        self.matchupGames = tuple([g[0] for g in db.curs.execute("SELECT stats.game_id FROM team_stats AS stats INNER JOIN ("+seasonCmd+") AS gd ON stats.game_id = gd.game_id WHERE team_id = ? AND opp_id = ?",(self.teamId,self.oppId)).fetchall()])
   
               
################################################################################


if __name__ == "__main__":

    Stats.createTempTables(db)
      
    matchups = []

    if not exists(lineupPath.format(*str(gameDate).split("-"))):
        createLineupFile(gameDate)

    with open(lineupPath.format(*str(gameDate).split("-"))) as fileIn:
        for match in load(fileIn)["matchups"]:
            matchups.append(Matchup(match).getJson())

    pprint(matchups)

    
##    with open(projPath.format(*str(gameDate).split("-")), "w") as fileOut:
##        dump({"matchups":matchups}, fileOut)
