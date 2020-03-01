import wx

from ..GamePanels import ThumbPanel as TP

class GamesTickerPanel(wx.ScrolledWindow):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.bindCmd = None
        self.SetMinSize((-1,140))
        self.SetMaxSize((-1,140))
        self.SetScrollbars(20, 20, 50, 50)

        self.thumbSizer = wx.BoxSizer()
        self.SetSizer(self.thumbSizer)



    def setPanel(self, games):
        self.DestroyChildren()
        self.thumbSizer.Clear()

        #add all games panel
        default = TP.ThumbPanel(self)
        default.bind(self.bindCmd)
        self.thumbSizer.Add(default, 1, wx.LEFT, 5)
        for game in games:
            tp = TP.ThumbPanel(self)
            self.thumbSizer.Add(tp, 1, wx.LEFT, 5)
            tp.setPanel(game)
            tp.bind(self.bindCmd)
        self.Layout()


    def setBindCmd(self, cmd):
        self.bindCmd = cmd
