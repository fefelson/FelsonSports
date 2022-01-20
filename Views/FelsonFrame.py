import datetime
import wx

from .GamingPanel import GamingPanel
from .GameLinePanel import GameLinePanel
from .GameLogPanel import GameLogPanel
from .InjuryPanel import InjuryPanel
from .PlayerStatsPanel import BballPlayerStatsPanel, FballPlayerStatsPanel
from .TeamStatsPanel import NCAAFTeamStatsPanel, NBATeamStatsPanel
from .ThumbPanel import ListPanel
from .TitlePanel import TitlePanel
from .. import Environ as ENV

from pprint import pprint



class FelsonFrame(wx.Frame):

    _nbPanels = None
    _listPanel = None
    _tFChoices = None
    _titlePanel = None

    def __init__(self, model, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.model = model

        self.SetSize((1000,700))

        self.panels = {}
        self.mainPanel = wx.Panel(self)
        self.titlePanel = self._titlePanel(self.mainPanel)
        self.noteBook = wx.Notebook(self.mainPanel)
        self.options = {}

        for label, panel in self._nbPanels:
            newPanel = panel(self.noteBook)
            self.panels[label] = newPanel
            self.noteBook.AddPage(newPanel, label)

        self.options["tF"] = wx.ComboBox(self.mainPanel, size=((150,35)), choices=self._tFChoices, name="tF")

        self.options["hA"] = wx.RadioBox(self.mainPanel, choices=("all", "Away/Home"), name="hA")

        self.options["wL"] = wx.RadioBox(self.mainPanel, choices=("all", "winner", "loser"), name="wL")

        self.options["tO"] = wx.RadioBox(self.mainPanel, choices=("team", "opp"), name="tO")

        self.options["comm"] = wx.CheckBox(self.mainPanel, label="Common opp", name="comm")
        self.options["vs"] = wx.CheckBox(self.mainPanel, label="vs opp", name="vs")

        self.listPanel = self._listPanel(self.mainPanel)


        mainSizer = wx.BoxSizer()
        leftSizer = wx.BoxSizer(wx.VERTICAL)
        leftSizer.Add(self.options["tF"], 0, wx.ALL, 5)
        leftSizer.Add(self.options["hA"],0, wx.ALL, 5)
        leftSizer.Add(self.options["wL"],0, wx.ALL, 5)
        leftSizer.Add(self.options["tO"],0, wx.ALL, 5)
        checkSizer = wx.BoxSizer()
        checkSizer.Add(self.options["comm"], 0, wx.ALL, 10)
        checkSizer.Add(self.options["vs"], 0, wx.ALL, 10)
        leftSizer.Add(checkSizer, 0, wx.ALL, 5)
        leftSizer.Add(self.listPanel, 1, wx.EXPAND | wx.TOP, 20)


        rightSizer = wx.BoxSizer(wx.VERTICAL)
        rightSizer.Add(self.titlePanel, 0, wx.EXPAND | wx.ALL, 5)
        rightSizer.Add(self.noteBook, 1, wx.EXPAND)

        mainSizer.Add(leftSizer, 0)
        mainSizer.Add(rightSizer, 1, wx.EXPAND)
        self.mainPanel.SetSizer(mainSizer)




class NCAAFFrame(FelsonFrame):

    _listPanel = ListPanel
    _nbPanels = (("Team Stats", NCAAFTeamStatsPanel), ("Player Stats", FballPlayerStatsPanel), ("Gaming", GamingPanel), ("Game Log", GameLogPanel),
                    ("GameLine", GameLinePanel))
    _titlePanel = TitlePanel
    _tFChoices = ENV.tFFootballChoices

    def __init__(self, model):
        super().__init__(model)



class NFLFrame(FelsonFrame):

    _listPanel = ListPanel
    _nbPanels = (("Team Stats", NCAAFTeamStatsPanel), ("Player Stats", FballPlayerStatsPanel), ("Gaming", GamingPanel), ("Game Log", GameLogPanel),
                    ("GameLine", GameLinePanel), ("Injuries", InjuryPanel))
    _titlePanel = TitlePanel
    _tFChoices = ENV.tFFootballChoices

    def __init__(self, model):
        super().__init__(model)


class NBAFrame(FelsonFrame):

    _listPanel = ListPanel
    _nbPanels = (("Team Stats", NBATeamStatsPanel), ("Player Stats", BballPlayerStatsPanel), ("Gaming", GamingPanel), ("Game Log", GameLogPanel),
                    ("GameLine", GameLinePanel), ("Injuries", InjuryPanel))
    _titlePanel = TitlePanel
    _tFChoices = ENV.tFBasketballChoices

    def __init__(self, model):
        super().__init__(model)


class NCAABFrame(FelsonFrame):

    _listPanel = ListPanel
    _nbPanels = (("Team Stats", NBATeamStatsPanel), ("Player Stats", BballPlayerStatsPanel), ("Gaming", GamingPanel), ("Game Log", GameLogPanel),
                    ("GameLine", GameLinePanel), ("Injuries", InjuryPanel))
    _titlePanel = TitlePanel
    _tFChoices = ENV.tFBasketballChoices

    def __init__(self, model):
        super().__init__(model)
