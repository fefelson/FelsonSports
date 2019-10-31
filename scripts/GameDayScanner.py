from json import dump, load
from csv import reader
from sqlite3 import connect, ProgrammingError
from os import environ
from pprint import pprint
from itertools import chain
from datetime import date, timedelta
from SportsDB.WebService.ESPN import TeamParser as TP
import operator
import numpy

league = "NBA"
season = 2019
filePath = environ["HOME"] + "/FEFelson/{}/BoxScores/{}/{}/{}/{}.json"
dbPath = environ["HOME"] + "/FEFelson/{}.db"

conn = connect(dbPath.format(league))
curs = conn.cursor()


sumTwoCmd = "SELECT SUM({0[div]}), SUM({0[stat]}) FROM player_stats AS totals"
countGPCmd = "SELECT COUNT(totals.player_id), SUM({0[stat]}) FROM player_stats AS totals"

similarCmd = "SELECT stats.player_id FROM player_{0[view]} AS stats INNER JOIN (SELECT player_id, {0[stat]}, {0[stat2]}, position FROM player_season WHERE player_id = ?) as player ON stats.{0[stat]} = player.{0[stat]} AND stats.{0[stat2]} = player.{0[stat2]} AND stats.position = player.position WHERE stats.player_id != ?"
gamesAgainstCmd = "SELECT game_id, stats.team_id FROM {0[item]}_stats AS stats INNER JOIN (SELECT distinct team_id, opp_id FROM {0[item]}_stats WHERE {0[item]}_id = ?) as teams ON stats.team_id = teams.opp_id WHERE stats.opp_id != teams.team_id"
homeAwayCmd = "SELECT games.game_id, stats.player_id FROM games INNER JOIN player_stats AS stats ON games.game_id = stats.game_id AND games.{0[home]}_id = stats.team_id WHERE player_id = ?"
homeAwaySimilarCmd = "SELECT games.game_id, stats.player_id FROM games INNER JOIN player_stats AS stats ON games.game_id = stats.game_id AND games.{0[home]}_id = stats.team_id WHERE player_id IN (" + similarCmd + ") AND opp_id = ?"
homeAwayAgainstCmd = "SELECT games.game_id, stats.player_id FROM games INNER JOIN player_stats AS stats ON games.game_id = stats.game_id AND games.{0[home]}_id = stats.team_id INNER JOIN (" + gamesAgainstCmd + ") AS against ON games.game_id = against.game_id AND stats.team_id = against.team_id WHERE stats.player_id IN (" + similarCmd + ")"




gameDate = date.today()
yesterday = gameDate - timedelta(1)

twoWeeks = gameDate - timedelta(14)
lastMonth = gameDate - timedelta(30)

sbPath = filePath.format(league, *str(gameDate).split("-"), "scoreboard")


def gameDateCmd(newDate, pastDate):
    cmd = "SELECT game_id FROM games WHERE season = {}".format(season)
    if pastDate.year != newDate.year:
        cmd += " AND ((game_year = {0[pastYear]} AND game_day >= {0[pastDay]}) OR (game_year = {0[newYear]} AND game_day >= 1.01))".format({"pastYear":pastDate.year,"pastDay":".".join(str(pastDate).split("-")[1:]),"newYear":newDate.year})
    else:
        cmd += " AND game_year = {} AND game_day >= {}".format(pastDate.year, ".".join(str(pastDate).split("-")[1:]))
    return cmd


def gameSeasonCmd(season):
    cmd = "SELECT game_id FROM games WHERE season = {}".format(season)
    return cmd


def statEval(cmds, items):
    itemStat = 0; itemUp = 1


    try:
        #print(cmds["statsAgainst"])
        #rint("")
        stats = curs.execute(cmds["stats"], items["stats"]).fetchone()
        #print(cmds["stats"], items, stats)
        #print("")
        statsAgainst = curs.execute(cmds["statsAgainst"], items["statsAgainst"]).fetchone()
        #print(cmds["statsAgainst"], items, statsAgainst)
        #print("")

        itemStat = stats[1]/stats[0]
        itemUp = itemStat/(statsAgainst[1]/statsAgainst[0])

        #print(itemStat, statsAgainst[1]/statsAgainst[0])
    except TypeError:
        pass
    except ZeroDivisionError:
        pass

    itemStat = 0 if itemStat == None else itemStat
    itemUp = 1 if itemUp == None else itemUp

    return itemStat, itemUp


def setStatProj(itemCmds, oppCmds, items, oppItems):

    value = None
    itemStat, itemUp = statEval(itemCmds, items)
    oppStat, oppUp = statEval(oppCmds, oppItems)

    if oppStat > 0:
        value = ((itemStat*oppUp) + (oppStat*itemUp))/2
    else:
        value = itemStat*oppUp

    #print(itemStat, itemUp, oppStat, oppUp, value)

    return value




def makeCmds(cmds, addIns, items):
    """
        cmds["stats"] = teamCmd.format(("rush_atts",))
        cmds["statsAgainst"] = teamAgainstCmd.format(("rush_atts",))
        or
        cmds["stats"] = teamCmd.format(("opp_rush_atts",))
        cmds["statsAgainst"] = teamAgainstCmd.format(("rush_atts",))
    """
    statCmds = {}
    itemDict = {}           


    for i, label in enumerate(("stats", "statsAgainst")):
        statCmds[label] = cmds[i].format(addIns)
        itemDict[label] = items[i]
    #pprint(statCmds)
    return itemDict, statCmds



class Player:
    printFormat = "{} {}  {:.2f} "+"".join(" {:.1f}"+x for x in ("min", "fga","fgm","fta","ftm","tpa","tpm","oreb","dreb","ast","stl","blk","turn","points"))        


    def __init__(self, playerId, team, d2d=None):

        self.playerId = playerId
        self.team = team
        self.d2d = d2d

        self.stats = {}
        self.makeStats()
        self.score = {"season": 0, "month": 0}


    def __str__(self):
        name = curs.execute("SELECT first_name, last_name FROM pro_players WHERE player_id = ?", (self.playerId,)).fetchone()
        line1 = Player.printFormat.format(*name, self.score["season"], *[self.stats[x]["season"] for x in ("min", "fga","fgm","fta","ftm","tpa","tpm","oreb","dreb","ast","stl","blk","turn","points")]) +"\n"
        line2 = Player.printFormat.format(*name, self.score["month"], *[self.stats[x]["month"] for x in ("min", "fga","fgm","fta","ftm","tpa","tpm","oreb","dreb","ast","stl","blk","turn","points")]) +"\n"
        return line1+line2        

    def getId(self):
        return self.playerId


    def makeStats(self):
        for stat in ("min", "fga", "fgm", "tpa", "tpm", "fta", "ftm", "oreb", "dreb", "ast", "stl", "blk", "turn", "points"):
            self.stats[stat] = {"season":0,"month":0}



    def getMinProj(self, view, starter):
        #print("setMins")
        playerId = self.playerId
        teamId = self.team.oppId
        starter = 1 if starter else 0
        playerHome = "home" if self.team.isHome else "away"
        stat = "min"

        if view == "season":
            gpCmd = gameSeasonCmd(season)
        else:
            gpCmd = gameDateCmd(gameDate, lastMonth)
            
        playerCountCmd = countGPCmd + " INNER JOIN (" + gpCmd + ") AS game_date ON totals.game_id = game_date.game_id INNER JOIN (" + homeAwayCmd + ") AS home ON totals.game_id = home.game_id AND totals.player_id = home.player_id WHERE starter = "+str(starter)
        playerCountAgainstCmd = countGPCmd + " INNER JOIN (" + gpCmd + ") AS game_date ON totals.game_id = game_date.game_id" + " INNER JOIN (" + homeAwayAgainstCmd + ") AS home ON totals.game_id = home.game_id AND totals.player_id = home.player_id WHERE starter = "+str(starter)
        teamCountCmd = countGPCmd + " INNER JOIN (" + gpCmd + ") AS game_date ON totals.game_id = game_date.game_id" + " INNER JOIN (" + homeAwaySimilarCmd + ") AS home ON totals.game_id = home.game_id AND totals.player_id = home.player_id WHERE starter = "+str(starter)
        teamCountAgainstCmd = countGPCmd + " INNER JOIN (" + gpCmd + ") AS game_date ON totals.game_id = game_date.game_id" + " INNER JOIN (" + homeAwayAgainstCmd + ") AS home ON totals.game_id = home.game_id AND totals.player_id = home.player_id WHERE starter = "+str(starter)

        playerAddIns = {"stat":stat, "stat2": "starter", "home":playerHome, "item":"player", "view":view}
        teamAddIns = {"stat":stat,  "stat2": "starter", "home":playerHome, "item":"team", "view":view}
        
        items, itemCmds = makeCmds((playerCountCmd, playerCountAgainstCmd), playerAddIns, ((playerId,), (playerId, playerId, playerId)))
        oppItems, oppCmds = makeCmds((teamCountCmd, teamCountAgainstCmd), teamAddIns, ((playerId, playerId, teamId), (teamId, playerId, playerId)))
        
        return setStatProj(itemCmds, oppCmds, items, oppItems) 


    def setMinProj(self, view, proj):
        self.stats["min"][view] = proj


    def scorePlayer(self):
        for view in ("season", "month"):
            self.score[view] += self.stats["points"][view]
            self.score[view] += self.stats["tpm"][view]*.5
            self.score[view] += (self.stats["oreb"][view] + self.stats["dreb"][view]) * 1.25
            self.score[view] += self.stats["ast"][view] * 1.5
            self.score[view] += self.stats["stl"][view] * 2
            self.score[view] += self.stats["blk"][view] * 2
            self.score[view] += self.stats["turn"][view] * -.5

            total = 0
            for stat in (self.stats["points"][view], (self.stats["oreb"][view] + self.stats["dreb"][view]), self.stats["ast"][view], self.stats["stl"][view], self.stats["blk"][view]):
                if stat >= 10:
                    total += 1
            if total >= 2:
                self.score[view] += 1.5

            if total >=3:
                self.score[view] += 3


    def setProjections(self):
        playerId = self.playerId
        teamId = self.team.oppId
        playerHome = "home" if self.team.isHome else "away"
        
        for view in ("season", "month"):

            if view == "season":
                gpCmd = gameSeasonCmd(season)
            else:
                gpCmd = gameDateCmd(gameDate, lastMonth)
                
            for stat in ("fga", "fgm", "tpa", "tpm", "fta", "ftm", "oreb", "dreb", "ast", "stl", "blk", "turn", "points"):
                stat2 = {}
                div = {"fgm": "fga", "tpm": "tpa"}
                if stat not in ("ftm", "points"):

                    playerSumCmd = sumTwoCmd + " INNER JOIN (" + gpCmd + ") AS game_date ON totals.game_id = game_date.game_id INNER JOIN (" + homeAwayCmd + ") AS home ON totals.game_id = home.game_id AND totals.player_id = home.player_id"
                    playerSumAgainstCmd = sumTwoCmd + " INNER JOIN (" + gpCmd + ") AS game_date ON totals.game_id = game_date.game_id INNER JOIN (" + homeAwayAgainstCmd + ") AS home ON totals.game_id = home.game_id AND totals.player_id = home.player_id"
                    teamSumCmd = sumTwoCmd + " INNER JOIN (" + gpCmd + ") AS game_date ON totals.game_id = game_date.game_id INNER JOIN (" + homeAwaySimilarCmd + ") AS home ON totals.game_id = home.game_id AND totals.player_id = home.player_id"
                    teamSumAgainstCmd = sumTwoCmd + " INNER JOIN (" + gpCmd + ") AS game_date ON totals.game_id = game_date.game_id INNER JOIN (" + homeAwayAgainstCmd + ") AS home ON totals.game_id = home.game_id AND totals.player_id = home.player_id"

                    playerAddIns = {"stat":stat, "stat2": stat2.get(stat, "min"), "div": div.get(stat, "min"), "home": playerHome, "item":"player", "view":view}
                    teamAddIns = {"stat":stat, "stat2": stat2.get(stat, "min"), "div": div.get(stat, "min"), "home": playerHome, "item":"team", "view":view}
    
                    items, itemCmds = makeCmds((playerSumCmd, playerSumAgainstCmd), playerAddIns, ((playerId,), (playerId, playerId, playerId)))
                    oppItems, oppCmds = makeCmds((teamSumCmd, teamSumAgainstCmd), teamAddIns, ((playerId, playerId, teamId), (teamId, playerId, playerId)))

                if stat == "ftm":
                    try:
                        cmd = "SELECT (SUM(ftm)*1.0)/(SUM(fta)*1.0) FROM player_stats AS stats INNER JOIN (" + homeAwayCmd.format({"home":playerHome}) + ") AS home ON stats.game_id = home.game_id AND stats.player_id = home.player_id"
                        ftPct = curs.execute(cmd, (playerId,)).fetchone()[0]
                    except TypeError:
                        pass
                    except ZeroDivisionError:
                        pass
                    ftPct = 0 if ftPct == None else ftPct
                    self.stats[stat][view] = ftPct * self.stats["fta"][view]              
                    
                    
                elif stat == "turn":
                    result = setStatProj(itemCmds, oppCmds, items, oppItems)
                    self.stats[stat][view] = result * self.stats[div.get(stat,"min")][view]
                    self.stats[stat][view] = 5 if result >5 else result
        

                elif stat == "points":
                    self.stats[stat][view] = (self.stats["fgm"][view]*2)+(self.stats["tpm"][view])+(self.stats["ftm"][view])
                else:
                    self.stats[stat][view] = setStatProj(itemCmds, oppCmds, items, oppItems) *self.stats[div.get(stat,"min")][view]
                    
                    
            

    

class Team:

    def __init__(self, teamId, oppId, isHome, injuries):

        self.teamId = teamId
        self.oppId = oppId
        self.isHome = isHome
        self.abrv = curs.execute("SELECT abrv FROM pro_teams WHERE team_id = ?", (teamId,)).fetchone()[0]
        self.b2b = self.setB2B()
        print(self.abrv)

        self.injuries = injuries
        self.roster = self.setRoster()
        self.starters = self.setStarters()
        self.bench = self.setBench()
        self.setMinutes()
        for player in chain(self.starters,self.bench):
            player.setProjections()
            player.scorePlayer()
            print(player)


    def setMinutes(self):
        minutesTotal = {"season":5*48, "month":5*48}
        for view in ("season", "month"):
            total = minutesTotal[view]
            for player in chain(self.starters, self.bench):
                playerMinutes = player.getMinProj(view, player in self.starters)
                newMinutes = total - playerMinutes
                if newMinutes < 0:
                    playerMinutes = total
                    newMinutes = 0
                player.setMinProj(view, playerMinutes)
                total = newMinutes
                


    def setRoster(self):
        out = [x["player_id"] for x in self.injuries if x["status"] == "Out"]
        d2d = {x["player_id"]: x["date"] for x in self.injuries if x["status"] == "Day-To-Day"}
        players = {}
        for playerId in TP.getRoster(self.abrv, "nba"):
            if playerId not in out and curs.execute("SELECT COUNT(player_id) FROM player_stats as stats INNER JOIN ( " + gameSeasonCmd(season) + ") AS gd ON stats.game_id = gd.game_id WHERE player_id = ?", (playerId,)).fetchone()[0]:
                players[playerId] = Player(playerId, self, d2d.get(playerId, None))
            
        return players    


    def setB2B(self):
        b2b = False
        try:
            curs.execute("SELECT games.game_id FROM games INNER JOIN (" + gameDateCmd(gameDate, yesterday) + ") AS gd ON games.game_id = gd.game_id WHERE home_id = {0} OR away_id = {0}".format(teamId)).fetchone()[0]
            b2b = True
        except TypeError:
            pass
        return b2b
    

    def setStarters(self):
        cmd = "SELECT player_id, COUNT(player_id), (SUM(starter)*1.0)/(COUNT(player_id)*1.0), AVG(min) FROM player_stats INNER JOIN (" + gameDateCmd(gameDate, twoWeeks) + ") AS gd ON player_stats.game_id = gd.game_id WHERE player_id = ?"
        players = [curs.execute(cmd, (playerId,)).fetchone() for playerId in self.roster.keys() if curs.execute(cmd, (playerId,)).fetchone()[0]]
        players = sorted(players, key=operator.itemgetter(2, 1, 3), reverse=True)
        return [self.roster[x[0]] for x in players[:5]]


    def setBench(self):
        cmd = "SELECT stats.player_id, COUNT(stats.player_id), start.min FROM player_stats as stats INNER JOIN (" + gameDateCmd(gameDate, twoWeeks) + ") AS gd ON stats.game_id = gd.game_id INNER JOIN (SELECT player_id, AVG(min) as min FROM player_stats INNER JOIN (" + gameDateCmd(gameDate, twoWeeks) + ") AS gd ON player_stats.game_id = gd.game_id WHERE player_id = ? AND starter = 0) AS start ON stats.player_id = start.player_id"
        players = [curs.execute(cmd, (playerId,)).fetchone() for playerId, player in self.roster.items() if player not in self.starters and curs.execute(cmd, (playerId,)).fetchone()[0] ]
        players = sorted(players, key=operator.itemgetter(1, 2), reverse=True)
        return [self.roster[x[0]] for x in players]



#
        
        
                            

        
posTotalCmd = "SELECT player_id, position, COUNT(position) AS pos_count FROM positions INNER JOIN games ON positions.game_id = games.game_id WHERE season = 2019 AND game_day >= 11.20 GROUP BY player_id, position"
posCmd = "SELECT player_id, position, MAX(pos_count), SUM(pos_count) AS gp FROM ({}) AS totals GROUP BY player_id".format(posTotalCmd)

stats = ("starter", "min", "fga", "fgm", "tpa", "tpm", "fta", "ftm", "oreb", "dreb", "ast", "stl", "blk", "turn", "points")
playerViewCmd = "CREATE TEMP VIEW player_{} AS SELECT player_stats.player_id AS player_id, COUNT(player_stats.player_id) as gp, pos.position as position, "

perMin = "(SUM({})*1.0)/({}*1.0)"

for view in ("season", "month"):
    newViewCmd = playerViewCmd.format(view)

    if view == "season":
        gpCmd = gameSeasonCmd(season)
    else:
        gpCmd = gameDateCmd(gameDate, lastMonth)

    for stat in stats:
        divisor = "COUNT(player_stats.player_id)" if (stat == "min" or stat == "starter") else "SUM(min)"
        perMins = perMin.format(stat, divisor)
        cmd = "SELECT" + perMins + " FROM player_stats INNER JOIN (" + gpCmd + ") AS gd ON player_stats.game_id = gd.game_id GROUP BY player_stats.player_id"
        #print(cmd)
        points = [x[0] for x in curs.execute(cmd).fetchall() if x[0] != None]
        #pprint(points)
    ##    print(cmd)
        mean = numpy.mean(points)
        std = numpy.std(points)
        #print(mean, std)
        
        newViewCmd += " (CASE" + "".join([" WHEN {} THEN '{}'".format(perMins+" >= {}".format(exp), result) for exp,result in ((mean+std, "elite"),(mean,"good"), (mean-std,"ok"))]) + " ELSE 'poor' END) AS {}".format(stat)
        newViewCmd += "," if stat != stats[-1] else ""
        #print(newCmd)
    newViewCmd += " FROM player_stats INNER JOIN (SELECT player_id, COUNT(player_stats.player_id) AS gp FROM player_stats GROUP BY player_stats.player_id) AS games_played ON player_stats.player_id = games_played.player_id INNER JOIN (" + gpCmd + ") AS gd ON player_stats.game_id = gd.game_id INNER JOIN ({}) as pos ON player_stats.player_id = pos.player_id GROUP BY player_stats.player_id".format(posCmd)
    #pprint(playerViewCmd)

    curs.execute(newViewCmd)

        









matchupIds = []
teams = {}

with open(sbPath) as jsonFile:
    matchups = load(jsonFile)
    matchupIds = [ x["game_id"] for x in matchups["games"]]

for matchupId in matchupIds:    
    gamePath = filePath.format(league, *str(gameDate).split("-"),"M"+str(matchupId))
    with open(gamePath) as jsonFile:
        game = load(jsonFile)
        #pprint(game)
  
        for i,teamId in enumerate(game["team_ids"]):
            oppId = game["team_ids"][i-1]
            isHome = True if teamId == game["home_team"] else False
            injuries = [injury for injury in game["injuries"] if injury["team"] == teamId]
            newTeam = Team(teamId, oppId, isHome, injuries)
            teams[teamId] = newTeam


data = {}
for team in teams.values():
    for player in chain(team.starters, team.bench):
        playerStats = {"season":{}, "month":{}}
        for view in ("season", "month"):
            playerStats[view] = {"score": player.score[view]}
            for stat in ("min", "fga","fgm","fta","ftm","tpa","tpm","oreb","dreb","ast","stl","blk","turn","points"):
                playerStats[view][stat] = player.stats[stat][view]
        data[player.getId()] = playerStats

with open(filePath.format(league, *str(gameDate).split("-"), "similarProj"), "w") as fileOut:
    dump(data, fileOut)



            

