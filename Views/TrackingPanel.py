import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar2Wx
import wx

from pprint import pprint

class NCAABTrackingPanel(wx.Panel):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.figure = Figure()
        self.axes = self.figure.subplots(2,1)
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.toolbar = NavigationToolbar2Wx(self.canvas)
        self.toolbar.Realize()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
        self.SetSizer(sizer)
        self.Fit()


    def setPanel(self, info):

        for i, value in enumerate([info[hA] for hA in ("away", "home")]):

            name = value["name"]
            data = value["data"]
            num = [x for x in range(len(data))]
            colors = []
            for mO in value["money"]:
                if mO == 1:
                    colors.append("green")
                else:
                    colors.append("red")

            twoWeek = [sum(data[(i-5):i])/5 for i in range(5,len(data)+1)]
            oneMonth = [sum(data[(i-13):i])/13 for i in range(13,len(data)+1)]


            self.axes[i].clear()
            self.axes[i].bar(num, data, color=colors)
            self.axes[i].grid(True)
            self.axes[i].axis([0, 40, -20, 20])
            self.axes[i].plot([i for i in range(5,len(data)+1)], twoWeek, color="blue")
            self.axes[i].plot([i for i in range(13,len(data)+1)], oneMonth, color="orange")

        self.canvas.draw()
        self.canvas.Refresh()


class NBATrackingPanel(wx.Panel):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.figure = Figure()
        self.axes = self.figure.subplots(2,1)
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.toolbar = NavigationToolbar2Wx(self.canvas)
        self.toolbar.Realize()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
        self.SetSizer(sizer)
        self.Fit()


    def setPanel(self, info):

        for i, value in enumerate([info[hA] for hA in ("away", "home")]):

            name = value["name"]
            data = value["data"]
            num = [x for x in range(len(data))]
            colors = []
            for mO in value["money"]:
                if mO == 1:
                    colors.append("green")
                else:
                    colors.append("red")

            twoWeek = [sum(data[(i-7):i])/7 for i in range(7,len(data)+1)]
            oneMonth = [sum(data[(i-26):i])/26 for i in range(26,len(data)+1)]


            self.axes[i].clear()
            self.axes[i].bar(num, data, color=colors)
            self.axes[i].grid(True)
            self.axes[i].axis([40, 82, -20, 20])
            self.axes[i].plot([i for i in range(7,len(data)+1)], twoWeek, color="blue")
            self.axes[i].plot([i for i in range(26,len(data)+1)], oneMonth, color="orange")

        self.canvas.draw()
        self.canvas.Refresh()
