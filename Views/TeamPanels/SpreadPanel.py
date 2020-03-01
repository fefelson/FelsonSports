import datetime
import wx
import os

from pprint import pprint

logoPath = os.environ["HOME"] + "/Yahoo/{}/teams/{}.png"


class GamePanel(wx.Panel):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.date = wx.StaticText(self)
        self.team = wx.StaticBitmap(self)
        self.vs = wx.StaticText(self)
        self.logo = wx.StaticBitmap(self)
        self.spread = wx.StaticText(self)
        self.result = wx.StaticText(self)
        self.ou = wx.StaticText(self)
        self.total = wx.StaticText(self)
        self.money = wx.StaticText(self)

        sizer = wx.BoxSizer()
        sizer.Add(self.date, 1)
        sizer.Add(self.team, 1)
        sizer.Add(self.vs, 1)
        sizer.Add(self.logo, 1)
        sizer.Add(self.spread, 1)
        sizer.Add(self.result, 1)
        sizer.Add(self.ou, 1)
        sizer.Add(self.total, 1)
        sizer.Add(self.money, 1)

        self.SetSizer(sizer)


    def setPanel(self, gameInfo):

        self.date.SetLabel(str(gameInfo[0]))
        team = wx.Image(logoPath.format("nba", gameInfo[1]), wx.BITMAP_TYPE_PNG).Scale(30, 30, wx.IMAGE_QUALITY_HIGH)
        team = team.ConvertToBitmap()

        self.team.SetBitmap(team)

        self.vs.SetLabel("VS" if gameInfo[2] else "AT")

        try:
            logo = wx.Image(logoPath.format("nba", gameInfo[3]), wx.BITMAP_TYPE_PNG).Scale(30, 30, wx.IMAGE_QUALITY_HIGH)
            logo = logo.ConvertToBitmap()
            self.logo.SetBitmap(logo)
        except:
            pass

        self.spread.SetLabel("+"+str(gameInfo[4]) if gameInfo[4] > 0 else str(gameInfo[4]) )
        self.result.SetLabel(str(gameInfo[5]))
        self.ou.SetLabel(str(gameInfo[6]))
        self.total.SetLabel(str(gameInfo[7]))
        try:
            self.money.SetLabel("+"+str(gameInfo[8]) if gameInfo[8] > 0 else str(gameInfo[8]) )
        except:
            self.money.SetLabel("0")

        if gameInfo[5] > 0:
            self.money.SetForegroundColour(wx.GREEN)
        else:
            self.money.SetForegroundColour(wx.RED)

        if gameInfo[2]:
            self.SetBackgroundColour(wx.WHITE)
        else:
            self.SetBackgroundColour(wx.Colour("KHAKI"))

        if gameInfo[4] + gameInfo[5] > 0:
            self.spread.SetForegroundColour(wx.GREEN)
        elif gameInfo[4] + gameInfo[5] < 0:
            self.spread.SetForegroundColour(wx.RED)

        if gameInfo[7] > gameInfo[6]:
            self.ou.SetForegroundColour(wx.GREEN)
        elif gameInfo[7] < gameInfo[6]:
            self.ou.SetForegroundColour(wx.BLUE)



class SpreadPanel(wx.ScrolledWindow):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.SetScrollbars(20,20,50,50)

        self.game = None

        self.gameTime = wx.StaticText(self)
        self.spread = wx.StaticText(self)
        self.ou = wx.StaticText(self)

        self.timeFrame = wx.ComboBox(self, choices=("season", "sixWeeks", "twoWeeks"))
        self.timeFrame.Bind(wx.EVT_COMBOBOX, self.onTF)
        self.timeFrame.SetSelection(0)


        self.options = wx.ComboBox(self, choices=("spread", "ou", "money"))
        self.options.Bind(wx.EVT_COMBOBOX, self.onOpt)
        self.options.SetSelection(0)


        self.logos = {}
        self.firstNames = {}
        self.records = {}
        self.ats = {}
        self.gameLogSizers = {}

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(self.gameTime, 0, wx.CENTER | wx.TOP, 7)
        mainSizer.Add(self.spread, 0, wx.CENTER | wx.TOP, 5)
        mainSizer.Add(self.ou, 0, wx.CENTER | wx.TOP | wx.BOTTOM, 5)

        vsSizer = wx.BoxSizer()
        bodySizer = wx.BoxSizer()


        for hA in ("away", "home"):
            teamSizer = wx.BoxSizer(wx.VERTICAL)
            nameSizer = wx.BoxSizer()
            recordSizer = wx.BoxSizer()

            logo = wx.StaticBitmap(self)
            self.logos[hA] = logo

            firstNames = wx.StaticText(self)
            self.firstNames[hA] = firstNames

            nameSizer.Add(logo, 0, wx.EXPAND)
            nameSizer.Add(firstNames, 0, wx.EXPAND)

            record = wx.StaticText(self)
            self.records[hA] = record

            ats = wx.StaticText(self)
            self.ats[hA] = ats

            recordSizer.Add(record, 0, wx.EXPAND)
            recordSizer.Add(ats, 0, wx.EXPAND)

            teamSizer.Add(nameSizer, 0, wx.EXPAND)
            teamSizer.Add(recordSizer, 0, wx.EXPAND)

            vsSizer.Add(teamSizer, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

            gameLogSizer = wx.BoxSizer(wx.VERTICAL)
            self.gameLogSizers[hA] = gameLogSizer

            bodySizer.Add(gameLogSizer, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)

        mainSizer.Add(vsSizer, 0, wx.EXPAND)
        mainSizer.Add(bodySizer, 1, wx.EXPAND)
        self.SetSizer(mainSizer)


    def onTF(self, evt):
        self.game.model.setTimeFrame(self.timeFrame.GetStringSelection())
        for hA in ("away", "home"):
            team = self.game.getTeam(hA)

            wins = team.getStats("all_results", "wins")
            loses = team.getStats("all_results", "loses")
            atsWins = team.getStats("all_results", "atsWins")
            atsLoses = team.getStats("all_results", "atsLoses")

            self.records[hA].SetLabel("( {} - {} )".format(wins,loses))
            self.ats[hA].SetLabel("( {} - {} )".format(atsWins,atsLoses))
        self.Layout()


    def onOpt(self, evt):
        select = self.options.GetStringSelection()
        for hA in ("away", "home"):
            for item in self.gameLogSizers[hA].GetChildren():
                panel = item.GetWindow()
                print(panel)
                panel.spread.Hide()
                panel.result.Hide()
                panel.ou.Hide()
                panel.total.Hide()
                panel.money.Hide()

                if select == "spread":
                    panel.spread.Show()
                    panel.result.Show()
                elif select == "ou":
                    panel.ou.Show()
                    panel.total.Show()
                else:
                    panel.result.Show()
                    panel.money.Show()
                panel.Layout()
        self.Layout()





    def setPanel(self, game):

        self.game = game

        timeFrame = self.timeFrame.GetStringSelection()
        gd = datetime.datetime.strptime(game.getInfo("gameTime"), "%a, %d %b %Y %H:%M:%S %z") - datetime.timedelta(hours=5)
        self.gameTime.SetLabel(gd.strftime("%I:%M %p"))

        try:
            sp = "+"+str(game.getOdds("home_spread")) if float(game.getOdds("home_spread")) > 0 else str(game.getOdds("home_spread"))
        except (ValueError, KeyError):
            sp = -100
        self.spread.SetLabel("{}  {}".format(game.getTeam("home").getInfo("abrv"), sp))

        try:
            self.ou.SetLabel("{:.1f}".format(game.getOdds("ou")))
        except KeyError:
            self.ou.SetLabel("0")

        for hA in ("away", "home"):
            team = game.getTeam(hA)

            self.firstNames[hA].SetLabel(team.getInfo("firstName"))

            logo = wx.Image(logoPath.format(game.getInfo("league"), team.getId()), wx.BITMAP_TYPE_PNG).Scale(40, 40, wx.IMAGE_QUALITY_HIGH)
            logo = logo.ConvertToBitmap()
            self.logos[hA].SetBitmap(logo)

            wins = team.getStats("all_results", "wins")
            loses = team.getStats("all_results", "loses")
            atsWins = team.getStats("all_results", "atsWins")
            atsLoses = team.getStats("all_results", "atsLoses")

            self.records[hA].SetLabel("( {} - {} )".format(wins,loses))
            self.ats[hA].SetLabel("( {} - {} )".format(atsWins,atsLoses))

            for gameInfo in team.getSpreadGames():
                pprint(gameInfo)
                gp = GamePanel(self)
                self.gameLogSizers[hA].Add(gp, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 10)
                gp.setPanel(gameInfo)
                gp.ou.Hide()
                gp.total.Hide()
                gp.money.Hide()


class SpreadFrame(wx.Frame):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, size=(1000,700), *args, **kwargs)

        self.panel = SpreadPanel(self)
        self.Show()

    def setPanel(self, game):
        self.panel.setPanel(game)
