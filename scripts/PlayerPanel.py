import wx

class PitcherPanel(wx.Panel):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        
        # Panels
        self.mainPanel = wx.Panel(self)
        self.mainPanel.SetMinSize((850,300))
        self.mainPanel.SetMaxSize((850,300))
        self.expandPanel = wx.ScrolledWindow(self, style=wx.VSCROLL)
        self.expandPanel.SetScrollbars(20, 20, 50, 50)
        self.expandPanel.SetBackgroundColour(wx.GREEN)
        self.expandPanel.SetMinSize((850,300))
        self.expandPanel.Hide()
        

        # Fonts

        #   vsFont
        priceFont = wx.Font(20, wx.ROMAN, wx.NORMAL, wx.BOLD)
        infoFont = wx.Font(16, wx.ROMAN, wx.NORMAL, wx.NORMAL)
        vsFont = wx.Font(16, wx.SWISS, wx.NORMAL, wx.BOLD)
        ptsFont = wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD)
        pts2Font = wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD)
        pts3Font = wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD)
        labelFont = wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL)

        # Widgets

        #   expandBttn
        self.expandBttn = wx.Button(self.mainPanel, label="Expand")
        self.expandBttn.Bind(wx.EVT_BUTTON, self.onExpand)

        #   priceValue
        self.priceValue = wx.StaticText(self.mainPanel, label="$2000")
        self.priceValue.SetFont(priceFont)

        #   oppVsLabel
        oppVsLabel = wx.StaticText(self.mainPanel, label="VS.")
        oppVsLabel.SetFont(vsFont)

        #   oppLogo
        self.oppLogo = wx.StaticBitmap(self.mainPanel, size=(50,50))
        self.oppLogo.SetMinSize((50,50))
        self.oppLogo.SetBitmap(wx.Image("/home/ededub/FEFelson/MLBProjections/Teams/Logos/G20.png", wx.BITMAP_TYPE_ANY).Scale(50, 50, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap())

        #   oppPtsValue
        self.oppPtsValue = wx.TextCtrl(self.mainPanel, value="12.0", style=wx.TE_READONLY)
        self.oppPtsValue.SetFont(ptsFont)
        self.oppPtsValue.SetMaxSize((65,50))
        oppPtsLabel = wx.StaticText(self.mainPanel, label = "SPs vs Team")

        #   oppPctValue
        self.oppPctValue = wx.TextCtrl(self.mainPanel, value="-12.0%", style=wx.TE_READONLY)
        self.oppPctValue.SetFont(ptsFont)
        self.oppPctValue.SetMaxSize((65,50))

        #   oppPtsThrValue
        self.oppPtsThrValue = wx.TextCtrl(self.mainPanel, value="12.0", style=wx.TE_READONLY)
        self.oppPtsThrValue.SetFont(ptsFont)
        self.oppPtsThrValue.SetMaxSize((65,50))
        oppPtsThrLabel = wx.StaticText(self.mainPanel, label = "LHPs vs Team")

        #   oppPctThrValue
        self.oppPctThrValue = wx.TextCtrl(self.mainPanel, value="-12.0%", style=wx.TE_READONLY)
        self.oppPctThrValue.SetFont(ptsFont)
        self.oppPctThrValue.SetMaxSize((65,50))

        #   toggleBttn
        self.toggleBttn = SToggleButton(self.mainPanel, label="Add", size=(70,70))

        #   throwsValue
        self.throwsValue = wx.StaticText(self.mainPanel, label="L")
        self.throwsValue.SetFont(infoFont)

        #   posValue
        self.posValue = wx.StaticText(self.mainPanel, label="P")
        self.posValue.SetFont(infoFont)

        #   nameValue
        self.nameValue = wx.StaticText(self.mainPanel, label="firstName lastName")
        self.nameValue.SetFont(priceFont)

        #   avgPtsValue
        self.avgPtsValue = wx.TextCtrl(self.mainPanel, value="12.0", style=wx.TE_READONLY)
        self.avgPtsValue.SetFont(pts2Font)
        self.avgPtsValue.SetMinSize((70,70))
        

        #   avgPctValue
        self.avgPctValue = wx.TextCtrl(self.mainPanel, value="-12.0%", style=wx.TE_READONLY)
        self.avgPctValue.SetFont(pts2Font)
        self.avgPctValue.SetMinSize((70,70))


        #   ptsPerValue
        self.ptsPerValue = wx.TextCtrl(self.mainPanel, value="12.0", style=wx.TE_READONLY)
        self.ptsPerValue.SetFont(pts3Font)
        self.ptsPerValue.SetMinSize((90,90))
        

        #   vsVsLabel
        vsVsLabel = wx.StaticText(self.mainPanel, label="VS.")
        vsVsLabel.SetFont(vsFont)

        #   vsValue
        self.vsVsValue = wx.StaticText(self.mainPanel, label="WSH")
        self.vsVsValue.SetFont(vsFont)

        #   vsCareer
        vsCareerLabel = wx.StaticText(self.mainPanel, label="Career")
        vsCareerLabel.SetFont(ptsFont)

        #   vsSeason
        vsSeasonLabel = wx.StaticText(self.mainPanel, label="Season")
        vsSeasonLabel.SetFont(ptsFont)

        #   vsteam
        vsTeamLabel = wx.StaticText(self.mainPanel, label="Team")
        vsTeamLabel.SetFont(ptsFont)

        #   vsIPLabel
        vsIPLabel = wx.StaticText(self.mainPanel, label="IP")
        vsIPLabel.SetFont(labelFont)

        #   vsIpValue
        self.vsIPCareerValue = wx.StaticText(self.mainPanel, label="0.0")
        self.vsIPCareerValue.SetFont(ptsFont)

        self.vsIPSeasonValue = wx.StaticText(self.mainPanel, label="0.0")
        self.vsIPSeasonValue.SetFont(ptsFont)

        self.vsIPTeamValue = wx.StaticText(self.mainPanel, label="0.0")
        self.vsIPTeamValue.SetFont(ptsFont)

        #   vsWLabel
        vsWLabel = wx.StaticText(self.mainPanel, label="W")
        vsWLabel.SetFont(labelFont)

        #   vsWValue
        self.vsWCareerValue = wx.StaticText(self.mainPanel, label="0")
        self.vsWCareerValue.SetFont(ptsFont)

        self.vsWSeasonValue = wx.StaticText(self.mainPanel, label="0")
        self.vsWSeasonValue.SetFont(ptsFont)

        self.vsWTeamValue = wx.StaticText(self.mainPanel, label="0")
        self.vsWTeamValue.SetFont(ptsFont)

        #   vsERALabel
        vsERALabel = wx.StaticText(self.mainPanel, label="ERA")
        vsERALabel.SetFont(labelFont)

        #   vsERAValue
        self.vsERACareerValue = wx.StaticText(self.mainPanel, label="0.0")
        self.vsERACareerValue.SetFont(ptsFont)

        self.vsERASeasonValue = wx.StaticText(self.mainPanel, label="0.0")
        self.vsERASeasonValue.SetFont(ptsFont)

        self.vsERATeamValue = wx.StaticText(self.mainPanel, label="0.0")
        self.vsERATeamValue.SetFont(ptsFont)

        #   vsWHIPLabel
        vsWHIPLabel = wx.StaticText(self.mainPanel, label="WHIP")
        vsWHIPLabel.SetFont(labelFont)

        #   vsWHIPValue
        self.vsWHIPCareerValue = wx.StaticText(self.mainPanel, label="0.0")
        self.vsWHIPCareerValue.SetFont(ptsFont)

        self.vsWHIPSeasonValue = wx.StaticText(self.mainPanel, label="0.0")
        self.vsWHIPSeasonValue.SetFont(ptsFont)

        self.vsWHIPTeamValue = wx.StaticText(self.mainPanel, label="0.0")
        self.vsWHIPTeamValue.SetFont(ptsFont)

        #   vsK9Label
        vsK9Label = wx.StaticText(self.mainPanel, label="K9")
        vsK9Label.SetFont(labelFont)

        #   vsWHIPValue
        self.vsK9CareerValue = wx.StaticText(self.mainPanel, label="0.0")
        self.vsK9CareerValue.SetFont(ptsFont)

        self.vsK9SeasonValue = wx.StaticText(self.mainPanel, label="0.0")
        self.vsK9SeasonValue.SetFont(ptsFont)

        self.vsK9TeamValue = wx.StaticText(self.mainPanel, label="0.0")
        self.vsK9TeamValue.SetFont(ptsFont)

        
        
        

        # Sizers
        self.playerSizer = wx.BoxSizer(wx.VERTICAL)

        #   in playerSizer
        self.mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.expandSizer = wx.BoxSizer(wx.VERTICAL)

        #   in mainSizer
        self.oppSizer = wx.BoxSizer(wx.VERTICAL)
        self.windowSizer = wx.BoxSizer(wx.VERTICAL)
        self.toggleSizer = wx.BoxSizer(wx.VERTICAL)
        
        #   in oppSizer
        self.oppLogoSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.oppDataSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.oppDataThrSizer = wx.BoxSizer(wx.HORIZONTAL)

        #   in windowSizer
        self.infoSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.infoPtsSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.vsSizer = wx.BoxSizer(wx.HORIZONTAL)

        #   in vsSizer
        self.vsStatsSizer = wx.GridSizer(4,6,5,5)
        
        # Add items
        #   Add items to vsStatsSizer
        self.vsStatsSizer.Add(wx.StaticText(self.mainPanel))
        self.vsStatsSizer.Add(vsIPLabel)
        self.vsStatsSizer.Add(vsWLabel)
        self.vsStatsSizer.Add(vsERALabel)
        self.vsStatsSizer.Add(vsWHIPLabel)
        self.vsStatsSizer.Add(vsK9Label)
        self.vsStatsSizer.Add(vsCareerLabel)
        self.vsStatsSizer.Add(self.vsIPCareerValue)
        self.vsStatsSizer.Add(self.vsWCareerValue)
        self.vsStatsSizer.Add(self.vsERACareerValue)
        self.vsStatsSizer.Add(self.vsWHIPCareerValue)
        self.vsStatsSizer.Add(self.vsK9CareerValue)
        self.vsStatsSizer.Add(vsSeasonLabel)
        self.vsStatsSizer.Add(self.vsIPSeasonValue)
        self.vsStatsSizer.Add(self.vsWSeasonValue)
        self.vsStatsSizer.Add(self.vsERASeasonValue)
        self.vsStatsSizer.Add(self.vsWHIPSeasonValue)
        self.vsStatsSizer.Add(self.vsK9SeasonValue)
        self.vsStatsSizer.Add(vsTeamLabel)
        self.vsStatsSizer.Add(self.vsIPTeamValue)
        self.vsStatsSizer.Add(self.vsWTeamValue)
        self.vsStatsSizer.Add(self.vsERATeamValue)
        self.vsStatsSizer.Add(self.vsWHIPTeamValue)
        self.vsStatsSizer.Add(self.vsK9TeamValue)

        #   Add items to vsSizer
        self.vsSizer.Add(vsVsLabel, 0, wx.ALIGN_CENTER)
        self.vsSizer.Add(self.vsVsValue, 0, wx.ALIGN_CENTER | wx.RIGHT, 25)
        self.vsSizer.Add(self.vsStatsSizer, 0, wx.ALIGN_CENTER)

        #   Add items to infoPtsSizer
        self.infoPtsSizer.Add(self.avgPtsValue, 0, wx.ALIGN_CENTER |  wx.RIGHT, 10)
        self.infoPtsSizer.Add(self.avgPctValue, 0, wx.ALIGN_CENTER | wx.RIGHT, 100)
        self.infoPtsSizer.Add(self.ptsPerValue, 0, wx.ALIGN_CENTER)
        
        #   Add items to infoSizer 
        self.infoSizer.Add(self.posValue, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.infoSizer.Add(self.nameValue, 0, wx.ALIGN_CENTER_HORIZONTAL |wx.LEFT | wx.RIGHT, 40)
        self.infoSizer.Add(self.throwsValue, 0, wx.ALIGN_CENTER_HORIZONTAL)

        #   Add items to toggleSizer
        self.toggleSizer.Add(self.toggleBttn, 0, wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, 20)

         #   Add items to oppLogoSizer
        self.oppLogoSizer.Add(oppVsLabel, 0, wx.ALIGN_CENTER | wx.RIGHT, 15)
        self.oppLogoSizer.Add(self.oppLogo)
        
        #   Add items to oppDataSizer
        self.oppDataSizer.Add(self.oppPtsValue, 0, wx.RIGHT, 15)

        self.oppDataSizer.Add(self.oppPctValue)

        #   Add items to oppDataThrSizer
        self.oppDataThrSizer.Add(self.oppPtsThrValue, 0, wx.RIGHT, 15)
        self.oppDataThrSizer.Add(self.oppPctThrValue)

        # Add items to oppSizer
        self.oppSizer.Add(self.priceValue, 0)
        self.oppSizer.Add(self.oppLogoSizer, 0, wx.TOP, 40)
        self.oppSizer.Add(oppPtsLabel, 0, wx.ALIGN_CENTER | wx.TOP, 25)
        self.oppSizer.Add(self.oppDataSizer, 0, wx.TOP, 5)
        self.oppSizer.Add(oppPtsThrLabel, 0, wx.ALIGN_CENTER | wx.TOP, 25)
        self.oppSizer.Add(self.oppDataThrSizer, 0, wx.TOP, 5)

        # Add items to windowSizer
        self.windowSizer.Add(self.infoSizer, 1, wx.ALIGN_CENTER)
        self.windowSizer.Add(self.infoPtsSizer, 1, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 20)
        self.windowSizer.Add(self.vsSizer, 1, wx.ALIGN_CENTER | wx.BOTTOM, 10)
        self.windowSizer.Add(self.expandBttn, 0)

        # Add items to mainSizer
        self.mainSizer.Add(self.oppSizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 20)
        self.mainSizer.Add(self.windowSizer, 1, wx.EXPAND | wx.BOTTOM, 10)
        self.mainSizer.Add(self.toggleSizer, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)

        # Add items to playerSizer
        self.playerSizer.Add(self.mainPanel, 1,  wx.TOP, 20)
        self.playerSizer.Add(self.expandPanel, 1, wx.EXPAND)

        

        # Set Sizer
        self.mainPanel.SetSizer(self.mainSizer)
        self.expandPanel.SetSizer(self.expandSizer)
        self.SetSizer(self.playerSizer)

        self.Layout()


    def onExpand(self, event):
        label = self.expandBttn.GetLabel()
        if label == "Expand":
            self.expandBttn.SetLabel("Hide")
            self.expandPanel.Show()
        else:
            self.expandBttn.SetLabel("Expand")
            self.expandPanel.Hide()
        self.Layout()




class BatterPanel(wx.Panel):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        
        # Panels
        self.mainPanel = wx.Panel(self)
        self.mainPanel.SetMinSize((850,300))
        self.mainPanel.SetMaxSize((850,300))
        self.expandPanel = wx.ScrolledWindow(self, style=wx.VSCROLL)
        self.expandPanel.SetScrollbars(20, 20, 50, 50)
        self.expandPanel.SetBackgroundColour(wx.GREEN)
        self.expandPanel.SetMinSize((850,300))
        self.expandPanel.Hide()
        

        # Fonts

        #   vsFont
        priceFont = wx.Font(20, wx.ROMAN, wx.NORMAL, wx.BOLD)
        infoFont = wx.Font(16, wx.ROMAN, wx.NORMAL, wx.NORMAL)
        vsFont = wx.Font(16, wx.SWISS, wx.NORMAL, wx.BOLD)
        ptsFont = wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD)
        pts2Font = wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD)
        pts3Font = wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD)
        labelFont = wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL)

        # Widgets

        #   expandBttn
        self.expandBttn = wx.Button(self.mainPanel, label="Expand")
        self.expandBttn.Bind(wx.EVT_BUTTON, self.onExpand)

        #   priceValue
        self.priceValue = wx.StaticText(self.mainPanel, label="$2000")
        self.priceValue.SetFont(priceFont)

        #   oppVsLabel
        oppVsLabel = wx.StaticText(self.mainPanel, label="VS.")
        oppVsLabel.SetFont(vsFont)

        #   oppLogo
        self.oppLogo = wx.StaticBitmap(self.mainPanel, size=(50,50))
        self.oppLogo.SetMinSize((50,50))
        self.oppLogo.SetBitmap(wx.Image("/home/ededub/FEFelson/MLBProjections/Teams/Logos/G20.png", wx.BITMAP_TYPE_ANY).Scale(50, 50, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap())

        #   oppPtsValue
        self.oppPtsValue = wx.TextCtrl(self.mainPanel, value="12.0", style=wx.TE_READONLY)
        self.oppPtsValue.SetFont(ptsFont)
        self.oppPtsValue.SetMaxSize((65,50))
        oppPtsLabel = wx.StaticText(self.mainPanel, label = "Bats vs SP")

        #   oppPctValue
        self.oppPctValue = wx.TextCtrl(self.mainPanel, value="-12.0%", style=wx.TE_READONLY)
        self.oppPctValue.SetFont(ptsFont)
        self.oppPctValue.SetMaxSize((65,50))

        #   oppPtsThrValue
        self.oppPtsThrValue = wx.TextCtrl(self.mainPanel, value="12.0", style=wx.TE_READONLY)
        self.oppPtsThrValue.SetFont(ptsFont)
        self.oppPtsThrValue.SetMaxSize((65,50))
        oppPtsThrLabel = wx.StaticText(self.mainPanel, label = "LHBs vs SP")

        #   oppPctThrValue
        self.oppPctThrValue = wx.TextCtrl(self.mainPanel, value="-12.0%", style=wx.TE_READONLY)
        self.oppPctThrValue.SetFont(ptsFont)
        self.oppPctThrValue.SetMaxSize((65,50))

        #   toggleBttn
        self.toggleBttn = SToggleButton(self.mainPanel, label="Add", size=(70,70))

        #   batsValue
        self.batsValue = wx.StaticText(self.mainPanel, label="L")
        self.batsValue.SetFont(infoFont)

        #   posValue
        self.posValue = wx.StaticText(self.mainPanel, label="2B,OF")
        self.posValue.SetFont(infoFont)

        #   nameValue
        self.nameValue = wx.StaticText(self.mainPanel, label="firstName lastName")
        self.nameValue.SetFont(priceFont)

        #   avgPtsValue
        self.avgPtsValue = wx.TextCtrl(self.mainPanel, value="12.0", style=wx.TE_READONLY)
        self.avgPtsValue.SetFont(pts2Font)
        self.avgPtsValue.SetMinSize((70,70))
        

        #   avgPctValue
        self.avgPctValue = wx.TextCtrl(self.mainPanel, value="-12.0%", style=wx.TE_READONLY)
        self.avgPctValue.SetFont(pts2Font)
        self.avgPctValue.SetMinSize((70,70))


        #   ptsPerValue
        self.ptsPerValue = wx.TextCtrl(self.mainPanel, value="12.0", style=wx.TE_READONLY)
        self.ptsPerValue.SetFont(pts3Font)
        self.ptsPerValue.SetMinSize((90,90))
        

        #   vsVsLabel
        vsVsLabel = wx.StaticText(self.mainPanel, label="VS.")
        vsVsLabel.SetFont(vsFont)

        #   vsValue
        self.vsVsValue = wx.StaticText(self.mainPanel, label="WSH")
        self.vsVsValue.SetFont(vsFont)

        #   vsCareer
        vsCareerLabel = wx.StaticText(self.mainPanel, label="Career")
        vsCareerLabel.SetFont(ptsFont)

        #   vsSeason
        vsSeasonLabel = wx.StaticText(self.mainPanel, label="Season")
        vsSeasonLabel.SetFont(ptsFont)

        #   vsSP
        vsSPLabel = wx.StaticText(self.mainPanel, label="SP")
        vsSPLabel.SetFont(ptsFont)

        #   vsABLabel
        vsABLabel = wx.StaticText(self.mainPanel, label="AB")
        vsABLabel.SetFont(labelFont)

        #   vsABValue
        self.vsABCareerValue = wx.StaticText(self.mainPanel, label="0")
        self.vsABCareerValue.SetFont(ptsFont)

        self.vsABSeasonValue = wx.StaticText(self.mainPanel, label="0")
        self.vsABSeasonValue.SetFont(ptsFont)

        self.vsABSPValue = wx.StaticText(self.mainPanel, label="0")
        self.vsABSPValue.SetFont(ptsFont)

        #   vsBALabel
        vsBALabel = wx.StaticText(self.mainPanel, label="AVG")
        vsBALabel.SetFont(labelFont)

        #   vsBAValue
        self.vsBACareerValue = wx.StaticText(self.mainPanel, label="0.000")
        self.vsBACareerValue.SetFont(ptsFont)

        self.vsBASeasonValue = wx.StaticText(self.mainPanel, label="0.000")
        self.vsBASeasonValue.SetFont(ptsFont)

        self.vsBASPValue = wx.StaticText(self.mainPanel, label="0.000")
        self.vsBASPValue.SetFont(ptsFont)

        #   vsSlugLabel
        vsSlugLabel = wx.StaticText(self.mainPanel, label="SLUG")
        vsSlugLabel.SetFont(labelFont)

        #   vsSlugValue
        self.vsSlugCareerValue = wx.StaticText(self.mainPanel, label="0.000")
        self.vsSlugCareerValue.SetFont(ptsFont)

        self.vsSlugSeasonValue = wx.StaticText(self.mainPanel, label="0.000")
        self.vsSlugSeasonValue.SetFont(ptsFont)

        self.vsSlugSPValue = wx.StaticText(self.mainPanel, label="0.000")
        self.vsSlugSPValue.SetFont(ptsFont)

        #   vsHRLabel
        vsHRLabel = wx.StaticText(self.mainPanel, label="HR")
        vsHRLabel.SetFont(labelFont)

        #   vsHRValue
        self.vsHRCareerValue = wx.StaticText(self.mainPanel, label="0.0")
        self.vsHRCareerValue.SetFont(ptsFont)

        self.vsHRSeasonValue = wx.StaticText(self.mainPanel, label="0.0")
        self.vsHRSeasonValue.SetFont(ptsFont)

        self.vsHRSPValue = wx.StaticText(self.mainPanel, label="0.0")
        self.vsHRSPValue.SetFont(ptsFont)

    
        
        
        

        # Sizers
        self.playerSizer = wx.BoxSizer(wx.VERTICAL)

        #   in playerSizer
        self.mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.expandSizer = wx.BoxSizer(wx.VERTICAL)

        #   in mainSizer
        self.oppSizer = wx.BoxSizer(wx.VERTICAL)
        self.windowSizer = wx.BoxSizer(wx.VERTICAL)
        self.toggleSizer = wx.BoxSizer(wx.VERTICAL)
        
        #   in oppSizer
        self.oppLogoSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.oppDataSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.oppDataThrSizer = wx.BoxSizer(wx.HORIZONTAL)

        #   in windowSizer
        self.infoSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.infoPtsSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.vsSizer = wx.BoxSizer(wx.HORIZONTAL)

        #   in vsSizer
        self.vsStatsSizer = wx.GridSizer(4,5,5,5)
        
        # Add items
        #   Add items to vsStatsSizer
        self.vsStatsSizer.Add(wx.StaticText(self.mainPanel))
        self.vsStatsSizer.Add(vsABLabel)
        self.vsStatsSizer.Add(vsBALabel)
        self.vsStatsSizer.Add(vsSlugLabel)
        self.vsStatsSizer.Add(vsHRLabel)
        self.vsStatsSizer.Add(vsCareerLabel)
        self.vsStatsSizer.Add(self.vsABCareerValue)
        self.vsStatsSizer.Add(self.vsBACareerValue)
        self.vsStatsSizer.Add(self.vsSlugCareerValue)
        self.vsStatsSizer.Add(self.vsHRCareerValue)
        self.vsStatsSizer.Add(vsSeasonLabel)
        self.vsStatsSizer.Add(self.vsABSeasonValue)
        self.vsStatsSizer.Add(self.vsBASeasonValue)
        self.vsStatsSizer.Add(self.vsSlugSeasonValue)
        self.vsStatsSizer.Add(self.vsHRSeasonValue)
        self.vsStatsSizer.Add(vsSPLabel)
        self.vsStatsSizer.Add(self.vsABSPValue)
        self.vsStatsSizer.Add(self.vsBASPValue)
        self.vsStatsSizer.Add(self.vsSlugSPValue)
        self.vsStatsSizer.Add(self.vsHRSPValue)

        #   Add items to vsSizer
        self.vsSizer.Add(vsVsLabel, 0, wx.ALIGN_CENTER)
        self.vsSizer.Add(self.vsVsValue, 0, wx.ALIGN_CENTER | wx.RIGHT, 25)
        self.vsSizer.Add(self.vsStatsSizer, 0, wx.ALIGN_CENTER)

        #   Add items to infoPtsSizer
        self.infoPtsSizer.Add(self.avgPtsValue, 0, wx.ALIGN_CENTER |  wx.RIGHT, 10)
        self.infoPtsSizer.Add(self.avgPctValue, 0, wx.ALIGN_CENTER | wx.RIGHT, 100)
        self.infoPtsSizer.Add(self.ptsPerValue, 0, wx.ALIGN_CENTER)
        
        #   Add items to infoSizer 
        self.infoSizer.Add(self.posValue, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.infoSizer.Add(self.nameValue, 0, wx.ALIGN_CENTER_HORIZONTAL |wx.LEFT | wx.RIGHT, 40)
        self.infoSizer.Add(self.batsValue, 0, wx.ALIGN_CENTER_HORIZONTAL)

        #   Add items to toggleSizer
        self.toggleSizer.Add(self.toggleBttn, 0, wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, 20)

         #   Add items to oppLogoSizer
        self.oppLogoSizer.Add(oppVsLabel, 0, wx.ALIGN_CENTER | wx.RIGHT, 15)
        self.oppLogoSizer.Add(self.oppLogo)
        
        #   Add items to oppDataSizer
        self.oppDataSizer.Add(self.oppPtsValue, 0, wx.RIGHT, 15)

        self.oppDataSizer.Add(self.oppPctValue)

        #   Add items to oppDataThrSizer
        self.oppDataThrSizer.Add(self.oppPtsThrValue, 0, wx.RIGHT, 15)
        self.oppDataThrSizer.Add(self.oppPctThrValue)

        # Add items to oppSizer
        self.oppSizer.Add(self.priceValue, 0)
        self.oppSizer.Add(self.oppLogoSizer, 0, wx.TOP, 40)
        self.oppSizer.Add(oppPtsLabel, 0, wx.ALIGN_CENTER | wx.TOP, 25)
        self.oppSizer.Add(self.oppDataSizer, 0, wx.TOP, 5)
        self.oppSizer.Add(oppPtsThrLabel, 0, wx.ALIGN_CENTER | wx.TOP, 25)
        self.oppSizer.Add(self.oppDataThrSizer, 0, wx.TOP, 5)

        # Add items to windowSizer
        self.windowSizer.Add(self.infoSizer, 1, wx.ALIGN_CENTER)
        self.windowSizer.Add(self.infoPtsSizer, 1, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 20)
        self.windowSizer.Add(self.vsSizer, 1, wx.ALIGN_CENTER | wx.BOTTOM, 10)
        self.windowSizer.Add(self.expandBttn, 0)

        # Add items to mainSizer
        self.mainSizer.Add(self.oppSizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 20)
        self.mainSizer.Add(self.windowSizer, 1, wx.EXPAND | wx.BOTTOM, 10)
        self.mainSizer.Add(self.toggleSizer, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)

        # Add items to playerSizer
        self.playerSizer.Add(self.mainPanel, 1,  wx.TOP, 20)
        self.playerSizer.Add(self.expandPanel, 1, wx.EXPAND)

        

        # Set Sizer
        self.mainPanel.SetSizer(self.mainSizer)
        self.expandPanel.SetSizer(self.expandSizer)
        self.SetSizer(self.playerSizer)

        self.Layout()


    def onExpand(self, event):
        label = self.expandBttn.GetLabel()
        if label == "Expand":
            self.expandBttn.SetLabel("Hide")
            self.expandPanel.Show()
        else:
            self.expandBttn.SetLabel("Expand")
            self.expandPanel.Hide()
        self.Layout()
        

