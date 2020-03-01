import wx


class StatsPanel(wx.Panel):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.SetMaxSize(wx.Size(-1, 300))

        largeFont = wx.Font(20, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL,
                                        wx.FONTWEIGHT_BOLD)

        mediumFont = wx.Font(15, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL,
                                        wx.FONTWEIGHT_NORMAL)

        smallFont = wx.Font(10, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL,
                                        wx.FONTWEIGHT_NORMAL)

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

        self.fga = wx.StaticText(self)
        self.fga.SetFont(largeFont)

        self.fta = wx.StaticText(self)
        self.fta.SetFont(mediumFont)

        self.tpa = wx.StaticText(self)
        self.tpa.SetFont(mediumFont)



        self.oppFGA = wx.StaticText(self)
        self.oppFGA.SetFont(mediumFont)

        self.oppFTA = wx.StaticText(self)
        self.oppFTA.SetFont(smallFont)

        self.oppTPA = wx.StaticText(self)
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
        pctSizer.Add(wx.StaticText(self, label="ft%"))
        pctSizer.Add(ftaSizer, 0, wx.CENTER)
        pctSizer.Add(wx.StaticText(self, label="3pt%"))
        pctSizer.Add(tpaSizer, 0, wx.CENTER)

        shotSizer = wx.BoxSizer(wx.HORIZONTAL)
        shotSizer.Add(fgaSizer, 0, wx.CENTER | wx.LEFT | wx.RIGHT, 15)
        shotSizer.Add(pctSizer, 0, wx.CENTER | wx.LEFT | wx.RIGHT, 15)


        ptsSizer = wx.BoxSizer(wx.VERTICAL)
        ptsSizer.Add(self.ppg, 0, wx.BOTTOM, 10)
        ptsSizer.Add(self.oppPPG, 0, wx.TOP, 10)
        ptsSizer.Add(shotSizer)
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
