import os
import wx
from pprint import pprint

from ..Views.StatsPanel.PlayersPanel import NCAABPlayerStatsPanel, NBAPlayerStatsPanel
from ..Views.TeamPanels.StatsPanel import NCAABStatsPanel, NBAStatsPanel
from ..Views.GamePanels.GameLinePanel import GameLinePanel
from ..Views.GamePanels.TitlePanel import TitlePanel
from ..Views.GamePanels.PredictPanel import PredictPanel

timeframeList = ["2weeks", "1month", "6weeks", "season"]


logoPath = os.environ["HOME"] + "/Yahoo/{}/logos/{}.png"






class MatchupFrame(wx.Frame):



    def __init__(self, parent, info, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.SetMinSize(wx.Size(1000,700))


        panel = wx.Panel(self)

        self.info = info

        self.timeBox = wx.ComboBox(panel, value=timeframeList[1], choices=timeframeList )
        self.timeBox.SetMinSize(wx.Size(200,-1))
        self.timeBox.Bind(wx.EVT_COMBOBOX, self.onChange)
        self.timeBox.SetSelection(1)



        self.mainPanel = wx.ScrolledWindow(panel)
        self.mainPanel.SetScrollbars(20, 20, 50, 50)

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainPanel.SetSizer(mainSizer)

        self.gameLinePanel = GameLinePanel(self.mainPanel)
        self.titlePanel = TitlePanel(self.mainPanel)
        self.predictPanel = PredictPanel(self.mainPanel)
        self.predictPanel.setPanel({"regs": self.info["regs"], "teamStats": self.info["teamStats"]})
        self.teamStatsPanel = self.getStatsPanel(self.mainPanel)
        self.playerStatsPanel = self.getPlayerPanel(self.mainPanel)

        mainSizer.Add(self.gameLinePanel, 0, wx.EXPAND)
        mainSizer.Add(self.titlePanel, 0, wx.EXPAND)
        mainSizer.Add(self.predictPanel, 0, wx.EXPAND)
        mainSizer.Add(self.teamStatsPanel, 1, wx.EXPAND)
        mainSizer.Add(self.playerStatsPanel, 1, wx.EXPAND)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.timeBox, 0, wx.ALIGN_CENTER)
        sizer.Add(self.mainPanel, 1, wx.EXPAND | wx.ALL, 10)

        panel.SetSizer(sizer)

        self.onChange(wx.EVT_COMBOBOX)


    def getStatsPanel(self, parent):
        raise AssertionError


    def getPlayerPanel(self, parent):
        raise AssertionError



    def onChange(self, event):

        tF = self.timeBox.GetStringSelection()

        self.gameLinePanel.setPanel({"games": self.info["gameLines"][tF], "homeId": self.info["homeId"], "awayId": self.info["awayId"], "commonOpp": self.info["commonOpp"][tF]})
        self.titlePanel.setPanel({"odds": self.info["odds"][-1]["99"], "details": self.info["teamDetails"], "records": self.info["teamRecords"][tF]})
        self.teamStatsPanel.setPanel(self.info["teamStats"][tF])
        self.playerStatsPanel.setPanel({"stats": self.info["playerStats"][tF], "injuries": self.info["injuries"]})
        self.Layout()


##        pprint()










class NBAMatchup(MatchupFrame):

    def __init__(self, parent, info, *args, **kwargs):
        super().__init__(parent, info, *args, **kwargs)

    def getStatsPanel(self, parent):
        return NBAStatsPanel(parent)


    def getPlayerPanel(self, parent):
        return NBAPlayerStatsPanel(parent)


class NFLMatchup(MatchupFrame):

    def __init__(self, parent, info, *args, **kwargs):
        super().__init__(parent, info, *args, **kwargs)

    def getStatsPanel(self, parent):
        raise AssertionError


class NCAABMatchup(MatchupFrame):

    def __init__(self, parent, info, *args, **kwargs):
        super().__init__(parent, info, *args, **kwargs)


    def getStatsPanel(self, parent):
        return NCAABStatsPanel(parent)


    def getPlayerPanel(self, parent):
        return NCAABPlayerStatsPanel(parent)



class NCAAFMatchup(MatchupFrame):

    def __init__(self, parent, info, *args, **kwargs):
        super().__init__(parent, info, *args, **kwargs)

    def getStatsPanel(self, parent):
        raise AssertionError
