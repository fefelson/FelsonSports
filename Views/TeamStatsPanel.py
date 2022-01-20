import wx

from itertools import chain


class NCAAFTeamStatsPanel(wx.ScrolledWindow):

    _statList = ("PLAYS", "Points", "TmPaAtt", "TmPaComp", "TmPaYds", "PaAvg", "PaTDs",
                    "TmINTS", "TmRuAtt", "TmRuYds", "RuAvg", "RuTDs", "TmFum", "TO",
                    "PEN", "PENYds", "POSSTIME", "TmPaSACKS", "TmPaSACKYds", "3rd%", "4th%",
                    "TmYDS", )


    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.SetScrollbars(20, 20, 50, 50)

        self.values = dict(zip(("away", "home"), [{} for _ in range(2)]))

        mainSizer = wx.BoxSizer()

        for hA in ("away", "home"):
            pointsPanel = wx.Panel(self, size=(120,120), style=wx.BORDER_SIMPLE)
            for stat in self._statList:
                text = wx.StaticText(self)
                font = wx.Font(wx.FontInfo(15).Bold())
                if stat == 'Points':
                    font = wx.Font(wx.FontInfo(25).Bold())
                    text = wx.StaticText(pointsPanel)
                if stat in ("TO", "TmYDS"):
                    text = wx.StaticText(pointsPanel)


                text.SetFont(font)
                self.values[hA][stat] = text

            sizer = wx.BoxSizer(wx.VERTICAL)

            ptsLabel = wx.StaticText(pointsPanel, label="pts")
            ptsLabel.SetFont( wx.Font(wx.FontInfo(8)))


            penLabel = self.makeLabel("pen")
            penLostLabel = self.makeLabel("yds lost")


            posLabel = self.makeLabel("posTime")
            playsLabel = self.makeLabel("plays")
            paAttLabel = self.makeLabel("att")
            paCompLabel = self.makeLabel("comp")
            paYdsLabel = self.makeLabel("yds")
            paAvgLabel = self.makeLabel("avg")
            paTDLabel = self.makeLabel("TD")
            paINTLabel = self.makeLabel("INT")
            carLabel = self.makeLabel("att")
            ruYdsLabel = self.makeLabel("yds")
            ruAvgLabel = self.makeLabel("avg")
            ruTDLabel = self.makeLabel("TD")
            fumLabel = self.makeLabel("FUM")


            offYdsLabel = wx.StaticText(pointsPanel, label="yds")
            offYdsLabel.SetFont( wx.Font(wx.FontInfo(8)))
            toLabel = wx.StaticText(pointsPanel, label="to")
            toLabel.SetFont( wx.Font(wx.FontInfo(8)))


            pointSizer = wx.BoxSizer(wx.VERTICAL)
            pointSizer.Add(ptsLabel, 0, wx.CENTER)
            pointSizer.Add(self.values[hA]["Points"], 1, wx.CENTER | wx.BOTTOM, 10)
            ydsSizer = wx.BoxSizer()
            itemSizer = wx.BoxSizer(wx.VERTICAL)
            itemSizer.Add(offYdsLabel, 0, wx.CENTER)
            itemSizer.Add(self.values[hA]["TmYDS"], 0, wx.CENTER)
            ydsSizer.Add(itemSizer, 0, wx.RIGHT, 8)
            itemSizer = wx.BoxSizer(wx.VERTICAL)
            itemSizer.Add(toLabel, 0, wx.CENTER)
            itemSizer.Add(self.values[hA]["TO"], 0, wx.CENTER)
            ydsSizer.Add(itemSizer, 0, wx.RIGHT, 8)
            pointSizer.Add(ydsSizer, 0, wx.CENTER)

            pointsPanel.SetSizer(pointSizer)

            detailSizer = wx.BoxSizer(wx.VERTICAL)
            playPosSizer = wx.BoxSizer()

            playSizer = self.xSizer(playsLabel, self.values[hA]["PLAYS"])
            topSizer = self.xSizer(posLabel, self.values[hA]["POSSTIME"])

            playPosSizer.Add(playSizer, 1, wx.CENTER | wx.RIGHT, 15)




            playPosSizer.Add(topSizer, 1, wx.CENTER)

            detailSizer.Add(playPosSizer, 0, wx.CENTER| wx.BOTTOM, 15)

            thirdSizer = wx.BoxSizer()
            thirdSizer.Add(wx.StaticText(self, label="3rd%"), 0, wx.RIGHT, 25)
            thirdSizer.Add(self.values[hA]["3rd%"], 0, wx.CENTER)

            fourthSizer = wx.BoxSizer()
            fourthSizer.Add(wx.StaticText(self, label="4th%"), 0, wx.RIGHT, 25)
            fourthSizer.Add(self.values[hA]["4th%"], 0, wx.CENTER)

            detailSizer.Add(thirdSizer, 0, wx.CENTER)
            detailSizer.Add(fourthSizer, 0, wx.CENTER | wx.BOTTOM, 15)

            penSizer = wx.BoxSizer()
            p1Sizer = self.xSizer(penLabel, self.values[hA]["PEN"])
            p2Sizer = self.xSizer(penLostLabel, self.values[hA]["PENYds"])
            penSizer.Add(p1Sizer, 1, wx.CENTER | wx.RIGHT, 25)
            penSizer.Add(p2Sizer, 1, wx.CENTER)

            detailSizer.Add(penSizer, 0, wx.CENTER)

            passLabel = wx.StaticText(self, label="Passing")
            rushLabel = wx.StaticText(self, label="Rushing")
            font = wx.Font(wx.FontInfo(15).Bold())
            passLabel.SetFont(font)
            rushLabel.SetFont(font)

            sacksLabel = wx.StaticText(self, label="sacks")
            ydsLostLabel = wx.StaticText(self, label="yds lost")
            sacksLabel.SetFont( wx.Font(wx.FontInfo(8)))
            ydsLostLabel.SetFont( wx.Font(wx.FontInfo(8)))

            passingSizer = wx.BoxSizer(wx.VERTICAL)
            passingSizer.Add(passLabel, 0, wx.CENTER | wx.BOTTOM, 15)
            passStatSizer = wx.BoxSizer()

            compSizer = wx.BoxSizer(wx.VERTICAL)
            compSizer.Add(paCompLabel, 0, wx.CENTER | wx.BOTTOM, 10)
            compSizer.Add(self.values[hA]["TmPaComp"], 1, wx.CENTER)

            paCompSizer = self.xSizer(paCompLabel, self.values[hA]["TmPaComp"])
            paAttSizer = self.xSizer(paAttLabel, self.values[hA]["TmPaAtt"])
            paYdsSizer = self.xSizer(paYdsLabel, self.values[hA]["TmPaYds"])
            paAvgSizer = self.xSizer(paAvgLabel, self.values[hA]["PaAvg"])
            paTdSizer = self.xSizer(paTDLabel, self.values[hA]["PaTDs"])
            paIntSizer = self.xSizer(paINTLabel, self.values[hA]["TmINTS"])


            passStatSizer.Add(paCompSizer, 0, wx.RIGHT, 5)
            passStatSizer.Add(wx.StaticText(self, label="-"), 0, wx.CENTER | wx.RIGHT, 5)
            passStatSizer.Add(paAttSizer, 0, wx.RIGHT, 25)


            passStatSizer.Add(paYdsSizer, 0, wx.RIGHT, 10)
            passStatSizer.Add(paAvgSizer, 0, wx.RIGHT, 15)
            passStatSizer.Add(paTdSizer, 0, wx.RIGHT, 10)
            passStatSizer.Add(paIntSizer, 0, wx.RIGHT)
            passingSizer.Add(passStatSizer, 0, wx.CENTER | wx.BOTTOM, 10)

            sackSizer = wx.BoxSizer(wx.HORIZONTAL)
            sSizer = wx.BoxSizer(wx.VERTICAL)
            sSizer.Add(sacksLabel, 0, wx.CENTER)
            sSizer.Add(self.values[hA]["TmPaSACKS"], 0, wx.CENTER)
            sackSizer.Add(sSizer, 1, wx.CENTER | wx.RIGHT, 25)
            sSizer = wx.BoxSizer(wx.VERTICAL)
            sSizer.Add(ydsLostLabel, 0, wx.CENTER)
            sSizer.Add(self.values[hA]["TmPaSACKYds"], 0, wx.CENTER)
            sackSizer.Add(sSizer, 1, wx.CENTER )

            passingSizer.Add(sackSizer, 0, wx.EXPAND)


            rushingSizer = wx.BoxSizer(wx.VERTICAL)
            rushingSizer.Add(rushLabel, 0, wx.CENTER | wx.BOTTOM, 15)
            rushingStatSizer = wx.BoxSizer()
            ruAttSizer = self.xSizer(carLabel, self.values[hA]["TmRuAtt"])
            ruYdsSizer = self.xSizer(ruYdsLabel, self.values[hA]["TmRuYds"])
            ruAvgSizer = self.xSizer(ruAvgLabel, self.values[hA]["RuAvg"])
            ruTDSizer = self.xSizer(ruTDLabel, self.values[hA]["RuTDs"])
            fumSizer = self.xSizer(fumLabel, self.values[hA]["TmFum"])
            rushingStatSizer.Add(ruAttSizer, 0, wx.RIGHT, 25)
            rushingStatSizer.Add(ruYdsSizer, 0, wx.RIGHT, 5)
            rushingStatSizer.Add(ruAvgSizer, 0, wx.RIGHT, 15)
            rushingStatSizer.Add(ruTDSizer, 0, wx.RIGHT, 10)
            rushingStatSizer.Add(fumSizer, 0)
            rushingSizer.Add(rushingStatSizer, 0, wx.CENTER)

            lineSizer = wx.BoxSizer()
            lineSizer.Add(pointsPanel, 0, wx.LEFT | wx.RIGHT, 15)
            lineSizer.Add(detailSizer, 0, wx.LEFT | wx.RIGHT, 15)
            sizer.Add(lineSizer, 0, wx.CENTER | wx.BOTTOM, 40)
            sizer.Add(passingSizer, 0, wx.CENTER | wx.BOTTOM, 25)
            sizer.Add(rushingSizer, 0, wx.CENTER)



            mainSizer.Add(sizer, 1, wx.EXPAND | wx.ALL, 20)
        self.SetSizer(mainSizer)



    def makeLabel(self, text):
        label = wx.StaticText(self, label=text)
        label.SetFont( wx.Font(wx.FontInfo(8)))
        return label


    def xSizer(self, label, item):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(label, 0, wx.CENTER | wx.BOTTOM, 10)
        sizer.Add(item, 1, wx.CENTER)
        return sizer


################################################################################
################################################################################


class NBATeamStatsPanel(wx.ScrolledWindow):

    _stats = ("oreb", "dreb", "reb", "ast", "stl", "blk", "trn", "fls",)
    _shots = ("pts", "fga", "fg%", "fta", "ft%", "tpa", "tp%", "pts_in_pt", "fb_pts")


    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.SetScrollbars(20, 20, 50, 50)

        largeFont = wx.Font(20, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL,
                                        wx.FONTWEIGHT_BOLD)

        mediumFont = wx.Font(15, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL,
                                        wx.FONTWEIGHT_NORMAL)

        smallFont = wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL,
                                        wx.FONTWEIGHT_NORMAL)

        self.values = dict(zip(("away", "home"), [{} for _ in range(2)]))

        mainSizer = wx.BoxSizer()

        for hA in ("away", "home"):

            baseSizer = wx.BoxSizer(wx.VERTICAL)

            shotPctPanel = wx.Panel(self, size= (290,250), style=wx.BORDER_SIMPLE)

            for stat in chain(self._shots, self._stats):
                panel = self if stat in self._stats else shotPctPanel
                if stat == "pts":
                    font = wx.Font(wx.FontInfo(25).Bold())
                    text = wx.StaticText(panel)
                else:
                    text = wx.StaticText(panel)
                    font = wx.Font(wx.FontInfo(15).Bold())

                text.SetFont(font)
                self.values[hA][stat] = text



            ptsLabel = self.makeLabel("pts", shotPctPanel)
            ptPtsLabel = self.makeLabel("pts in pt", shotPctPanel)
            fbPtsLabel = self.makeLabel("fb pts", shotPctPanel)
            fgaLabel = self.makeLabel("fga", shotPctPanel)
            fgPctLabel = self.makeLabel("fg%", shotPctPanel)
            ftaLabel = self.makeLabel("fta", shotPctPanel)
            ftPctLabel = self.makeLabel("ft%", shotPctPanel)
            tpaLabel = self.makeLabel("3pa", shotPctPanel)
            tpPctLabel = self.makeLabel("3p%", shotPctPanel)

            orebLabel = self.makeLabel("oreb")
            drebLabel = self.makeLabel("dreb")
            rebLabel = self.makeLabel("reb")
            astLabel = self.makeLabel("ast")
            stlLabel = self.makeLabel("stl")
            blkLabel = self.makeLabel("blk")
            trnLabel = self.makeLabel("trn")
            flsLabel = self.makeLabel("fls")



            ptsSizer = self.xSizer(ptsLabel, self.values[hA]["pts"])
            fbSizer = self.xSizer(fbPtsLabel, self.values[hA]["fb_pts"])
            ptPtsSizer = self.xSizer(ptPtsLabel, self.values[hA]["pts_in_pt"])
            fgaSizer = self.xSizer(fgaLabel, self.values[hA]["fga"])
            fgPctSizer = self.xSizer(fgPctLabel, self.values[hA]["fg%"])
            ftaSizer = self.xSizer(ftaLabel, self.values[hA]["fta"])
            ftPctSizer = self.xSizer(ftPctLabel, self.values[hA]["ft%"])
            tpaSizer = self.xSizer(tpaLabel, self.values[hA]["tpa"])
            tpPctSizer = self.xSizer(tpPctLabel, self.values[hA]["tp%"])

            shotPctSizer = wx.BoxSizer()
            ptGroupSizer = wx.BoxSizer(wx.VERTICAL)
            ptGroupSizer.Add(ptsSizer, 0, wx.CENTER | wx.BOTTOM, 15)
            ptRowSizer = wx.BoxSizer()
            ptRowSizer.Add(fbSizer, 0, wx.CENTER | wx.RIGHT, 15)
            ptRowSizer.Add(ptPtsSizer, 0, wx.CENTER | wx.RIGHT, 15)
            ptGroupSizer.Add(ptRowSizer, 0, wx.CENTER | wx.EXPAND, 15)

            ptPctSizer = wx.BoxSizer()
            ptPctSizer.Add(fgPctSizer, 0, wx.CENTER | wx.RIGHT, 35)
            ptPctSizer.Add(ftPctSizer, 0, wx.CENTER | wx.RIGHT, 35)
            ptPctSizer.Add(tpPctSizer, 0, wx.CENTER | wx.RIGHT, 35)

            shotAttSizer = wx.BoxSizer(wx.VERTICAL)
            shotAttSizer.Add(fgaSizer, 0, wx.CENTER | wx.BOTTOM, 15)
            shotAttSizer.Add(ftaSizer, 0, wx.CENTER | wx.BOTTOM, 15)
            shotAttSizer.Add(tpaSizer, 0, wx.CENTER | wx.BOTTOM, 15)

            rightShotPct = wx.BoxSizer(wx.VERTICAL)
            rightShotPct.Add(ptGroupSizer, 0, wx.CENTER | wx.BOTTOM, 35)
            rightShotPct.Add(ptPctSizer, 0, wx.CENTER)


            shotPctSizer.Add(shotAttSizer, 0, wx.CENTER | wx.RIGHT, 15)
            shotPctSizer.Add(rightShotPct, 0, wx.CENTER | wx.BOTTOM, 25)

            shotPctPanel.SetSizer(shotPctSizer)

            orebSizer = self.xSizer(orebLabel, self.values[hA]["oreb"])
            drebSizer = self.xSizer(drebLabel, self.values[hA]["dreb"])
            rebSizer = self.xSizer(rebLabel, self.values[hA]["reb"])
            astSizer = self.xSizer(astLabel, self.values[hA]["ast"])
            stlSizer = self.xSizer(stlLabel, self.values[hA]["stl"])
            blkSizer = self.xSizer(blkLabel, self.values[hA]["blk"])
            trnSizer = self.xSizer(trnLabel, self.values[hA]["trn"])
            flsSizer = self.xSizer(flsLabel, self.values[hA]["fls"])

            statSizer = wx.BoxSizer()
            rebAllSizer = wx.BoxSizer(wx.VERTICAL)
            rebBSizer = wx.BoxSizer()
            rebBSizer.Add(orebSizer, 0, wx.CENTER | wx.RIGHT, 30)
            rebBSizer.Add(drebSizer, 0, wx.CENTER)
            rebAllSizer.Add(rebSizer, 0, wx.CENTER | wx.BOTTOM, 15)
            rebAllSizer.Add(rebBSizer, 0, wx.CENTER)

            asbSizer = wx.BoxSizer()
            asbSizer.Add(astSizer, 0, wx.CENTER | wx.RIGHT, 25)
            asbSizer.Add(stlSizer, 0, wx.CENTER | wx.RIGHT, 25)
            asbSizer.Add(blkSizer, 0, wx.CENTER | wx.RIGHT, 15)

            statSizer.Add(rebAllSizer, 0, wx.CENTER | wx.RIGHT, 65)
            statSizer.Add(asbSizer, 0, wx.CENTER)

            flTrnSizer = wx.BoxSizer()
            flTrnSizer.Add(flsSizer, 0, wx.CENTER | wx.RIGHT, 95)
            flTrnSizer.Add(trnSizer, 0, wx.CENTER)

            baseSizer.Add(flTrnSizer, 0, wx.CENTER | wx.BOTTOM, 15)
            baseSizer.Add(shotPctPanel, 0, wx.CENTER | wx.BOTTOM, 30)
            baseSizer.Add(statSizer, 0, wx.CENTER)


            mainSizer.Add(baseSizer, 1, wx.EXPAND | wx.ALL, 15)

        self.SetSizer(mainSizer)



    def makeLabel(self, text, panel=None):
        if not panel:
            panel = self
        label = wx.StaticText(panel, label=text)
        label.SetFont( wx.Font(wx.FontInfo(8)))
        return label


    def xSizer(self, label, item):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(label, 0, wx.CENTER | wx.BOTTOM, 10)
        sizer.Add(item, 0, wx.CENTER)
        return sizer
