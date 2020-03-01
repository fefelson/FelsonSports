import wx
import os

logoPath = os.environ["HOME"] + "/Yahoo/nba/teams/{}.png"


class OddsPanel(wx.Panel):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.SetMaxSize((-1,100))

        abrvFont = wx.Font(wx.FontInfo(15).Bold())
        spreadFont = wx.Font(wx.FontInfo(12).Bold())


        self.awayLogo = wx.StaticBitmap(self)

        self.awayAbrv = wx.StaticText(self)
        self.awayAbrv.SetFont(abrvFont)

        self.awaySpread = wx.StaticText(self)
        self.awaySpread.SetFont(spreadFont)

        self.awayMoney = wx.StaticText(self)
        self.awayMoney.SetFont(spreadFont)

        self.homeLogo = wx.StaticBitmap(self)
        self.homeAbrv = wx.StaticText(self)
        self.homeAbrv.SetFont(abrvFont)

        self.homeSpread = wx.StaticText(self)
        self.homeSpread.SetFont(spreadFont)

        self.homeMoney = wx.StaticText(self)
        self.homeMoney.SetFont(spreadFont)

        self.ou = wx.StaticText(self)
        self.ou.SetFont(spreadFont)


        lineSizer = wx.GridSizer(2,4,(5,5))

        lineSizer.Add(self.awayLogo)
        lineSizer.Add(self.awayAbrv)
        lineSizer.Add(self.awaySpread)
        lineSizer.Add(self.awayMoney)

        lineSizer.Add(self.homeLogo)
        lineSizer.Add(self.homeAbrv)
        lineSizer.Add(self.homeSpread)
        lineSizer.Add(self.homeMoney)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(lineSizer, 1, wx.EXPAND)
        sizer.Add(self.ou, 0, wx.CENTER | wx.TOP, 15)

        self.SetSizer(sizer)


    def setPanel(self, game):
        away = game.getTeam("away")
        home = game.getTeam("home")

        aSP = "+"+str(game.getOdds("awaySpread")) if float(game.getOdds("awaySpread")) > 0 else str(game.getOdds("awaySpread"))
        hSP = "+"+str(game.getOdds("homeSpread")) if float(game.getOdds("homeSpread")) > 0 else str(game.getOdds("homeSpread"))
        aML = "+"+str(game.getOdds("awayMoney")) if float(game.getOdds("awayMoney")) > 0 else str(game.getOdds("awayMoney"))
        hML = "+"+str(game.getOdds("homeMoney")) if float(game.getOdds("homeMoney")) > 0 else str(game.getOdds("homeMoney"))

        awayLogo = wx.Image(logoPath.format(away.getId()), wx.BITMAP_TYPE_PNG).Scale(30, 30, wx.IMAGE_QUALITY_HIGH)
        awayLogo = awayLogo.ConvertToBitmap()

        homeLogo = wx.Image(logoPath.format(home.getId()), wx.BITMAP_TYPE_PNG).Scale(30, 30, wx.IMAGE_QUALITY_HIGH)
        homeLogo = homeLogo.ConvertToBitmap()

        self.awayLogo.SetBitmap(awayLogo)
        self.awayAbrv.SetLabel(away.getInfo("abrv"))
        self.awaySpread.SetLabel(aSP)
        self.awayMoney.SetLabel(aML)

        self.homeLogo.SetBitmap(homeLogo)
        self.homeAbrv.SetLabel(home.getInfo("abrv"))
        self.homeSpread.SetLabel(hSP)
        self.homeMoney.SetLabel(hML)

        self.ou.SetLabel(str(game.getOdds("ou")))

        if game.hasPlayed:
            if game.getOdds("awaySpreadOutcome") > 0:
                self.awaySpread.SetForegroundColour(wx.Colour("DARK GREEN"))
                self.homeSpread.SetForegroundColour(wx.RED)
            elif game.getOdds("awaySpreadOutcome") < 0:
                self.awaySpread.SetForegroundColour(wx.RED)
                self.homeSpread.SetForegroundColour(wx.Colour("DARK GREEN"))
            else:
                self.awaySpread.SetForegroundColour(wx.BLACK)
                self.homeSpread.SetForegroundColour(wx.BLACK)

            if game.getOdds("awayMoneyOutcome") > 0:
                self.awayMoney.SetForegroundColour(wx.Colour("DARK GREEN"))
                self.homeMoney.SetForegroundColour(wx.RED)
            elif game.getOdds("awayMoneyOutcome") < 0:
                self.awayMoney.SetForegroundColour(wx.RED)
                self.homeMoney.SetForegroundColour(wx.Colour("DARK GREEN"))
            else:
                self.awayMoney.SetForegroundColour(wx.BLACK)
                self.homeMoney.SetForegroundColour(wx.BLACK)

            if game.getOdds("ouOutcome") > 0:
                self.ou.SetForegroundColour(wx.Colour("DARK GREEN"))
            elif game.getOdds("ouOutcome") < 0:
                self.ou.SetForegroundColour(wx.RED)
            else:
                self.ou.SetForegroundColour(wx.BLACK)


        self.Layout()
