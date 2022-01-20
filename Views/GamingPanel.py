import wx

from copy import deepcopy
from itertools import chain


class GamingPanel(wx.ScrolledWindow):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.SetScrollbars(20, 20, 50, 50)

        awayHome = ("away", "home")

        nameFont = wx.Font(wx.FontInfo(12).Bold())
        primeFont = wx.Font(wx.FontInfo(10).Bold())
        statFont = wx.Font(wx.FontInfo(8).Bold())

        self.gameList = ("atsW", "atsL", "atsP", "spread", "spreadLine", "moneyLine", "result", "ats$", "money$")

        self.ovList = ("ou", "total", "overLine", "underLine", "over$", "under$")

        hADict = dict(zip(awayHome, [{} for _ in awayHome]))


        self.teams = deepcopy(hADict)

        for hA in awayHome:

            teamName = wx.StaticText(self)
            teamName.SetFont(nameFont)

            self.teams[hA]["name"] = teamName


            for stat in chain(self.gameList, self.ovList):

                teamItem = wx.StaticText(self)
                if stat in ("atsW", "atsL", "atsP", "ats$", "money$", "under$", "over$"):
                    teamItem.SetFont(primeFont)
                else:
                    teamItem.SetFont(statFont)

                self.teams[hA][stat] = teamItem



        mainSizer = wx.BoxSizer()

        for hA in awayHome:
            sizer = wx.BoxSizer(wx.VERTICAL)

            item = self.teams[hA]

            sizer.Add(item["name"], 0, wx.CENTER | wx.BOTTOM, 10)
            recordSizer = wx.BoxSizer()
            recordSizer.Add(item["atsW"])
            recordSizer.Add(wx.StaticText(self, label="-"), 0, wx.LEFT | wx.RIGHT, 15)
            recordSizer.Add(item["atsL"])
            recordSizer.Add(wx.StaticText(self, label="-"), 0, wx.LEFT | wx.RIGHT, 15)
            recordSizer.Add(item["atsP"])
            sizer.Add(recordSizer, 0, wx.CENTER | wx.BOTTOM, 10)

            returnSizer = wx.BoxSizer()
            for key in ("ats$", "money$"):
                keySizer = wx.BoxSizer(wx.VERTICAL)
                keyLabel = wx.StaticText(self, label=key)
                keyLabel.SetFont(wx.Font(wx.FontInfo(7)))

                keySizer.Add(keyLabel,0,wx.CENTER)
                keySizer.Add(item[key], 0, wx.CENTER)
                returnSizer.Add(keySizer, 0, wx.LEFT | wx.RIGHT, 15)
            sizer.Add(returnSizer, 0, wx.CENTER | wx.BOTTOM, 40)


            for stat in [stat for stat in self.gameList if stat not in ("atsW", "atsL", "atsP", "ats$", "money$")]:
                statSizer = wx.BoxSizer()
                label = wx.StaticText(self, label=stat+":")
                label.SetFont(wx.Font(wx.FontInfo(8)))

                statSizer.Add(label, 0, wx.RIGHT, 20)
                statSizer.Add(item[stat], 0)
                sizer.Add(statSizer, 0, wx.CENTER | wx.BOTTOM, 10)

            sizer.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 30)


            returnSizer = wx.BoxSizer()
            for key in ("over$", "under$"):
                keySizer = wx.BoxSizer(wx.VERTICAL)
                keyLabel = wx.StaticText(self, label=key)
                keyLabel.SetFont(wx.Font(wx.FontInfo(7)))

                keySizer.Add(keyLabel,0,wx.CENTER)
                keySizer.Add(item[key], 0, wx.CENTER)
                returnSizer.Add(keySizer, 0, wx.LEFT | wx.RIGHT, 15)
            sizer.Add(returnSizer, 0, wx.CENTER | wx.BOTTOM, 40)
            for stat in [stat for stat in self.ovList if stat not in ("over$", "under$")]:
                statSizer = wx.BoxSizer()
                label = wx.StaticText(self, label=stat+":")
                label.SetFont(wx.Font(wx.FontInfo(8)))

                statSizer.Add(label, 0, wx.RIGHT, 20)
                statSizer.Add(item[stat], 0)
                sizer.Add(statSizer, 0, wx.CENTER | wx.BOTTOM, 10)

            mainSizer.Add(sizer, 1, wx.EXPAND)


        self.SetSizer(mainSizer)
