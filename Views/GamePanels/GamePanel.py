import wx

from . import (TitlePanel as TP, TeamStatsPanel as TS, PrevGamesPanel as PGP,
                PlayerStatsPanel as PSP)

class GamePanel(wx.ScrolledWindow):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.SetScrollbars(20, 20, 50, 50)


        self.titlePanel = TP.TitlePanel(self)
        self.teamStatsPanel = TS.TeamStatsPanel(self)
        self.prevPanel = PGP.PrevGamesPanel(self)
        self.playerPanel = PSP.PlayerStatsPanel(self)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.titlePanel, 0, wx.EXPAND)
        self.sizer.Add(self.teamStatsPanel, 0, wx.EXPAND)
        self.sizer.Add(self.prevPanel, 0, wx.EXPAND)
        self.sizer.Add(self.playerPanel, 1, wx.EXPAND)

        self.SetSizer(self.sizer)


    def setPanel(self, game):
        self.titlePanel.setPanel(game)
        self.teamStatsPanel.setPanel(game)
        self.prevPanel.setPanel(game)
        self.playerPanel.setPanel(game)
        self.Layout()
