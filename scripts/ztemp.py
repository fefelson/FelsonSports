from LineupSetter import createLineupFile
from SportsDB.DB.NBA import gameDateCmd
from SportsDB.Models.SportsManager import SportsManager
import NBAStats

from datetime import date, timedelta
from itertools import chain
from json import dump, load
from os import environ
from os.path import exists
from pprint import pprint
from sqlite3 import OperationalError

################################################################################


mainPath = environ["HOME"] +"/FEFelson/NBA/BoxScores/{}/{}/{}/"
projPath = mainPath +"proj.json"
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
            # Iterate teamStat list
            for teamStat in NBAStats.teamStatList:
                # Create new stat
##                print("\n{} {}".format(team.abrv.upper(), teamStat.statId))
                newTeamStat = teamStat(team)
                # Add it to it's team
                team.addStat(newTeamStat)

        for team in (self.homeTeam, self.awayTeam):
            print("\n\n"+team.abrv)
            # Iterate the team's players
            for player in chain(team.starters, team.bench):
                print(player)
                # Create a new playerStat in the teamStat
                for teamStat in team.teamStats.values():
                    newPlayerStat = teamStat.getNewPlayerStat()
                    if newPlayerStat:
                        # Add it's player
                        newPlayerStat.setPlayer(player)
                        # Add newPlayerStat to player
                        player.addStat(newPlayerStat)
            print("\n")
            

        self.setTeamStatsA()
        self.setPlayerStatsA()        
        self.setTeamStatsB()
        self.setPlayerStatsB()
        
        
    def getJson(self):
        jsonDict = {"gameId":self.gameId,
                    "homeTeam":self.homeTeam.getJson(),
                    "awayTeam":self.awayTeam.getJson()}
        return jsonDict


    def getOpp(self, team):        
        return self.homeTeam if team.homeAway == "away" else self.awayTeam


    def setPlayerStatsA(self):

        for proj in NBAStats.PlayerStat.projections:
            for team in (self.homeTeam, self.awayTeam):
                team.setPlayerMinutes(proj)
                for player in chain(team.starters, team.bench):
                    for statAbrv in ("fouls", "turn", "2pta", "3pta", "fga", "2pt_pct", "3pt_pct", "fta",
                                 "ft_pct", "stl", "blk"):
                        player.playerStats[statAbrv].setStatEst(proj)

                for player in chain(team.starters, team.bench):
                    for statAbrv in ("fouls", "turn", "2pta", "3pta", "fga", "2pt_pct", "3pt_pct", "fta",
                                 "ft_pct", "stl", "blk"):
                        player.playerStats[statAbrv].setStatAdj(proj)

                for player in chain(team.starters, team.bench):
                    # Add points, fgm for estimates?
                    for statAbrv in ("2ptm", "3ptm", "ftm"):
                        player.playerStats[statAbrv].setStatEst(proj)

                for player in chain(team.starters, team.bench):
                    for statAbrv in ("2ptm", "3ptm", "ftm", "fgm", "points"):
                        player.playerStats[statAbrv].setStatAdj(proj)


    def setPlayerStatsB(self):

        for proj in NBAStats.PlayerStat.projections:
            for team in (self.homeTeam, self.awayTeam):
                for player in chain(team.starters, team.bench):
                    for statAbrv in ("ast", "oreb", "dreb"):
                        player.playerStats[statAbrv].setStatEst(proj)

                for player in chain(team.starters, team.bench):
                    for statAbrv in ("ast", "oreb", "dreb"):
                        player.playerStats[statAbrv].setStatAdj(proj)


    def setTeamStatsA(self):

        for proj in NBAStats.TeamStat.projections:
            for team in (self.homeTeam, self.awayTeam):

                team.teamStats["mins"].setStats(proj)
                team.teamStats["poss"].setStats(proj)
                team.teamStats["fouls"].setStats(proj)
                team.teamStats["turn"].setStats(proj)
                team.teamStats["stl_per_turn"].setStats(proj)
                team.teamStats["fta_per_foul"].setStats(proj)
                team.teamStats["3pt_per_fga"].setStats(proj)
                team.teamStats["blk_per_fga"].setStats(proj)
                team.teamStats["ft_pct"].setStats(proj)
                team.teamStats["2pt_pct"].setStats(proj)
                team.teamStats["3pt_pct"].setStats(proj)
                team.teamStats["oreb_per_miss"].setStats(proj)
                team.teamStats["dreb_per_miss"].setStats(proj)
                team.teamStats["ast_per_fgm"].setStats(proj)
                

                
            for team in (self.homeTeam, self.awayTeam):
                team.teamStats["fta"].setStats(proj)
                team.teamStats["2pta"].setStats(proj)
                team.teamStats["3pta"].setStats(proj)
                team.teamStats["fga"].setStats(proj)
                team.teamStats["stl"].setStats(proj)


            for team in (self.homeTeam, self.awayTeam):
                team.teamStats["blk"].setStats(proj)


    def setTeamStatsB(self):

        for proj in NBAStats.TeamStat.projections:

            for team in (self.homeTeam, self.awayTeam):
                team.teamStats["ftm"].setStats(proj)
                team.teamStats["2ptm"].setStats(proj)
                team.teamStats["3ptm"].setStats(proj)
                team.teamStats["fgm"].setStats(proj)


            for team in (self.homeTeam, self.awayTeam):
                team.teamStats["ast"].setStats(proj)
                team.teamStats["oreb"].setStats(proj)
                team.teamStats["dreb"].setStats(proj)
                team.teamStats["points"].setStats(proj)

        
        
        

################################################################################


class Team:

    def __init__(self, matchup, info, homeAway, oppId):

        self.matchup = matchup         
        self.homeAway = homeAway
        self.teamId = info["teamId"]
        self.abrv = info["abrv"]
        self.name = info["name"]
        self.oppId = oppId
        self.teamStats = {}
        self.starters = [Player(team=self, info=player, starter=True) for player in info["starters"]]
        self.bench = [Player(team=self, info=player) for player in info["bench"]]

        self.lineupGames = self.setLineupGames()
        self.matchupGames = self.setMatchupGames()
        self.b2bGames = None

                
        if db.curs.execute("SELECT stats.game_id FROM team_stats AS stats INNER JOIN games ON stats.game_id = games.game_id WHERE team_id = ? AND game_year = ? AND game_day = ?",(self.teamId, yesterday.year, ".".join(str(yesterday).split("-")[1:]))).fetchone():
            self.setB2bGames()        


    def addStat(self, stat):
        stat.setDB(db)
        stat.crunchNumbers()
        self.teamStats[stat.getStatId()] = stat


    def getB2bGames(self):
        return self.b2bGames


    def getJson(self):
        jsonDict = {"teamId": self.teamId,
                    "abrv": self.abrv,
                    "oppId": self.oppId,
                    "starters": [],
                    "bench": [],
                    "teamStats": {}}
        for player in self.starters:
            jsonDict["starters"].append(player.getJson())

        for player in self.bench:
            jsonDict["bench"].append(player.getJson())

        for key, value in self.teamStats.items():
            jsonDict["teamStats"][key] = value.getJson()
        return jsonDict


    def getHomeAway(self):
        return self.homeAway


    def getLineupGames(self):
        return self.lineupGames
    

    def getMatchupGames(self):
        return self.matchupGames


    def getOppId(self):
        return self.oppId

    
    def getTeamId(self):
        return self.teamId


    def setB2bGames(self):
        self.b2bGames = tuple([g[0] for g in db.curs.execute("SELECT b2b.game_id FROM back_to_back AS b2b INNER JOIN ("+seasonCmd+") AS gd ON b2b.game_id = gd.game_id WHERE team_id = ?",(self.teamId,)).fetchall()])


    def setLineupGames(self, starterList=[], games=[], index=5):
        games = set(games)
        gameTotal = len(db.curs.execute("SELECT stats.game_id FROM team_stats AS stats INNER JOIN ("+seasonCmd+") AS games ON stats.game_id = games.game_id WHERE team_id = ?", (self.teamId,)).fetchall())
        if not starterList:
            starterList = sorted([db.curs.execute("SELECT stats.player_id, COUNT(stats.game_id) FROM player_stats AS stats INNER JOIN ("+seasonCmd+") AS gd ON stats.game_id = gd.game_id WHERE starter = 1 AND stats.player_id = ? AND team_id = ?",(starter.playerId,self.teamId)).fetchone() for starter in self.starters], key=lambda x: x[-1], reverse=True)
       
        startCmd = "SELECT game_id FROM player_stats WHERE starter = 1 AND player_id = {} AND team_id = {}"

        cmds = [" INNER JOIN (" + startCmd.format(starter,self.teamId) +") AS table{0} ON stats.game_id = table{0}.game_id".format(i) for i, starter in enumerate([x[0] for x in starterList[:index]])]
        cmd = "SELECT DISTINCT stats.game_id FROM player_stats AS stats INNER JOIN ("+ gameDateCmd(seasons=("2019",))+") AS games ON stats.game_id = games.game_id"+"".join(cmds)

        
        try:
            for gameId in [x[0] for x in db.curs.execute(cmd).fetchall()]:
                games.add(gameId)
        except OperationalError:
            pass

       
        
        if len(games) < gameTotal/3:
            cmd = "SELECT DISTINCT stats.game_id FROM player_stats AS stats INNER JOIN ("+ gameDateCmd(seasons=("2019",))+") AS games ON stats.game_id = games.game_id WHERE starter = 1 AND stats.player_id = ? AND team_id = ?"
            for gameId in [x[0] for x in db.curs.execute(cmd, (starterList[-1][0], self.teamId)).fetchall()]:
                games.add(gameId)

        if len(games) < gameTotal/3:
            games = self.setLineupGames(starterList, games, index-1)

        if len(games) > gameTotal:
            raise AssertionError
##        print(gameTotal, len(games))
       
        return tuple(games)


    def setMatchupGames(self):
        return tuple([g[0] for g in db.curs.execute("SELECT stats.game_id FROM team_stats AS stats INNER JOIN ("+seasonCmd+") AS gd ON stats.game_id = gd.game_id WHERE team_id = ? AND opp_id = ?",(self.teamId,self.oppId)).fetchall()])


    def setPlayerMinutes(self, proj):
        
        for player in chain(self.starters,self.bench):
            player.playerStats["mins"].setStatEst(proj)

        for conditions in NBAStats.getGameConditions(itemId=self.getTeamId(), haConstraint=self.getHomeAway()):
    
            for pos, starter in NBAStats.getPlayerConditions(player=player):
                posProjComponent = "_{}".format(pos) if pos else ""
                startProjComponent = "_{}".format(starter) if starter else ""
                posLabelComponent = "_pos" if pos else ""
                startLabelComponent = "_start" if starter else ""

                label = proj["proj_id"]+posLabelComponent+startLabelComponent+"-"+conditions["label"]              

                for player in chain(self.starters, self.bench):
                    totalMins = self.teamStats["mins"].getForPlayerProj(label)
                    newMins = player.playerStats["mins"].getStatEst(label)
                    if newMins > totalMins:
                        newMins = totalMins
                        totalMins = 0
                    else:
                        totalMins -= newMins
                    player.playerStats["mins"].setStatAdj(label, newMins)
                    self.teamStats["mins"].updateMins(label, totalMins)                 
   
               
################################################################################


class Player:


    def __init__(self, team, info, starter=False):

        self.playerId = info["playerId"]
        self.firstName = info["firstName"]
        self.lastName = info["lastName"]
        self.team = team
        self.status = info["status"]
        self.starter = 1 if starter else 0
        self.pos = db.curs.execute("SELECT position FROM pro_players WHERE player_id = ?",(self.playerId,)).fetchone()[0]
        self.pos = "PG" if self.pos == "G" else self.pos
        self.pos = "SF" if self.pos == "F" else self.pos
        self.playerStats = {}


    def __str__(self):
        return "{:<8}{:<4}{:<10}{:<20}".format(self.playerId, self.pos, self.firstName, self.lastName)  


    def addStat(self, stat):
        stat.setDB(db)
        stat.crunchNumbers()
        self.playerStats[stat.getStatId()] = stat


    def getHomeAway(self):
        return self.team.getHomeAway()


    def getJson(self):
        jsonDict = {"playerId":self.playerId,
                    "name": self.firstName+" "+self.lastName,
                    "status": self.status,
                    "starter": self.starter,
                    "playerStats":{}}
        for key, value in self.playerStats.items():
            jsonDict["playerStats"][key] = value.getJson()
        return jsonDict


    def getPlayerId(self):
        return self.playerId


    def getOppId(self):
        return self.team.getOppId()


################################################################################


if __name__ == "__main__":

##    print("Dropping Tables\n")
##    NBAStats.dropTables(db)
    print("Creating Temp Tables\n")
    NBAStats.createTempTables(db)

    print("Setting Team Baselines\n")
    NBAStats.setTeamBaselines(db)
    NBAStats.makeTeamBuckets(db)
    NBAStats.setTeamBuckets(db)

    print("Setting Vs Baselines\n")
    NBAStats.setTeamVsBaselines(db)
    NBAStats.makeTeamVsBuckets(db)
    NBAStats.setTeamVsBuckets(db)
  
    print("Setting Player Baselines\n")
    NBAStats.setPlayerBaselines(db)
    NBAStats.makePlayerBuckets(db)
    NBAStats.setPlayerBuckets(db)


    
      
    matchups = []

    if not exists(lineupPath.format(*str(gameDate).split("-"))):
        createLineupFile(gameDate)

    with open(lineupPath.format(*str(gameDate).split("-"))) as fileIn:
        for match in load(fileIn)["matchups"]:
            newMatchup = Matchup(match).getJson()
            matchups.append(newMatchup)
            with open(mainPath.format(*str(gameDate).split("-"))+"P{}.json".format(newMatchup["gameId"]), "w") as fileOut:
                dump({"matchups":[newMatchup,]}, fileOut)

##    pprint(matchups)

    
    with open(projPath.format(*str(gameDate).split("-")), "w") as fileOut:
        dump({"matchups":matchups}, fileOut)
