import wx

from itertools import chain
from FelsonSports.Views.TeamGroupPanels import TeamStatsPanel as TSP

class TeamStatsControl:

    def __init__(self, parentView):

        self.panel = TSP.StatSwapPanel(parentView)
        self.panel.typeBox.Bind(wx.EVT_COMBOBOX, self.onBox)

        for bttn in chain(self.panel.statsPanel.bttns, self.panel.resultsPanel.bttns):
            bttn.Bind(wx.EVT_BUTTON, self.onBttn)

        self.teams = []
        self.statLabel = "pts"
        self.typeLabel = "team"


    def onBox(self, evt):
        self.typeLabel = self.panel.typeBox.GetStringSelection()
        if self.typeLabel == "results":
            self.statLabel = "wins"
            self.panel.resultsPanel.Show()
            self.panel.statsPanel.Hide()
        else:
            self.statLabel = "pts"
            self.panel.resultsPanel.Hide()
            self.panel.statsPanel.Show()
        self.update()


    def getPanel(self):
        return self.panel


    def setTeams(self, teams):
        self.teams = teams
        for panel in (self.panel.statsPanel, self.panel.resultsPanel):
            panel.addPanels(len(self.teams))
        self.update()


    def onBttn(self, evt):
        bttn = evt.GetEventObject()
        self.statLabel = bttn.GetLabel()
        self.update()


    def update(self):
        itemGroup = "all_{}".format(self.typeLabel)
        teams = sorted(self.teams, key=lambda x: x.getStats(itemGroup, self.statLabel), reverse=True)
        self.panel.setPanels(itemGroup, teams)
        self.panel.Layout()
