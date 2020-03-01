import wx

from ..GamePanels import ThumbPanel as TP






class PrevGamesPanel(wx.Panel):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.homePanel = GamesPanel(self, "home")
        self.awayPanel = GamesPanel(self, "away")

        sizer = wx.BoxSizer()
        sizer.Add(self.awayPanel, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 7)
        sizer.Add(self.homePanel, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 7)
        self.SetSizer(sizer)


    def setPanel(self, game):
        self.homePanel.setPanel(game)
        self.awayPanel.setPanel(game)
        self.Layout()


class GamesPanel(wx.ScrolledWindow):

    def __init__(self, parent, hA, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.hA = hA
        self.bindCmd = None
        self.SetMaxSize((-1,130))
        self.SetMinSize((-1,130))
        self.SetScrollbars(20, 20, 50, 50)

        self.thumbSizer = wx.BoxSizer()
        self.SetSizer(self.thumbSizer)


    def setPanel(self, game):
        team = game.getTeam(self.hA)
        self.DestroyChildren()
        self.thumbSizer.Clear()

        #add all games panel
        default = TP.ThumbPanel(self)
        default.bind(self.bindCmd)
        self.thumbSizer.Add(default, 1, wx.LEFT, 5)
        for game in team.getGames(10):
            tp = TP.ThumbPanel(self)
            self.thumbSizer.Add(tp, 1, wx.LEFT, 5)
            tp.setPanel(game)
            tp.bind(self.bindCmd)
        self.Layout()


    def setBindCmd(self, cmd):
        self.bindCmd = cmd
