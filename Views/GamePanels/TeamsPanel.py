import wx

from . import TeamStatsPanel as TSP, PlayerStatsPanel as PS

class TeamsPanel(wx.Panel):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.awayPanel = TeamPanel(self, "away")
        self.homePanel = TeamPanel(self, "home")

        sizer = wx.BoxSizer()
        sizer.Add(self.awayPanel, 1, wx.EXPAND)
        sizer.Add(self.homePanel, 1, wx.EXPAND)
        self.SetSizer(sizer)


    def setPanel(self, game):

        self.awayPanel.setPanel(game)
        self.homePanel.setPanel(game)



class TeamPanel(wx.ScrolledWindow):

    def __init__(self, parent, hA, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.SetScrollbars(20, 20, 50, 50)

        self.hA = hA
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.panels = []

        ts = TSP.TeamStatsPanel(self, self.hA)
        self.sizer.Add(ts, 1, wx.EXPAND)
        self.panels.append(ts)

        cp = wx.CollapsiblePane(self, label="Players:")
        sizer = wx.BoxSizer()
        pane = cp.GetPane()
        ps = PS.PlayerStatsPanel(pane, self.hA)
        sizer.Add(ps, 1, wx.EXPAND)
        pane.SetSizer(sizer)
        self.panels.append(ps)


        self.sizer.Add(cp, 0, wx.EXPAND)

        self.SetSizer(self.sizer)


    def setPanel(self, game):
        for p in self.panels:
            p.setPanel(game)
        self.Layout()
