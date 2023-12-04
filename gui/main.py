import wx

from gui.main_view import MainView

# Next, create an application object.
app = wx.App()

# Then a frame.
frm = MainView()

# Show it.
frm.Show()

# Start the event loop.
app.MainLoop()