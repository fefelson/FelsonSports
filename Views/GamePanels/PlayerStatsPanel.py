import wx


class PlayerPanel(wx.Panel):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, style=wx.BORDER_SIMPLE, *args, **kwargs)
        self.SetMaxSize((400,400))

        largeFont = wx.Font(15, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL,
                                        wx.FONTWEIGHT_BOLD)

        mediumFont = wx.Font(10, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL,
                                        wx.FONTWEIGHT_NORMAL)

        smallFont = wx.Font(8, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL,
                                        wx.FONTWEIGHT_NORMAL)

        self.name = wx.StaticText(self)
        self.name.SetFont(largeFont)
        self.positions = wx.StaticText(self)
        self.positions.SetFont(smallFont)

        self.mins = wx.StaticText(self)
        self.score = wx.StaticText(self)
        self.pts = wx.StaticText(self)
        self.reb = wx.StaticText(self)
        self.ast = wx.StaticText(self)
        self.stl = wx.StaticText(self)
        self.blk = wx.StaticText(self)

        self.score.SetFont(largeFont)
        for item in (self.mins, self.pts, self.reb, self.ast, self.stl, self.blk):
            item.SetFont(mediumFont)

        self.avgScore = wx.StaticText(self)
        self.avgScore.SetFont(mediumFont)

        scoreSizer = wx.BoxSizer(wx.VERTICAL)
        scoreSizer.Add(self.score, 1, wx.EXPAND)
        scoreSizer.Add(self.avgScore, 0, wx.EXPAND)

        nameSizer = wx.BoxSizer()
        nameSizer.Add(self.name, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 25)
        nameSizer.Add(scoreSizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 25)
        nameSizer.Add(self.positions, 0, wx.EXPAND | wx.LEFT, 25)

        statsSizer = wx.GridSizer(2, 6, (3,3))

        statsSizer.Add(wx.StaticText(self, label="mins"))
        statsSizer.Add(wx.StaticText(self, label="pts"))
        statsSizer.Add(wx.StaticText(self, label="reb"))
        statsSizer.Add(wx.StaticText(self, label="ast"))
        statsSizer.Add(wx.StaticText(self, label="stl"))
        statsSizer.Add(wx.StaticText(self, label="blk"))

        statsSizer.Add(self.mins)
        statsSizer.Add(self.pts)
        statsSizer.Add(self.reb)
        statsSizer.Add(self.ast)
        statsSizer.Add(self.stl)
        statsSizer.Add(self.blk)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(nameSizer)
        sizer.Add(statsSizer, 0, wx.EXPAND | wx.LEFT, 25)
        self.SetSizer(sizer)


    def setPanel(self, game, player):

        self.name.SetLabel(str(player))
        self.positions.SetLabel(", ".join(player.getInfo("pos")))
        if game.hasPlayed:
            self.mins.SetLabel("{}".format(round(game.getPlayerStats(player.getId(), "mins"))))
            self.score.SetLabel("{:.2f}".format(game.getPlayerStats(player.getId(), "score")))
            self.pts.SetLabel(str(game.getPlayerStats(player.getId(), "pts")))
            self.reb.SetLabel(str(game.getPlayerStats(player.getId(), "reb")))
            self.ast.SetLabel(str(game.getPlayerStats(player.getId(), "ast")))
            self.stl.SetLabel(str(game.getPlayerStats(player.getId(), "stl")))
            self.blk.SetLabel(str(game.getPlayerStats(player.getId(), "blk")))
        else:
            self.mins.SetLabel("{:.2f}".format(player.getStats("mins")))
            self.score.SetLabel("na")
            self.pts.SetLabel("{:.2f}".format(player.getStats("pts")))
            self.reb.SetLabel("{:.2f}".format(player.getStats("reb")))
            self.ast.SetLabel("{:.2f}".format(player.getStats("ast")))
            self.stl.SetLabel("{:.2f}".format(player.getStats("stl")))
            self.blk.SetLabel("{:.2f}".format(player.getStats("blk")))


        self.avgScore.SetLabel("{:.2f}".format(player.getStats("score")))


        self.Layout()


class TeamPanel(wx.Panel):

    def __init__(self, parent, hA, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.hA = hA
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)


    def setPanel(self, game):
        self.DestroyChildren()
        self.sizer.Clear()
        players = []
        if game.hasPlayed:
            players = game.getTeamPlayers(self.hA)
        else:
            players = game.getTeam(self.hA).getPlayers()

        for player in players:
            p = PlayerPanel(self)
            p.setPanel(game, player)
            self.sizer.Add(p, 1, wx.EXPAND | wx.TOP | wx.BOTTOM, 15)
        self.Layout()



class PlayerStatsPanel(wx.Panel):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.statsBox = wx.ComboBox(self, choices=("all", "winner", "loser", "home/away"))
        self.statsBox.SetSelection(0)

        self.awayPanel = TeamPanel(self, "away")
        self.homePanel = TeamPanel(self, "home")

        panelSizer = wx.BoxSizer()
        panelSizer.Add(self.awayPanel, 1, wx.EXPAND)
        panelSizer.Add(self.homePanel, 1, wx.EXPAND)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.statsBox)
        sizer.Add(panelSizer, 1, wx.EXPAND)
        self.SetSizer(sizer)


    def setPanel(self, game):
        self.awayPanel.setPanel(game)
        self.homePanel.setPanel(game)
        self.Layout()
