import wx
from pprint import pprint


class TitlePanel(wx.Panel):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.teamName = wx.StaticText(self)
        self.teamName.SetFont(wx.Font(20, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL,
                                        wx.FONTWEIGHT_BOLD))
        self.teamName.SetBackgroundColour(wx.Colour("GREY"))
        self.teamName.SetForegroundColour(wx.BLACK)

        self.homeAwayTag = wx.StaticText(self)
        self.homeAwayTag.SetForegroundColour(wx.WHITE)

        self.b2bTag = wx.StaticText(self, label="B2B")
        self.b2bTag.SetForegroundColour(wx.WHITE)
        self.b2bTag.SetBackgroundColour(wx.RED)
        self.b2bTag.Hide()

        tagSizer = wx.BoxSizer()
        tagSizer.Add(self.homeAwayTag, 0, wx.RIGHT, 5)
        tagSizer.Add(self.b2bTag, 0)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.teamName, 0, wx.CENTER | wx.TOP | wx.BOTTOM, 10)
        sizer.Add(tagSizer, 0, wx.GROW | wx.TOP | wx.LEFT, 10)

        self.SetSizer(sizer)


    def setPanel(self, team):
        teamInfo = team.getInfo()
        pprint(teamInfo)
        self.b2bTag.Hide()
        self.teamName.SetLabel(" ".join((teamInfo["city"], teamInfo["mascot"])))
        self.SetBackgroundColour(wx.Colour(teamInfo["colors"][0]))
        haValue = "Home" if teamInfo["hA"] == "home" else "Away"
        haColor = wx.GREEN if teamInfo["hA"] == "home" else wx.BLUE
        self.homeAwayTag.SetLabel(haValue)
        self.homeAwayTag.SetBackgroundColour(haColor)

        if teamInfo["b2b"]:
            self.b2bTag.Show()
        self.Layout()
