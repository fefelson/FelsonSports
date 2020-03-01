import re
import wx


class StatPanel(wx.Panel):

    def __init__(self, parent, hA, *args, **kwargs):
        super().__init__(parent, style=wx.BORDER_SIMPLE, *args, **kwargs)

        largeFont = wx.Font(20, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL,
                                        wx.FONTWEIGHT_BOLD)

        mediumFont = wx.Font(15, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL,
                                        wx.FONTWEIGHT_NORMAL)

        smallFont = wx.Font(10, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL,
                                        wx.FONTWEIGHT_NORMAL)


        shotPctPanel = wx.Panel(self, style=wx.BORDER_SIMPLE)

        self.hA = hA

        self.ppg = wx.StaticText(self)
        self.ppg.SetFont(largeFont)

        self.rpg = wx.StaticText(self)
        self.rpg.SetFont(mediumFont)

        self.apg = wx.StaticText(self)
        self.apg.SetFont(mediumFont)

        self.spg = wx.StaticText(self)
        self.spg.SetFont(mediumFont)

        self.bpg = wx.StaticText(self)
        self.bpg.SetFont(mediumFont)

        self.oppPPG = wx.StaticText(self)
        self.oppPPG.SetFont(mediumFont)

        self.oppRPG = wx.StaticText(self)
        self.oppRPG.SetFont(smallFont)

        self.oppAPG = wx.StaticText(self)
        self.oppAPG.SetFont(smallFont)

        self.oppSPG = wx.StaticText(self)
        self.oppSPG.SetFont(smallFont)

        self.oppBPG = wx.StaticText(self)
        self.oppBPG.SetFont(smallFont)



        self.fga = wx.StaticText(shotPctPanel)
        self.fga.SetFont(largeFont)

        self.fta = wx.StaticText(shotPctPanel)
        self.fta.SetFont(mediumFont)

        self.tpa = wx.StaticText(shotPctPanel)
        self.tpa.SetFont(mediumFont)



        self.oppFGA = wx.StaticText(shotPctPanel)
        self.oppFGA.SetFont(mediumFont)

        self.oppFTA = wx.StaticText(shotPctPanel)
        self.oppFTA.SetFont(smallFont)

        self.oppTPA = wx.StaticText(shotPctPanel)
        self.oppTPA.SetFont(smallFont)


        fgaSizer = wx.BoxSizer(wx.VERTICAL)
        fgaSizer.Add(self.fga, 0, wx.BOTTOM, 10)
        fgaSizer.Add(self.oppFGA, 0, wx.TOP, 10)

        ftaSizer = wx.GridSizer(1,2,2)
        ftaSizer.Add(self.fta)
        ftaSizer.Add(self.oppFTA)

        tpaSizer = wx.GridSizer(1,2,2)
        tpaSizer.Add(self.tpa)
        tpaSizer.Add(self.oppTPA)

        pctSizer = wx.GridSizer(2,2,2)
        pctSizer.Add(wx.StaticText(shotPctPanel, label="ft%"))
        pctSizer.Add(ftaSizer, 0, wx.CENTER)
        pctSizer.Add(wx.StaticText(shotPctPanel, label="3pt%"))
        pctSizer.Add(tpaSizer, 0, wx.CENTER)

        shotSizer = wx.BoxSizer(wx.HORIZONTAL)
        shotSizer.Add(fgaSizer, 0, wx.CENTER | wx.LEFT | wx.RIGHT, 15)
        shotSizer.Add(pctSizer, 0, wx.CENTER | wx.LEFT | wx.RIGHT, 15)

        shotPctPanel.SetSizer(shotSizer)




        ptsSizer = wx.BoxSizer(wx.VERTICAL)
        ptsSizer.Add(self.ppg, 0, wx.CENTER | wx.BOTTOM, 10)
        ptsSizer.Add(self.oppPPG, 0, wx.CENTER | wx.TOP, 10)
        ptsSizer.Add(shotPctPanel, 0, wx.TOP, 10)
        ####

        rebSizer = wx.GridSizer(1,2,2)
        rebSizer.Add(self.rpg)
        rebSizer.Add(self.oppRPG)

        astSizer = wx.GridSizer(1,2,2)
        astSizer.Add(self.apg)
        astSizer.Add(self.oppAPG)

        stlSizer = wx.GridSizer(1,2,2)
        stlSizer.Add(self.spg)
        stlSizer.Add(self.oppSPG)

        blkSizer = wx.GridSizer(1,2,2)
        blkSizer.Add(self.bpg)
        blkSizer.Add(self.oppBPG)


        statSizer = wx.GridSizer(2,4,2)
        statSizer.Add(wx.StaticText(self, label="reb"))
        statSizer.Add(rebSizer, 0, wx.CENTER)
        statSizer.Add(wx.StaticText(self, label="ast"))
        statSizer.Add(astSizer, 0, wx.CENTER)
        statSizer.Add(wx.StaticText(self, label="stl"))
        statSizer.Add(stlSizer, 0, wx.CENTER)
        statSizer.Add(wx.StaticText(self, label="blk"))
        statSizer.Add(blkSizer, 0, wx.CENTER)


        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(ptsSizer, 0, wx.CENTER | wx.LEFT | wx.RIGHT, 15)
        sizer.Add(statSizer, 0, wx.CENTER | wx.LEFT | wx.RIGHT, 15)

        self.SetSizer(sizer)



    def setPanel(self, itemLabel, game):

        team = game.getTeam(self.hA)
        if "home/away" in itemLabel:
            itemLabel = re.sub("home/away", self.hA, itemLabel)
        leagueLabel = re.sub("opp", "team", itemLabel)


        if game.hasPlayed:

            self.ppg.SetLabel(str(game.getTeamStats(self.hA, "pts")))

            self.rpg.SetLabel(str(game.getTeamStats(self.hA, "reb")))

            self.apg.SetLabel(str(game.getTeamStats(self.hA, "ast")))

            self.spg.SetLabel(str(game.getTeamStats(self.hA, "stl")))

            self.bpg.SetLabel(str(game.getTeamStats(self.hA, "blk")))

            fg = int(100 * (game.getTeamStats(self.hA, "fgm") / game.getTeamStats(self.hA, "fga")))
            ft = int(100 * (game.getTeamStats(self.hA, "ftm") / game.getTeamStats(self.hA, "fta")))
            tp = int(100 * (game.getTeamStats(self.hA, "tpm") / game.getTeamStats(self.hA, "tpa")))

            self.fga.SetLabel(str(fg))

            self.fta.SetLabel(str(ft))

            self.tpa.SetLabel(str(tp))

            self.oppPPG.SetLabel("{:.2f}".format(team.getStats(itemLabel, "pts")))

            self.oppRPG.SetLabel("{:.2f}".format(team.getStats(itemLabel, "reb")))

            self.oppAPG.SetLabel("{:.2f}".format(team.getStats(itemLabel, "ast")))

            self.oppSPG.SetLabel("{:.2f}".format(team.getStats(itemLabel, "stl")))

            self.oppBPG.SetLabel("{:.2f}".format(team.getStats(itemLabel, "blk")))

            fg = int(100 * (team.getStats(itemLabel, "fgm") / team.getStats(itemLabel, "fga")))
            ft = int(100 * (team.getStats(itemLabel, "ftm") / team.getStats(itemLabel, "fta")))
            tp = int(100 * (team.getStats(itemLabel, "tpm") / team.getStats(itemLabel, "tpa")))

            self.oppFGA.SetLabel(str(fg))

            self.oppFTA.SetLabel(str(ft))

            self.oppTPA.SetLabel(str(tp))

        else:

            self.ppg.SetLabel("{:.2f}".format(team.getStats(itemLabel, "pts")))

            self.rpg.SetLabel("{:.2f}".format(team.getStats(itemLabel, "reb")))

            self.apg.SetLabel("{:.2f}".format(team.getStats(itemLabel, "ast")))

            self.spg.SetLabel("{:.2f}".format(team.getStats(itemLabel, "stl")))

            self.bpg.SetLabel("{:.2f}".format(team.getStats(itemLabel, "blk")))

            fg = int(100 * (team.getStats(itemLabel, "fgm") / team.getStats(itemLabel, "fga")))
            ft = int(100 * (team.getStats(itemLabel, "ftm") / team.getStats(itemLabel, "fta")))
            tp = int(100 * (team.getStats(itemLabel, "tpm") / team.getStats(itemLabel, "tpa")))

            self.fga.SetLabel(str(fg))

            self.fta.SetLabel(str(ft))

            self.tpa.SetLabel(str(tp))


            self.oppPPG.SetLabel("{:.2f}".format(team.getLeagueStats(leagueLabel, "pts")))

            self.oppRPG.SetLabel("{:.2f}".format(team.getLeagueStats(leagueLabel, "reb")))

            self.oppAPG.SetLabel("{:.2f}".format(team.getLeagueStats(leagueLabel, "ast")))

            self.oppSPG.SetLabel("{:.2f}".format(team.getLeagueStats(leagueLabel, "stl")))

            self.oppBPG.SetLabel("{:.2f}".format(team.getLeagueStats(leagueLabel, "blk")))


            fg = int(100 * (team.getLeagueStats(leagueLabel, "fgm") / team.getLeagueStats(leagueLabel, "fga")))
            ft = int(100 * (team.getLeagueStats(leagueLabel, "ftm") / team.getLeagueStats(leagueLabel, "fta")))
            tp = int(100 * (team.getLeagueStats(leagueLabel, "tpm") / team.getLeagueStats(leagueLabel, "tpa")))

            self.oppFGA.SetLabel(str(fg))

            self.oppFTA.SetLabel(str(ft))

            self.oppTPA.SetLabel(str(tp))

        self.Layout()



class TeamStatsPanel(wx.Panel):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.offDefBox = wx.ComboBox(self, choices=("team", "opp"))
        self.offDefBox.SetSelection(0)

        self.statsBox = wx.ComboBox(self, choices=("all", "winner", "loser", "home/away"))
        self.statsBox.SetSelection(0)

        self.awayPanel = StatPanel(self, "away")
        self.homePanel = StatPanel(self, "home")

        comboSizer = wx.BoxSizer()
        comboSizer.Add(self.offDefBox)
        comboSizer.Add(self.statsBox)

        teamSizer = wx.BoxSizer()
        teamSizer.Add(self.awayPanel, 1, wx.EXPAND)
        teamSizer.Add(self.homePanel, 1, wx.EXPAND)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(comboSizer, 0, wx.CENTER)
        sizer.Add(teamSizer, 1, wx.EXPAND)


        self.SetSizer(sizer)


    def setPanel(self, game):
        offDef = self.offDefBox.GetStringSelection()
        stats = self.statsBox.GetStringSelection()

        itemLabel = "{}_{}".format(stats, offDef)

        self.awayPanel.setPanel(itemLabel, game)
        self.homePanel.setPanel(itemLabel, game)
        self.Layout()
