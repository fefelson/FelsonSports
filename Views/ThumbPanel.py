import datetime
import wx

from FelsonSports import Environ as ENV

from pprint import pprint

logoPath = ENV.logoPath

class ThumbPanel(wx.Panel):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, size=(120,120), style=wx.BORDER_SIMPLE, *args, **kwargs)
        self.SetMaxSize((120,120))

        self.SetBackgroundColour(wx.Colour("WHITE"))

        gdFont = wx.Font(wx.FontInfo(6))
        baseFont = wx.Font(wx.FontInfo(8))
        abrvFont = wx.Font(wx.FontInfo(11))

        self.abrvs = {}
        self.logos = {}
        self.values = {}

        self.gameDate = wx.StaticText(self)
        self.gameDate.SetFont(gdFont)

        self.gameTime = wx.StaticText(self)
        self.gameTime.SetFont(gdFont)

        self.spread = wx.StaticText(self)
        self.spread.SetFont(baseFont)

        self.ou = wx.StaticText(self)
        self.ou.SetFont(baseFont)

        lineSizers = {}

        for hA in ("away", "home"):
            abrv = wx.StaticText(self)
            abrv.SetFont(abrvFont)
            self.abrvs[hA] = abrv

            value = wx.StaticText(self)
            value.SetFont(baseFont)
            self.values[hA] = value

            logo = wx.StaticBitmap(self)
            self.logos[hA] = logo

            teamSizer = wx.BoxSizer()
            teamSizer.Add(logo, 1, wx.EXPAND | wx.BOTTOM, 5)
            teamSizer.Add(abrv, 1, wx.EXPAND)

            lineSizer = wx.BoxSizer()
            lineSizer.Add(teamSizer, 1, wx.EXPAND)
            lineSizer.Add(value, 0, wx.LEFT | wx.RIGHT, 8)

            lineSizers[hA] = lineSizer

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.gameDate, 0, wx.CENTER | wx.TOP, 5)
        sizer.Add(self.gameTime, 0, wx.CENTER | wx.BOTTOM, 7)
        sizer.Add(lineSizers["away"], 1, wx.EXPAND)
        sizer.Add(lineSizers["home"], 1, wx.EXPAND)
        sizer.Add(self.spread, 0, wx.CENTER | wx.TOP, 3)
        sizer.Add(self.ou, 0, wx.CENTER)

        self.SetSizer(sizer)


    def setPanel(self, game=None):

        winFont = wx.Font(wx.FontInfo(12).Bold())
        baseFont = wx.Font(wx.FontInfo(8).Bold())

        try:
            odds = game["odds"][-1]["101"]
        except:
            odds = {}

        gameId = str(game["gameId"])
        gd = datetime.datetime.strptime(game["gameTime"], "%a, %d %b %Y %H:%M:%S %z") - datetime.timedelta(hours=5)

        self.gameDate.SetName("{}".format(gameId))
        self.gameDate.SetLabel(gd.strftime("%a %b %d"))

        self.gameTime.SetName("{}".format(gameId))
        self.gameTime.SetLabel(gd.strftime("%I:%M %p"))

        try:
            sp = "+"+str(odds["home_spread"]) if float(odds["home_spread"]) > 0 else str(odds["home_spread"])
        except (ValueError, KeyError):
            sp = -100
        self.spread.SetName("{}".format(gameId))
        self.spread.SetLabel("{}  {}".format(game["teams"]["home"]["abrv"], sp))

        self.ou.SetName("{}".format(gameId))

        try:
            self.ou.SetLabel("{:.1f}".format(float(odds["total"])))
        except:
            self.ou.SetLabel("0")


        for hA in ("away", "home"):

            self.abrvs[hA].SetName("{}".format(gameId))
            self.abrvs[hA].SetLabel(game["teams"][hA]["abrv"])

            self.logos[hA].SetName("{}".format(gameId))
            try:
                logo = wx.Image(logoPath.format(game["leagueId"], game["{}Id".format(hA)]), wx.BITMAP_TYPE_PNG).Scale(22, 22, wx.IMAGE_QUALITY_HIGH)
            except:
                logo = wx.Image(logoPath.format(game["leagueId"], -1), wx.BITMAP_TYPE_PNG).Scale(22, 22, wx.IMAGE_QUALITY_HIGH)

            logo = logo.ConvertToBitmap()
            self.logos[hA].SetBitmap(logo)

            self.values[hA].SetName("{}".format(gameId))
            try:
                mL = str(odds["{}_ml".format(hA)])
                self.values[hA].SetLabel("+"+mL if int(mL) > 0 else mL)
            except (ValueError, KeyError):
                self.values[hA].SetLabel("0")


        self.Layout()


    def bind(self, cmd):
        self.Bind(wx.EVT_LEFT_DCLICK, cmd)
        for item in (*self.abrvs.values(), *self.logos.values(), *self.values.values(), self.spread,
                        self.ou, self.gameDate, self.gameTime):
            item.Bind(wx.EVT_LEFT_DCLICK, cmd)



class ListPanel(wx.ScrolledWindow):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, size=((150,500)), *args, **kwargs)
        self.SetScrollbars(20, 20, 50, 50)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)


    def addGame(self, game, bindCmd):
        thumbPanel = ThumbPanel(self)
        thumbPanel.setPanel(game)
        thumbPanel.bind(bindCmd)
        self.sizer.Add(thumbPanel, 0, wx.ALL, 10)
