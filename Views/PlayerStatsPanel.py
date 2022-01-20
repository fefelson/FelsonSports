import wx

from copy import deepcopy
from pprint import pprint




class BballPlayerStatsPanel(wx.ScrolledWindow):

    _statList = ("gp", "start%", "fg%", "ft%", "tp%", "pts", "oreb",  "reb",
                    "ast", "stl", "blk", "trn", "fls", "mins", "plmn")

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.SetScrollbars(20, 20, 50, 50)

        mainSizer = wx.BoxSizer()
        self.values = {"away": [], "home":[]}

        for hA in ("away", "home"):
            teamSizer = wx.BoxSizer(wx.VERTICAL)

            for i in range(10):
                items = {}
                self.values[hA].append({})

                for stat in self._statList:
                    if stat in ("tpa","tp%"):
                        label = self.makeLabel("3"+stat[1:])
                    else:
                        label = self.makeLabel(stat)
                    if stat != "pts":
                        font = wx.Font(wx.FontInfo(10).Bold())
                    elif stat in ("start%", "mins", "plmn"):
                        font = wx.Font(wx.FontInfo(8).Bold())

                    else:
                        font = wx.Font(wx.FontInfo(15).Bold())

                    text = wx.StaticText(self)
                    text.SetFont(font)

                    self.values[hA][i][stat] = text
                    items[stat] = self.xSizer(label, text)

                statSizer = wx.BoxSizer()
                recSizer = wx.BoxSizer(wx.VERTICAL)

                row1 = wx.BoxSizer()
                row1.Add(items["fg%"], 0, wx.RIGHT, 35)
                row1.Add(items["ft%"], 0, wx.RIGHT, 35)
                row1.Add(items["tp%"])


                recSizer.Add(row1, 0, wx.BOTTOM, 10)

                row2 = wx.BoxSizer()
                row2.Add(items["reb"], 0, wx.RIGHT, 10)
                row2.Add(items["oreb"], 0, wx.RIGHT, 35)
                row2.Add(items["ast"], 0, wx.RIGHT, 10)
                row2.Add(items["stl"], 0, wx.RIGHT, 10)
                row2.Add(items["blk"], 0, wx.RIGHT, 30)
                row2.Add(items["trn"], 0, wx.RIGHT, 10)
                row2.Add(items["fls"], 0, wx.RIGHT, 10)

                recSizer.Add(row2, 0, wx.BOTTOM, 10)

                statSizer.Add(items["pts"], 0, wx.CENTER | wx.RIGHT, 35)
                statSizer.Add(recSizer, 0)


                sizer = wx.BoxSizer(wx.VERTICAL)

                name = wx.StaticText(self)
                name.SetFont(wx.Font(wx.FontInfo(13).Bold()))

                pos = wx.StaticText(self)
                pos.SetFont(wx.Font(wx.FontInfo(9)))

                self.values[hA][i]["name"] = name
                self.values[hA][i]["pos"] = pos
                self.values[hA][i]["inj"] = wx.Panel(self, size=(10,10))


                nameSizer = wx.BoxSizer()
                nameSizer.Add(name, 1, wx.EXPAND | wx.RIGHT, 15)
                nameSizer.Add(pos, 0, wx.EXPAND | wx.RIGHT, 5)
                nameSizer.Add(self.values[hA][i]["inj"], 0, wx.CENTER | wx.RIGHT, 15)
                nameSizer.Add(items["gp"], 0, wx.RIGHT, 10)
                nameSizer.Add(items["start%"], 0, wx.RIGHT, 10)
                nameSizer.Add(items["mins"], 0, wx.RIGHT, 10)
                nameSizer.Add(items["plmn"], 0, wx.RIGHT, 10)

                sizer.Add(nameSizer, 0, wx.BOTTOM, 25)
                sizer.Add(statSizer)
                teamSizer.Add(sizer, 1, wx.BOTTOM, 10)
                teamSizer.Add(wx.StaticLine(self), 0, wx.EXPAND)

            mainSizer.Add(teamSizer, 1, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(mainSizer)


    def makeLabel(self, text):
        label = wx.StaticText(self, label=text)
        label.SetFont( wx.Font(wx.FontInfo(8)))
        return label


    def xSizer(self, label, item):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(label, 0, wx.CENTER | wx.BOTTOM, 8)
        sizer.Add(item, 1, wx.CENTER)
        return sizer



class FballPlayerStatsPanel(wx.ScrolledWindow):

    _passingList = ("att", "comp%", "yds", "avg", "td", "int", "rating")
    _rushingList = ("car", "yds", "avg", "td", "fum")
    _receivingList = ("tgt", "rec", "yds", "avg", "td", "fum")

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.SetScrollbars(20, 20, 50, 50)

        mainFont = wx.Font(wx.FontInfo(14).Bold())

        statGroup = {"passing": [], "rushing": [], "receiving": []}

        mainSizer = wx.BoxSizer()
        self.values = {"away": deepcopy(statGroup), "home":deepcopy(statGroup)}

        for hA in ("away", "home"):
            teamSizer = wx.BoxSizer(wx.VERTICAL)

            label = wx.StaticText(self, label="Passing")
            label.SetFont(mainFont)

            teamSizer.Add(label, 0, wx.CENTER | wx.TOP | wx.BOTTOM, 25)

            for i in range(2):
                self.addPlayer(hA, teamSizer, "passing", self._passingList)

            label = wx.StaticText(self, label="Rushing")
            label.SetFont(mainFont)

            teamSizer.Add(label, 0, wx.CENTER | wx.TOP | wx.BOTTOM, 25)
            for i in range(4):
                self.addPlayer(hA, teamSizer, "rushing", self._rushingList)

            label = wx.StaticText(self, label="Receiving")
            label.SetFont(mainFont)

            teamSizer.Add(label, 0, wx.CENTER | wx.TOP | wx.BOTTOM, 25)

            for i in range(7):
                self.addPlayer(hA, teamSizer, "receiving", self._receivingList)

            mainSizer.Add(teamSizer, 1, wx.EXPAND | wx.ALL, 15)
        self.SetSizer(mainSizer)


    def addPlayer(self, hA, sizer, title, statList):
        values = {}

        playerSizer = wx.BoxSizer(wx.VERTICAL)
        nameSizer = wx.BoxSizer()
        name = wx.StaticText(self)
        name.SetFont(wx.Font(wx.FontInfo(13).Bold()))

        pos = wx.StaticText(self)
        pos.SetFont(wx.Font(wx.FontInfo(9)))

        values["name"] = name
        values["pos"] = pos
        values["inj"] = wx.Panel(self, size=(10,10))

        nameSizer = wx.BoxSizer()
        nameSizer.Add(name, 1, wx.EXPAND | wx.RIGHT, 15)
        nameSizer.Add(pos, 0, wx.EXPAND | wx.RIGHT, 5)
        nameSizer.Add(values["inj"], 0, wx.CENTER | wx.RIGHT, 15)

        statSizer = wx.BoxSizer()
        for stat in statList:
            text = wx.StaticText(self)
            text.SetFont(wx.Font(wx.FontInfo(10).Bold()))
            label = self.makeLabel(stat)
            values[stat] = text
            statSizer.Add(self.xSizer(label, text), 0, wx.CENTER | wx.RIGHT, 25)

        playerSizer.Add(nameSizer, 0, wx.BOTTOM, 10)
        playerSizer.Add(statSizer, 0)

        sizer.Add(playerSizer, 0, wx.BOTTOM, 10)
        sizer.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.BOTTOM, 20)

        self.values[hA][title].append(values)




    def makeLabel(self, text):
        label = wx.StaticText(self, label=text)
        label.SetFont( wx.Font(wx.FontInfo(8)))
        return label


    def xSizer(self, label, item):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(label, 0, wx.CENTER | wx.BOTTOM, 8)
        sizer.Add(item, 1, wx.CENTER)
        return sizer


    def reset(self):
        for hA in ("away", "home"):
            for label in ("passing", "rushing", "receiving"):
                for player in self.values[hA][label]:
                    for item in player.values():
                        item.SetLabel("--")
                        item.SetBackgroundColour(wx.WHITE)
