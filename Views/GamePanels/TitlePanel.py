import wx


class TitlePanel(wx.Panel):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.panels = {}
        self.teamNames = {}
        self.teamRecords = {}
        self.hATags = {}
        self.b2bTags = {}

        largeFont = wx.Font(25, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL,
                                        wx.FONTWEIGHT_BOLD)

        mediumFont = wx.Font(20, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL,
                                        wx.FONTWEIGHT_BOLD)

        smallFont = wx.Font(15, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL,
                                        wx.FONTWEIGHT_BOLD)

        for hA in ("away", "home"):
            panel = wx.Panel(self)
            tn = wx.StaticText(panel)
            tn.SetFont(largeFont)
            tn.SetBackgroundColour(wx.BLACK)
            tn.SetForegroundColour(wx.Colour("GREY"))

            tr = wx.StaticText(panel)
            tr.SetFont(smallFont)
            tr.SetBackgroundColour(wx.BLACK)
            tr.SetForegroundColour(wx.Colour("GREY"))

            haTag = wx.StaticText(panel)
            haTag.SetForegroundColour(wx.WHITE)

            b2bTag = wx.StaticText(panel, label="B2B")
            b2bTag.SetForegroundColour(wx.WHITE)
            b2bTag.SetBackgroundColour(wx.RED)
            b2bTag.Hide()

            sizer = wx.BoxSizer(wx.VERTICAL)
            tagSizer = wx.BoxSizer()

            tagSizer.Add(haTag, 0, wx.RIGHT, 5)
            tagSizer.Add(b2bTag, 0)

            sizer.Add(tn, 0, wx.CENTER | wx.TOP | wx.BOTTOM, 10)
            sizer.Add(tr, 0, wx.CENTER | wx.TOP | wx.BOTTOM, 10)
            sizer.Add(tagSizer, 0, wx.GROW | wx.TOP | wx.LEFT, 10)

            panel.SetSizer(sizer)

            self.panels[hA] = panel
            self.teamNames[hA] = tn
            self.teamRecords[hA] = tr
            self.b2bTags[hA] = b2bTag
            self.hATags[hA] = haTag



        nameSizer = wx.BoxSizer()
        nameSizer.Add(self.panels["away"], 1, wx.EXPAND)
        nameSizer.Add(self.panels["home"], 1, wx.EXPAND)

        self.SetSizer(nameSizer)





    def setPanel(self, game):
        for hA in ("away", "home"):
            team = game.getTeam(hA)
            self.b2bTags[hA].Hide()
            self.teamNames[hA].SetLabel(" ".join([team.getInfo(x) for x in ("firstName", "lastName")]))
            # self.teamNames[hA].SetBackgroundColour(wx.Colour(team.getInfo("colors")[1]))

            self.teamRecords[hA].SetLabel("( {} - {} )".format(team.getStats("all_results", "wins"), team.getStats("all_results", "loses")))
            # self.teamRecords[hA].SetBackgroundColour(wx.Colour(team.getInfo("colors")[1]))
            # self.panels[hA].SetBackgroundColour(wx.Colour(team.getInfo("colors")[0]))
            haValue = "Home" if hA == "home" else "Away"
            haColor = wx.GREEN if hA == "home" else wx.BLUE
            self.hATags[hA].SetLabel(haValue)
            self.hATags[hA].SetBackgroundColour(haColor)

            # if game.getB2B(hA):
            #     self.b2bTags[hA].Show()

            self.panels[hA].Layout()


        self.Layout()
