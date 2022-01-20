import wx

from .. import Environ as ENV
from pprint import pprint


awayHome = ("away", "home")



class GameLogPanel(wx.ScrolledWindow):

    _list = ("hA", "oppId", "teamPts", "oppPts", "spread", "money", "ou", "spreadOutcome", "moneyOutcome", "ovOutcome")

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, size=((150,500)), *args, **kwargs)
        self.SetScrollbars(20, 20, 50, 50)

        mainSizer = wx.BoxSizer()
        self.teamSizers = {}

        for hA in awayHome:

            self.teamSizers[hA] = wx.BoxSizer(wx.VERTICAL)
            mainSizer.Add(self.teamSizers[hA], 1, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(mainSizer)


    def addGame(self, hA, game):

        ptsFont = wx.Font(wx.FontInfo(10).Bold())
        spreadFont = wx.Font(wx.FontInfo(12).Bold())
        ouFont = wx.Font(wx.FontInfo(8).Bold())

        # pprint(game)

        backColor = wx.WHITE if game["hA"] == 1 else wx.Colour("KHAKI")
        moneyColor = wx.Colour("GREEN") if game["moneyOutcome"] == 1 else wx.Colour("RED")
        spreadColor = wx.Colour("BLACK")
        ouColor = wx.Colour("BLACK")
        if game["spreadOutcome"] > 0:
            spreadColor = wx.Colour("GREEN")
        elif game["spreadOutcome"] < 0:
            spreadColor = wx.Colour("RED")

        if game["ovOutcome"] > 0:
            ouColor = wx.Colour("GREEN")
        elif game["ovOutcome"] < 0:
            ouColor = wx.Colour("RED")

        panel = wx.Panel(self)
        panel.SetBackgroundColour(backColor)

        gameDate = wx.StaticText(panel, label=str(game["gameDate"]))
        gameDate.SetFont(ouFont)

        logo = wx.StaticBitmap(panel)
        try:
            img = wx.Image(ENV.logoPath.format(game["leagueId"], game["oppId"]), wx.BITMAP_TYPE_PNG).Scale(35, 35, wx.IMAGE_QUALITY_HIGH)
        except:
            img = wx.Image(ENV.logoPath.format(game["leagueId"], -1), wx.BITMAP_TYPE_PNG).Scale(35, 35, wx.IMAGE_QUALITY_HIGH)
        img = img.ConvertToBitmap()
        logo.SetBitmap(img)

        teamPts = wx.StaticText(panel, label=str(game["teamPts"]))
        oppPts = wx.StaticText(panel, label=str(game["oppPts"]))
        for item in (teamPts, oppPts):
            item.SetFont(ptsFont)

        spLabel = str(game["spread"]) if float(game["spread"]) < 0 else "+"+str(game["spread"])
        try:
            monLabel = str(game["money"]) if float(game["money"]) < 0 else "+"+str(game["money"])
        except:
            monLabel = ""


        spread = wx.StaticText(panel, label=spLabel)
        spread.SetForegroundColour(spreadColor)

        money = wx.StaticText(panel, label=monLabel)
        money.SetForegroundColour(moneyColor)

        for item in (spread, money):
            item.SetFont(spreadFont)

        ou = wx.StaticText(panel, label=str(game["ou"]))
        ou.SetForegroundColour(ouColor)
        ou.SetFont(ouFont)

        sizer = wx.BoxSizer()
        sizer.Add(gameDate, 0, wx.CENTER | wx.RIGHT, 25)
        sizer.Add(teamPts, 0, wx.RIGHT, 15)
        sizer.Add(logo, wx.RIGHT, 15)
        sizer.Add(oppPts, wx.RIGHT, 15)
        sizer.Add(spread, wx.RIGHT, 15)
        sizer.Add(money, wx.RIGHT, 15)
        sizer.Add(ou, wx.RIGHT, 15)

        panel.SetSizer(sizer)
        self.teamSizers[hA].Add(panel, 0, wx.EXPAND | wx.ALL, 20)
