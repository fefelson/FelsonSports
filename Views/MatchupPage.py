import os
import wx
from pprint import pprint

# from ..Views.StatsPanel.PlayersPanel import NCAABPlayerStatsPanel, NBAPlayerStatsPanel
from ..Views.TeamPanels.StatsPanel import NCAABStatsPanel, NBAStatsPanel, MLBStatsPanel
from ..Views.GamePanels.GameLinePanel import GameLinePanel
from .GamePanels.TitlePanel import TitlePanel
# from ..Views.GamePanels.PredictPanel import PredictPanel

timeframeList = ["2weeks", "1month", "6weeks", "season"]


logoPath = os.environ["HOME"] + "/Yahoo/{}/logos/{}.png"






class MatchupPage(wx.Panel):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)


        self.titlePanel = TitlePanel(self)

        self.timeBox = wx.ComboBox(self, choices=["2weeks", "1month", "6weeks", "season"])
        self.timeBox.SetSelection(0)
        self.timeBox.Bind(wx.EVT_COMBOBOX, self.onChange)

        self.mainPanel = wx.Notebook(self)

        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainPanel.SetSizer(self.mainSizer)

        self.gameLinePanel = GameLinePanel(self.mainPanel)
        # self.predictPanel = PredictPanel(self.mainPanel)
        # self.predictPanel.setPanel({"regs": self.info["regs"], "teamStats": self.info["teamStats"]})
        self.teamStatsPanel = self.getStatsPanel(self.mainPanel)
        # self.playerStatsPanel = self.getPlayerPanel(self.mainPanel)

        self.mainPanel.AddPage(self.gameLinePanel, "gL")
        self.mainPanel.AddPage(self.teamStatsPanel, "teamS")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.titlePanel, 0, wx.EXPAND)
        sizer.Add(self.timeBox, 0, wx.CENTER)
        sizer.Add(self.mainPanel, 1, wx.EXPAND)

        self.SetSizer(sizer)


    def setPanel(self, info):
        self.info = info
        tF = self.timeBox.GetStringSelection()
        self.titlePanel.setPanel({"odds": info["odds"][-1]["99"], "details": info["teamDetails"], "records": info["teamRecords"][tF]})
        self.gameLinePanel.setPanel({"games": self.info["gameLines"][tF], "homeId": self.info["homeId"], "awayId": self.info["awayId"], "commonOpp": self.info["commonOpp"][tF]})
        self.teamStatsPanel.setPanel(self.info["teamStats"][tF])

        self.Layout()


    def onChange(self, event):
        self.setPanel(self.info)



    def getStatsPanel(self, parent):
        raise AssertionError


    def getPlayerPanel(self, parent):
        raise AssertionError




class MLBMatchupPage(MatchupPage):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)


    def getStatsPanel(self, parent):
        return MLBStatsPanel(parent)



class NBAMatchupPage(MatchupPage):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)


    def getStatsPanel(self, parent):
        return NBAStatsPanel(parent)
