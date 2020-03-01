import os
import wx






class ShotChart(wx.Panel):

    def __init__(self, parent, hA, *args, **kwargs):
        super().__init__(parent, size=(400,376), *args, **kwargs)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnBackground)

        largeFont = wx.Font(10, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL,
                                    wx.FONTWEIGHT_NORMAL)

        smallFont = wx.Font(7, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL,
                                    wx.FONTWEIGHT_NORMAL)


        self.hA = hA

        sizer = wx.GridSizer(5, 2, 7)

        self.mainBoxes = {}
        self.secondBoxes = {}

        for i in range(1,11):
            shotSizer = wx.BoxSizer(wx.VERTICAL)
            mBox = wx.StaticText(self, style=wx.ALIGN_CENTRE_HORIZONTAL, label = "0%")
            mBox.SetFont(largeFont)
            sBox = wx.StaticText(self, style=wx.ALIGN_CENTRE_HORIZONTAL, label = "0%")
            sBox.SetFont(smallFont)
            shotSizer.Add(mBox, 0, wx.CENTER, wx.TOP, 20)
            shotSizer.Add(sBox, 0, wx.CENTER)
            sizer.Add(shotSizer, 1, wx.EXPAND)

            self.mainBoxes[i] = mBox
            self.secondBoxes[i] = sBox


        self.SetSizer(sizer)


    def OnBackground(self, evt):
        dc = evt.GetDC()
        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)
        dc.Clear()
        bmp = wx.Bitmap(os.environ["HOME"]+"/Downloads/halfcourt.png")
        dc.DrawBitmap(bmp, 0, 0)


class TeamShotsPanel(wx.Panel):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.optionBox = wx.ComboBox(self, choices=("fg", "pts"))
        self.optionBox.SetSelection(0)

        self.awayChart = ShotChart(self, "away")
        self.homeChart = ShotChart(self, "home")

        sizer = wx.BoxSizer(wx.VERTICAL)



        sizer.Add(self.optionBox)

        chartSizer = wx.BoxSizer()
        chartSizer.Add(self.awayChart, 1, wx.EXPAND | wx.ALL, 25)
        chartSizer.Add(self.homeChart, 1, wx.EXPAND | wx.ALL, 25)

        sizer.Add(chartSizer, 1, wx.EXPAND)

        self.SetSizer(sizer)
