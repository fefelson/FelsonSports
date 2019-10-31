import wx




###############################################################################








###############################################################################


class MatchupView(wx.Panel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.awayTeamName = wx.StaticText(self, label="Away Team")
        self.homeTeamName = wx.StaticText(self, label="Home Team")
        self.awayLogo = wx.StaticBitmap(self)
        self.homeLogo = wx.StaticBitmap(self)

        vsText = wx.StaticText(self, label="vs")

        self.homeMoneyLine = wx.StaticText(self, label="Home Money")
        self.awayMoneyLine = wx.StaticText(self, label="Away Money")
        self.pointsLine = wx.StaticText(self, label="Points Line")
        self.overUnder = wx.StaticText(self, label="Over/Under")

        self.mainSizer = wx.BoxSizer(wx.VERTICAL)

        self.awaySizer = wx.BoxSizer()
        self.awaySizer.Add(self.awayLogo, 0)
        self.awaySizer.Add(self.awayTeamName, 1, wx.EXPAND)

        self.homeSizer = wx.BoxSizer()
        self.homeSizer.Add(self.homeTeamName, 1, wx.EXPAND)
        self.homeSizer.Add(self.homeLogo, 0)

        self.moneySizer = wx.BoxSizer()
        self.moneySizer.Add(self.homeMoneyLine)
        self.moneySizer.Add(self.awayMoneyLine)


        self.mainSizer.Add(self.awaySizer,1)
        self.mainSizer.Add(vsText)
        self.mainSizer.Add(self.homeSizer,1)
        self.mainSizer.Add(self.moneySizer)
        self.mainSizer.Add(self.pointsLine)
        self.mainSizer.Add(self.overUnder)

        self.SetSizer(self.mainSizer)
        
        







###############################################################################


if __name__ == "__main__":

    app = wx.App()
    frame = wx.Frame(None)
    panel = MatchupView(parent=frame)
    frame.Show()
    app.MainLoop()
