import wx

from views.main import MainView

# Next, create an application object.
app = wx.App()

# Then a frame.
frm = MainView(None, title="Weather Processing APP")

# Show it.
frm.Show()

# Start the event loop.
app.MainLoop()