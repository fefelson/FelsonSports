import os
import wx


logoPath = os.environ["HOME"] + "/Yahoo/{}/teams/{}.png"


class StatSwapPanel(wx.Panel):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.typeBox = wx.ComboBox(self, choices=("team", "opp", "results"))
        self.typeBox.SetSelection(0)

        self.statsPanel = TeamStatsPanel(self)
        self.resultsPanel = TeamResultsPanel(self)


        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(self.typeBox, 0, wx.CENTER)
        sizer.Add(self.statsPanel, 1, wx.EXPAND)
        sizer.Add(self.resultsPanel, 1, wx.EXPAND)

        self.resultsPanel.Hide()

        self.SetSizer(sizer)


    def setPanels(self, typeLabel, teams):
        for panel in (self.statsPanel, self.resultsPanel):
            for i, team in enumerate(teams):
                panel.teamPanels[i].setPanel(typeLabel, team)
            panel.Layout()
        self.Layout()




class TeamResultsPanel(wx.ScrolledWindow):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.SetScrollbars(20,20,50,50)

        self.bttns = []
        self.teamPanels = []
        bttnSizer = wx.BoxSizer()
        bttnSizer.Add(199,30)
        for label in ("wins", "loses", "atsWins", "atsLoses", "result", "spread", "money", "total"):
            bttn = wx.Button(self, label=label)
            bttnSizer.Add(bttn, 0, wx.EXPAND)
            self.bttns.append(bttn)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(bttnSizer, 0, wx.EXPAND)


        self.SetSizer(self.sizer)


    def addPanels(self, n):

        for i in range(1,n+1):
            tp = TeamResultPanel(self, i)
            self.sizer.Add(tp, 1, wx.EXPAND)
            self.teamPanels.append(tp)


class TeamStatsPanel(wx.ScrolledWindow):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.SetScrollbars(20,20,50,50)

        self.bttns = []
        self.teamPanels = []
        bttnSizer = wx.BoxSizer()
        bttnSizer.Add(199,30)
        for label in ("pts", "reb", "ast", "stl", "blk", "fls"):
            bttn = wx.Button(self, label=label)
            bttnSizer.Add(bttn, 0, wx.EXPAND)
            self.bttns.append(bttn)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(bttnSizer, 0, wx.EXPAND)


        self.SetSizer(self.sizer)


    def addPanels(self, n):

        for i in range(1,n+1):
            tp = TeamStatPanel(self, i)
            self.sizer.Add(tp, 1, wx.EXPAND)
            self.teamPanels.append(tp)


class TeamStatPanel(wx.Panel):

    def __init__(self, parent, i, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        i = wx.StaticText(self, label=str(i))
        self.logo = wx.StaticBitmap(self)
        self.name = wx.StaticText(self)
        self.name.SetMinSize((169,-1))

        self.ppg = wx.StaticText(self)
        self.ppg.SetMinSize((70,-1))

        self.rpg = wx.StaticText(self)
        self.rpg.SetMinSize((70,-1))

        self.apg = wx.StaticText(self)
        self.apg.SetMinSize((70,-1))

        self.spg = wx.StaticText(self)
        self.spg.SetMinSize((70,-1))

        self.bpg = wx.StaticText(self)
        self.bpg.SetMinSize((70,-1))

        self.fls = wx.StaticText(self)
        self.fls.SetMinSize((70,-1))

        nameSizer = wx.BoxSizer()
        nameSizer.Add(i)
        nameSizer.Add(self.logo)
        nameSizer.Add(self.name)

        mainSizer = wx.BoxSizer()
        mainSizer.Add(nameSizer, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        mainSizer.Add(self.ppg, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        mainSizer.Add(self.rpg, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        mainSizer.Add(self.apg, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        mainSizer.Add(self.spg, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        mainSizer.Add(self.bpg, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        mainSizer.Add(self.fls, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)

        self.SetSizer(mainSizer)

    def setPanel(self, typeLabel, team):
        if "results" not in typeLabel:
            logo = wx.Image(logoPath.format(team.getInfo("league"), team.getId()), wx.BITMAP_TYPE_PNG).Scale(30, 30, wx.IMAGE_QUALITY_HIGH)
            logo = logo.ConvertToBitmap()

            self.logo.SetBitmap(logo)
            self.name.SetLabel(str(team))

            self.ppg.SetLabel("{:.1f}".format(team.getStats(typeLabel, "pts")))
            self.rpg.SetLabel("{:.1f}".format(team.getStats(typeLabel, "reb")))
            self.apg.SetLabel("{:.1f}".format(team.getStats(typeLabel, "ast")))
            self.spg.SetLabel("{:.1f}".format(team.getStats(typeLabel, "stl")))
            self.bpg.SetLabel("{:.1f}".format(team.getStats(typeLabel, "blk")))
            self.fls.SetLabel("{:.1f}".format(team.getStats(typeLabel, "fls")))

            self.Layout()


class TeamResultPanel(wx.Panel):

    def __init__(self, parent, i, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        i = wx.StaticText(self, label=str(i))
        self.logo = wx.StaticBitmap(self)
        self.name = wx.StaticText(self)
        self.name.SetMinSize((169,-1))

        self.wins = wx.StaticText(self)
        self.wins.SetMinSize((70,-1))

        self.loses = wx.StaticText(self)
        self.loses.SetMinSize((70,-1))

        self.atsWins = wx.StaticText(self)
        self.atsWins.SetMinSize((70,-1))

        self.atsLoses = wx.StaticText(self)
        self.atsLoses.SetMinSize((70,-1))

        self.total = wx.StaticText(self)
        self.total.SetMinSize((70,-1))

        self.spread = wx.StaticText(self)
        self.spread.SetMinSize((70,-1))

        self.money = wx.StaticText(self)
        self.money.SetMinSize((70,-1))

        self.result = wx.StaticText(self)
        self.result.SetMinSize((70,-1))

        nameSizer = wx.BoxSizer()
        nameSizer.Add(i)
        nameSizer.Add(self.logo)
        nameSizer.Add(self.name)

        mainSizer = wx.BoxSizer()
        mainSizer.Add(nameSizer, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        mainSizer.Add(self.wins, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        mainSizer.Add(self.loses, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        mainSizer.Add(self.atsWins, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        mainSizer.Add(self.atsLoses, 0,wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        mainSizer.Add(self.result, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        mainSizer.Add(self.spread, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        mainSizer.Add(self.money, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        mainSizer.Add(self.total, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)

        self.SetSizer(mainSizer)

    def setPanel(self, typeLabel, team):
        if "results" in typeLabel:
            logo = wx.Image(logoPath.format(team.getInfo("league"), team.getId()), wx.BITMAP_TYPE_PNG).Scale(30, 30, wx.IMAGE_QUALITY_HIGH)
            logo = logo.ConvertToBitmap()

            self.logo.SetBitmap(logo)
            self.name.SetLabel(str(team))

            self.wins.SetLabel(str(team.getStats(typeLabel, "wins")))
            self.loses.SetLabel(str(team.getStats(typeLabel, "loses")))
            self.atsWins.SetLabel(str(team.getStats(typeLabel, "atsWins")))
            self.atsLoses.SetLabel(str(team.getStats(typeLabel, "atsLoses")))
            self.result.SetLabel("{:.1f}".format(team.getStats(typeLabel, "result")))
            self.total.SetLabel("{:.1f}".format(team.getStats(typeLabel, "total")))
            self.spread.SetLabel("{:.1f}".format(team.getStats(typeLabel, "spread")))
            self.money.SetLabel("{:.1f}".format(team.getStats(typeLabel, "money")))

            self.Layout()
