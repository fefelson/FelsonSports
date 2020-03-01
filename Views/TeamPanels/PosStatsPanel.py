import wx


class PosStatsPanel(wx.Panel):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.comboBox = wx.ComboBox(self, value="PG", choices=("PG", "SG", "G", "GF", "SF", "PF", "F", "FC", "C"))

        self.minsPg = wx.StaticText(self)
        self.minsPct = wx.StaticText(self)

        self.ptsPg = wx.StaticText(self)
        self.ptsPct = wx.StaticText(self)

        self.rebPg = wx.StaticText(self)
        self.rebPct = wx.StaticText(self)

        self.astPg = wx.StaticText(self)
        self.astPct = wx.StaticText(self)

        self.stlPg = wx.StaticText(self)
        self.stlPct = wx.StaticText(self)

        self.blkPg = wx.StaticText(self)
        self.blkPct = wx.StaticText(self)

        gridSizer = wx.GridSizer(3, 6, (5,5))
        gridSizer.Add(wx.StaticText(self, label="mins"))
        gridSizer.Add(wx.StaticText(self, label="pts"))
        gridSizer.Add(wx.StaticText(self, label="reb"))
        gridSizer.Add(wx.StaticText(self, label="ast"))
        gridSizer.Add(wx.StaticText(self, label="stl"))
        gridSizer.Add(wx.StaticText(self, label="blk"))

        gridSizer.Add(self.minsPg)
        gridSizer.Add(self.ptsPg)
        gridSizer.Add(self.rebPg)
        gridSizer.Add(self.astPg)
        gridSizer.Add(self.stlPg)
        gridSizer.Add(self.blkPg)

        gridSizer.Add(self.minsPct)
        gridSizer.Add(self.ptsPct)
        gridSizer.Add(self.rebPct)
        gridSizer.Add(self.astPct)
        gridSizer.Add(self.stlPct)
        gridSizer.Add(self.blkPct)



        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.comboBox)
        sizer.Add(gridSizer)



        self.SetSizer(sizer)
