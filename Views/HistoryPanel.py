import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar2Wx
import wx

from pprint import pprint

class HistoryPanel(wx.Panel):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.figure = Figure()
        self.axes = self.figure.subplots(1,2)
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.toolbar = NavigationToolbar2Wx(self.canvas)
        self.toolbar.Realize()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
        self.SetSizer(sizer)
        self.Fit()


    def setPanel(self, info):

        spread = info["spread"]
        overUnder = info["overUnder"]

        self.axes[0].clear()

        n, bins, patches = self.axes[0].hist(spread["spreadBoxes"],len(spread["spreadCount"].keys()))

        for item,patch in zip(bins,patches):
            if item < 0 and item < -1*spread["i"] :
                patch.set_facecolor("red")
            elif item > -1*spread["i"] and item <0:
                patch.set_facecolor("orange")
            elif item > 0 and item < -1*spread["i"]:
                patch.set_facecolor("orange")
            elif item > -1*spread["i"]:
                patch.set_facecolor("green")



        self.axes[0].scatter((spread["i"]*-1),20, color="orange")

        self.axes[0].text(bins[0]+5, 20, "total {}".format(len(spread["spreadResults"])), ha='left')
        self.axes[0].text(bins[0]+5, 18, "ats win {:2d}%".format(int((spread["wins"]/len(spread["spreadOutcome"]))*100)), ha='left')
        self.axes[0].text(bins[0]+5, 17, "ats loss {:2d}%".format(int((spread["loss"]/len(spread["spreadOutcome"]))*100)), ha='left')
        self.axes[0].text(bins[0]+5, 16, "push {:2d}%".format(int((spread["push"]/len(spread["spreadOutcome"]))*100)), ha='left')
        self.axes[0].text(bins[0]+5, 14, "win% {:2d}%".format(int((spread["m"]/len(spread["spreadOutcome"]))*100)), ha='left')
        # self.axes[0].title("Home "+spread["spread"])


        self.axes[1].clear()
        n, bins, patches = self.axes[1].hist(overUnder["ouBoxes"],len(overUnder["ouCount"].keys()))

        for item,patch in zip(bins,patches):
            if item < overUnder["ou"] :
                patch.set_facecolor("red")
            elif item > overUnder["ou"]:
                patch.set_facecolor("green")

        self.axes[1].scatter((overUnder["ou"]),20, color="orange")

        self.axes[1].text(bins[0]+5, 20, "total {}".format(len(overUnder["ouResults"])), ha='left')
        self.axes[1].text(bins[0]+5, 18, "overs {:2d}%".format(int((overUnder["overs"]/len(overUnder["ouOutcome"]))*100)), ha='left')
        self.axes[1].text(bins[0]+5, 17, "unders {:2d}%".format(int((overUnder["unders"]/len(overUnder["ouOutcome"]))*100)), ha='left')
        self.axes[1].text(bins[0]+5, 16, "push {:2d}%".format(int((overUnder["ouPush"]/len(overUnder["ouOutcome"]))*100)), ha='left')
        # self.axes[1].title("O/U "+str(overUnder["ou"]))

        self.canvas.draw()
        self.canvas.Refresh()
