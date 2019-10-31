import wx
from pprint import pprint
from os import environ
from json import load, dump
from SportsDB.WebService.ESPN.TeamParser import getRoster
from SportsDB.DB.NBA import gameDateCmd
from datetime import date, timedelta
import sqlite3

###########################################

mainPath = environ["HOME"] +"/FEFelson/NBA/BoxScores/{}/{}/{}/"
scorePath = mainPath + "scoreboard.json"
lineupPath = mainPath + "lineups.json"
seasonDBPath = environ["HOME"] +"/FEFelson/NBA/season.db"
conn = sqlite3.connect(seasonDBPath)
curs = conn.cursor()


gameDate = date.today()
yesterday = gameDate - timedelta(1)
twoWeeks = gameDate - timedelta(14)
lastWeek = gameDate - timedelta(7)
lastMonth = gameDate - timedelta(30)
seasonCmd = gameDateCmd(seasons=("2019",))
monthCmd = gameDateCmd(gameDates=(lastMonth,gameDate))
twoWeeksCmd = gameDateCmd(gameDates=(twoWeeks,gameDate))
lastWeekCmd = gameDateCmd(gameDates=(lastWeek,gameDate))

############################################



########  SQL Commands ##############################################

gamesPlayedCmd = "SELECT stats.game_id FROM {0[item]}_stats AS stats INNER JOIN ({0[gdCmd]}) AS gd ON stats.game_id = gd.game_id WHERE {0[item]}_id = ?"
playerNameCmd = "SELECT first_name, last_name FROM pro_players WHERE player_id = ?"
startPctCmd = "SELECT COUNT(stats.game_id), SUM(starter)*1.0 / COUNT(stats.game_id)*1.0, SUM(stats.mins) FROM player_stats AS stats INNER JOIN ({0[gdCmd]}) AS gd ON stats.game_id = gd.game_id WHERE team_id = ? AND player_id = ?"  
dnpCmd = "SELECT COUNT(dnp.game_id) FROM dnp_games AS dnp INNER JOIN ({0[gdCmd]}) AS gd ON dnp.game_id = gd.game_id WHERE team_id = ? AND player_id = ?"  

#####################################################################



def createLineupFile(gameDate):
    matchups = []

    

    
    with open(scorePath.format(*str(gameDate).split("-"))) as scoreIn:
        sb = load(scoreIn)

    for game in sb["games"]:
        info = dict(zip([x["team_id"] for x in game["teams"]], [x for x in game["teams"]])) 
        gameId = game["game_id"]
        matchPath = mainPath+"M{}.json".format(gameId)
        #print(matchPath)
        with open(matchPath.format(*str(gameDate).split("-"))) as matchIn:
            match = load(matchIn)
            #pprint(match)

            index = sorted([x for x in match["injuries"].keys()])[-1]
            injuries = {}
            for teamId in match["team_ids"]:
                injuries[teamId] = [x for x in match["injuries"][index] if x["team"] == teamId]


            homeId = match["home_team"]
            awayId = match["team_ids"][0] if match["team_ids"][0] != match["home_team"] else match["team_ids"][1]

            homeTeam = Team(info[homeId], injuries[homeId])
            awayTeam = Team(info[awayId], injuries[awayId])
            matchups.append({"gameId":gameId, "homeTeam": homeTeam.getJson(), "awayTeam": awayTeam.getJson()})


    with open(lineupPath.format(*str(gameDate).split("-")), "w") as fileOut:
        dump({"matchups":matchups}, fileOut)
    


class Model:

    def __init__(self):

        self.matchups = []
        self.teams = []
        self.setMatchups()
        self.index = 0
        self.team = None
        self.player = None


    def addStarter(self):
        self.team.starters.append(self.player)


    def removeStarter(self):
        self.team.starters.remove(self.player)


    def removeOut(self):
        self.team.out.remove(self.player)


    def addOut(self):
        self.team.out.append(self.player)


    def addBench(self):
        self.team.bench.append(self.player)


    def removeBench(self):
        self.team.bench.remove(self.player)


    def changeBenchOrder(self, oldN, newN, player):
        self.team.bench.pop(oldN)
        self.team.bench.insert(newN, player)


    def nextTeam(self):
        self.team = self.teams[self.index]
        self.index += 1
        

    def writeFile(self):
        x = []
        for match in self.matchups:
            x.append({"gameId":match["gameId"], "homeTeam": match["homeTeam"].getJson(), "awayTeam": match["awayTeam"].getJson()})

            
        with open(lineupPath.format(*str(gameDate).split("-")), "w") as fileOut:
            dump({"matchups":x}, fileOut)


    def setMatchups(self):
        
        with open(scorePath.format(*str(gameDate).split("-"))) as scoreIn:
            sb = load(scoreIn)

        for game in sb["games"]:
            info = dict(zip([x["team_id"] for x in game["teams"]], [x for x in game["teams"]])) 
            gameId = game["game_id"]
            matchPath = mainPath+"M{}.json".format(gameId)
            #print(matchPath)
            with open(matchPath.format(*str(gameDate).split("-"))) as matchIn:
                match = load(matchIn)
                #pprint(match)

                index = sorted([x for x in match["injuries"].keys()])[-1]
                injuries = {}
                for teamId in match["team_ids"]:
                    injuries[teamId] = [x for x in match["injuries"][index] if x["team"] == teamId]


                homeId = match["home_team"]
                awayId = match["team_ids"][0] if match["team_ids"][0] != match["home_team"] else match["team_ids"][1]

                homeTeam = Team(info[homeId], injuries[homeId])
                awayTeam = Team(info[awayId], injuries[awayId])
                self.teams.append(homeTeam)
                self.teams.append(awayTeam)
                self.matchups.append({"gameId":gameId, "homeTeam": homeTeam, "awayTeam": awayTeam})



class Controller:

    def __init__(self):

        self.model = Model()
        self.view = View(None)
        self.model.nextTeam()
        self.view.setTeam(self.model.team)
        self.view.actionBtn.Bind(wx.EVT_BUTTON, self.onActionBtn)
        self.view.aBtn.Bind(wx.EVT_BUTTON, self.onMove)
        self.view.bBtn.Bind(wx.EVT_BUTTON, self.onMove)
        self.view.upBtn.Bind(wx.EVT_BUTTON, self.upMove)
        self.view.downBtn.Bind(wx.EVT_BUTTON, self.downMove)
        self.view.starters.Bind(wx.EVT_LISTBOX_DCLICK, self.selectPlayer)
        self.view.bench.Bind(wx.EVT_LISTBOX_DCLICK, self.selectPlayer)
        self.view.out.Bind(wx.EVT_LISTBOX_DCLICK, self.selectPlayer)
        self.view.Show()


    def selectPlayer(self, event):
        listBox = event.GetEventObject()
        player = listBox.GetClientData(listBox.GetSelection())
        self.view.selection.SetLabel(player.firstName + " " +player.lastName)
        self.model.player = player
        
        if player in self.model.team.starters:
            self.view.aBtn.SetLabel("Bench?")
            self.view.bBtn.SetLabel("Out?")
        elif player in self.model.team.bench:
            self.view.aBtn.SetLabel("Start?")
            self.view.bBtn.SetLabel("Out?")
        else:
            self.view.aBtn.SetLabel("Start?")
            self.view.bBtn.SetLabel("Bench?")

        self.view.aBtn.Enable()
        self.view.bBtn.Enable()


    def onMove(self, event):
        btn = event.GetEventObject()
        label = btn.GetLabel()

        if label == "Start?":
            if self.model.player.status == "Out":
                self.model.player.status = None
                self.model.removeOut()
                self.view.out.Clear()
                for player in self.model.team.out:
                    self.view.out.Append(player.firstName + " " +player.lastName, player)
            
            else:
                self.model.removeBench()
                self.view.bench.Clear()
                for player in self.model.team.bench:
                    self.view.bench.Append(player.firstName + " " +player.lastName, player)
            
                
            self.model.addStarter()
            self.view.starters.Clear()
            for player in self.model.team.starters:
                self.view.starters.Append(player.firstName + " " +player.lastName, player)

                

        if label == "Bench?":
            self.model.addBench()
            if self.model.player.status == "Out":
                self.model.player.status = None
                self.model.removeOut()
                self.view.out.Clear()
                for player in self.model.team.out:
                    self.view.out.Append(player.firstName + " " +player.lastName, player)
            elif self.model.player in self.model.team.starters:
                self.model.removeStarter()
                self.view.starters.Clear()
                for player in self.model.team.starters:
                    self.view.starters.Append(player.firstName + " " +player.lastName, player)

            self.view.bench.Clear()
            for player in self.model.team.bench:
                self.view.bench.Append(player.firstName + " " +player.lastName, player)


        if label == "Out?":
            self.model.player.status ="Out"
            self.model.addOut()
            if self.model.player in self.model.team.starters:
                self.model.removeStarter()
                self.view.starters.Clear()
                for player in self.model.team.starters:
                    self.view.starters.Append(player.firstName + " " +player.lastName, player)

            if self.model.player in self.model.team.bench:
                self.model.removeBench()
                self.view.bench.Clear()
                for player in self.model.team.bench:
                    self.view.bench.Append(player.firstName + " " +player.lastName, player)
            self.view.out.Clear()
            for player in self.model.team.out:
                self.view.out.Append(player.firstName + " " +player.lastName, player)
            

        self.model.player = None
        self.view.selection.SetLabel("No Selection")
        self.view.aBtn.Disable()
        self.view.bBtn.Disable()

        if len(self.model.team.starters) !=5:
            self.view.actionBtn.Disable()
        else:
            self.view.actionBtn.Enable()

        self.view.Layout()
            

    def onActionBtn(self, event):
        self.view.starters.Clear()
        self.view.bench.Clear()
        self.view.out.Clear()
        if self.model.index == len(self.model.teams):
            self.model.writeFile()
            self.view.Close()
        else:
            self.model.nextTeam()
            self.view.setTeam(self.model.team)
        self.model.player = None
        self.view.aBtn.Disable()
        self.view.bBtn.Disable()
        self.view.selection.SetLabel("")
        self.view.Layout()


    def upMove(self, event):
        n = self.view.bench.GetSelection()
        if  n > 0:
            player = self.view.bench.DetachClientObject(n)
            self.view.bench.Delete(n)
            self.view.bench.Insert(player.firstName + " " +player.lastName, n-1, player)
            self.view.bench.SetSelection(n-1)
            self.model.changeBenchOrder(n, n-1, player)
            self.view.Layout()


    def downMove(self, event):
        n = self.view.bench.GetSelection()
        if  n > -1 and n+1 < len(self.view.bench.GetItems()):
            player = self.view.bench.DetachClientObject(n)
            self.view.bench.Delete(n)
            self.view.bench.Insert(player.firstName + " " +player.lastName, n+1, player)
            self.view.bench.SetSelection(n+1)
            self.model.changeBenchOrder(n, n+1, player)
            self.view.Layout()


class Team:

    def __init__(self, info, injuries):

        self.teamId = info["team_id"]
        self.abrv = info["abrv"]
        self.name = info["name"]
        self.colors = [info[x] for x in ("color","alt_color")]
        self.injuries = dict(zip([x["player_id"] for x in injuries], [x["status"] for x in injuries]))

        self.roster = self.setRoster()
        self.starters = None
        self.bench = None
        self.out = None
        
        self.setStarters()
        self.setBench()


    def getJson(self):
        return {"teamId": self.teamId, "abrv": self.abrv, "name": self.name, "starters": [s.getJson() for s in self.starters], "bench": [s.getJson() for s in self.bench]}

       

    def setRoster(self):
        roster = []
        for playerId in getRoster(self.abrv, "nba"):
            try:
                firstName, lastName = curs.execute(playerNameCmd, (playerId,)).fetchone()
                roster.append(Player(self, playerId, firstName, lastName, self.injuries.get(playerId, None)))
            except TypeError:
                pass
                
        return roster


    def setStarters(self):
        #TODO: IN Future use position to set uncommon starter
        starters = []
        for player in self.roster:
            if player.getStartPct("season") == 1 and player.getStatus() not in ("Out", "Fringe"):
                starters.append(player)

        if len(starters) < 5:
            for player in sorted(self.roster, key=lambda x: (x.getStartPct("twoWeeks"), x.getGP("twoWeeks"), x.getMins("twoWeeks")), reverse=True ):
                if player not in starters and player.getStatus() not in ("Out", "Fringe"):
                    starters.append(player)
                    if len(starters) == 5:
                        break
        self.starters = starters


    def setBench(self):
        bench = []
        fringe = []
        out = []
        for player in [x for x in sorted(self.roster, key=lambda x: (x.getGP("twoWeeks")-x.getDnp("twoWeeks"), x.getMins("twoWeeks")), reverse=True ) if x not in self.starters]:
            if player.getStatus() == "Out":
                out.append(player)
            elif player.getStatus() == "Fringe":
                fringe.append(player)
            else:
                bench.append(player)

        self.out = out
        self.bench = bench + fringe
            

class Player:

    def __init__(self, team, playerId, firstName, lastName, status):

        self.playerId = playerId
        self.firstName = firstName
        self.lastName = lastName
        self.status = status
        self.team = team

        self.gameInfo = self.setGameInfo()
        if self.gameInfo["twoWeeks"][0] == 0:
            self.status = "Out"
        elif self.gameInfo["week"][0] == 0:
            self.status = "Fringe"


    def getJson(self):
        return {"playerId": self.playerId, "firstName": self.firstName, "lastName": self.lastName, "status": self.status}


    def getStartPct(self, item):
        return self.gameInfo[item][1]


    def getMins(self, item):
        return self.gameInfo[item][-1]


    def getGP(self, item):
        return self.gameInfo[item][0]


    def getDnp(self, item):
        return self.gameInfo[item][2]


    def __str__(self):
        line = "{:<16} {:<16}"
        if self.status:
            line += "   {}"
        return line.format(self.firstName, self.lastName, self.status)


    def getStatus(self):
        return self.status


    def setGameInfo(self):
        gameInfo = {}

        for timeFrame, gdCmd in (("season", seasonCmd),
                                 ("month", monthCmd),
                                 ("twoWeeks", twoWeeksCmd),
                                 ("week", lastWeekCmd)):
            gp, stPct, mins = curs.execute(startPctCmd.format({"gdCmd":gdCmd}), (self.team.teamId, self.playerId)).fetchone()
            dnp = curs.execute(dnpCmd.format({"gdCmd":gdCmd}), (self.team.teamId, self.playerId)).fetchone()[0]
            stPct = 0 if not stPct else stPct
            mins = 0 if not mins else mins

            gameInfo[timeFrame] = (gp,stPct,dnp,mins)
        #pprint(startPct)
        return gameInfo
                                 











class View(wx.Frame):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.panel = wx.Panel(self)
        
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.listSizer = wx.BoxSizer()
        
        ##########
 
        self.starters = wx.ListBox(self.panel)
        self.listSizer.Add(self.starters, 1, wx.EXPAND)
                
        ##########
        
        self.bench = wx.ListBox(self.panel)
        self.listSizer.Add(self.bench, 1, wx.EXPAND)
        self.moveSizer = wx.BoxSizer(wx.VERTICAL)
        self.upBtn = wx.Button(self.panel, label="up")
        self.downBtn = wx.Button(self.panel, label="dwn")
        self.moveSizer.Add(self.upBtn)
        self.moveSizer.Add(self.downBtn)
        self.listSizer.Add(self.moveSizer, 0, wx.EXPAND)
        
        ##########
 
        self.out = wx.ListBox(self.panel)
        self.listSizer.Add(self.out, 1, wx.EXPAND)
        
         
        ##########

        self.selection = wx.StaticText(self.panel, label="No Selection")
        self.btnSizer = wx.BoxSizer()
        self.aBtn = wx.Button(self.panel, label="")
        self.aBtn.Disable()
        self.bBtn = wx.Button(self.panel, label="")
        self.bBtn.Disable()
        self.btnSizer.Add(self.aBtn, 0)
        self.btnSizer.Add(self.bBtn, 0)

        self.actionBtn = wx.Button(self.panel, label="Next")
       
        self.mainSizer.Add(self.listSizer, 1, wx.EXPAND)
        self.mainSizer.Add(wx.StaticText(self.panel, label="Selected Player"),0, wx.EXPAND)
        self.mainSizer.Add(self.selection, 0, wx.EXPAND)
        self.mainSizer.Add(self.btnSizer, 0, wx.EXPAND)
        self.mainSizer.Add(self.actionBtn, 0, wx.EXPAND)

        self.panel.SetSizer(self.mainSizer)

        


    def setTeam(self, team):
        self.team = team
        for player in self.team.starters:
            self.starters.Append(player.firstName + " " +player.lastName, player)

        for player in self.team.bench:
            self.bench.Append(player.firstName + " " +player.lastName, player)

        for player in self.team.out:
            self.out.Append(player.firstName + " " +player.lastName, player)
        self.Layout()

        

    




if __name__ == "__main__":
        
    app = wx.App()
    c = Controller()
    app.MainLoop()


    conn.close()
