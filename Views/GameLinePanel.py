import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar2Wx
import wx

from pprint import pprint

class GameLinePanel(wx.Panel):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.toolbar = NavigationToolbar2Wx(self.canvas)
        self.toolbar.Realize()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
        self.SetSizer(sizer)
        self.Fit()


    def setPanel(self, game):
        allLines = {"99":[], "101":[]}

        for odds in game["odds"]:
            if len(odds.keys()):
                try:
                    allLines["99"].append(odds["99"])
                except KeyError:
                    pass
                try:
                    allLines["101"].append(odds["101"])
                except KeyError:
                    pass




        postLines = []

        lastSpread = 0
        for g in allLines["99"]:
            try:
                temp = float(g["home_spread"])
                postLines.append(temp)
                lastSpread = temp
            except (KeyError, TypeError, ValueError):
                postLines.append(lastSpread)

        self.axes.clear()
        self.axes.plot(range(len(postLines)), postLines)
        self.canvas.draw()
        self.canvas.Refresh()
