import wx

from FelsonSports.Views.GamePanels import GamePanel as GP
from . import TeamShotsControl as TSC


class GameControl:

    def __init__(self, parentView):

        self.panel = GP.GamePanel(parentView)
        self.game = None

        self.panel.teamStatsPanel.offDefBox.Bind(wx.EVT_COMBOBOX, self.onBox)
        self.panel.teamStatsPanel.statsBox.Bind(wx.EVT_COMBOBOX, self.onBox)

        # self.shotsControl = TSC.TeamShotsControl(self.panel)
        # self.panel.sizer.Add(self.shotsControl.getPanel(), 1, wx.EXPAND)


    def getPanel(self):
        return self.panel


    def setGame(self, game):
        self.game = game
        # self.shotsControl.setGame(game)
        self.update()


    def onBox(self, evt):
        self.update()


    def update(self):
        self.panel.setPanel(self.game)
        # self.shotsControl.update()
