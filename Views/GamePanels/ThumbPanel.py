import datetime
import os
import wx

from pprint import pprint

logoPath = os.environ["HOME"] + "/Yahoo/{}/teams/{}.png"

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

        if game:
            gameId = str(game.getId())
            gd = datetime.datetime.strptime(game.getInfo("gameTime"), "%a, %d %b %Y %H:%M:%S %z") - datetime.timedelta(hours=5)

            self.gameDate.SetName(gameId)
            self.gameDate.SetLabel(gd.strftime("%a %b %d"))

            self.gameTime.SetName(gameId)
            self.gameTime.SetLabel(gd.strftime("%I:%M %p"))

            try:
                sp = "+"+str(game.getOdds("home_spread")) if float(game.getOdds("home_spread")) > 0 else str(game.getOdds("home_spread"))
            except (ValueError, KeyError):
                sp = -100
            self.spread.SetName(gameId)
            self.spread.SetLabel("{}  {}".format(game.getTeam("home").getInfo("abrv"), sp))

            self.ou.SetName(gameId)

            try:
                self.ou.SetLabel("{:.1f}".format(game.getOdds("ou")))
            except KeyError:
                self.ou.SetLabel("0")


            for hA in ("away", "home"):
                team = game.getTeam(hA)

                self.abrvs[hA].SetName(gameId)
                self.abrvs[hA].SetLabel(team.getInfo("abrv"))

                self.logos[hA].SetName(gameId)
                logo = wx.Image(logoPath.format(game.getInfo("league"), team.getId()), wx.BITMAP_TYPE_PNG).Scale(22, 22, wx.IMAGE_QUALITY_HIGH)
                logo = logo.ConvertToBitmap()
                self.logos[hA].SetBitmap(logo)

                self.values[hA].SetName(gameId)

                if game.hasPlayed:

                    self.spread.SetFont(baseFont)
                    self.ou.SetFont(baseFont)

                    self.values[hA].SetLabel(str(game.getTeamStats(hA,"pts")))

                    if int(game.getTeamStats("home","pts")) > int(game.getTeamStats("away","pts")):
                        color = wx.BLACK
                        self.abrvs["home"].SetFont(winFont)
                        self.values["home"].SetFont(winFont)
                        self.abrvs["home"].SetForegroundColour(wx.Colour(color))
                        self.values["home"].SetForegroundColour(wx.Colour(color))


                    else:
                        color = wx.BLACK
                        self.abrvs["away"].SetFont(winFont)
                        self.values["away"].SetFont(winFont)
                        self.abrvs["away"].SetForegroundColour(wx.Colour(color))
                        self.values["away"].SetForegroundColour(wx.Colour(color))


                    try:
                        if game.getOdds("homeSpreadOutcome") > 0:
                            self.spread.SetForegroundColour(wx.Colour("DARK GREEN"))
                        else:
                            self.spread.SetForegroundColour(wx.BLUE)

                        if game.getOdds("ouOutcome") > 0:
                            self.ou.SetForegroundColour(wx.Colour("DARK GREEN"))
                        else:
                            self.ou.SetForegroundColour(wx.BLUE)
                    except KeyError:
                        pass

                # game has not been played yet
                else:

                    try:
                        mL = str(game.getOdds("{}_ml".format(hA)))
                        self.values[hA].SetLabel("+"+mL if int(mL) > 0 else mL)
                    except (ValueError, KeyError):
                        self.values[hA].SetLabel("0")


        else:
            self.abrvs["away"].SetLabel("ALL")
            self.values["away"].SetLabel("")

            self.abrvs["home"].SetLabel("GAMES")
            self.values["home"].SetLabel("")

        self.Layout()


    def bind(self, cmd):
        self.Bind(wx.EVT_LEFT_DCLICK, cmd)
        for item in (*self.abrvs.values(), *self.logos.values(), *self.values.values(), self.spread,
                        self.ou, self.gameDate, self.gameTime):
            item.Bind(wx.EVT_LEFT_DCLICK, cmd)
