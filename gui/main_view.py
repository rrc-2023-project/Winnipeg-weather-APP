"""Main view."""
import threading

import wx
import weather


class MainView(wx.Frame):
    """UI class."""

    def __init__(self):
        # ensure the parent's __init__ is called
        super().__init__(None, title="Weather Processing APP", size=(1600, 900))
         # create a panel in the frame
        self.db = weather.WeatherDB()
        panel = wx.Panel(self)

        # show main title
        self.main_title = wx.StaticText(panel, label="Main View Loading...")
        font = self.main_title.GetFont()
        font.PointSize += 10
        font = font.Bold()
        self.main_title.SetFont(font)

        # and create a sizer to manage the layout of child widgets
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.main_title, flag=wx.ALL, border=5)

        date_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # from year
        # from_label = wx.StaticText(panel, label="From:")
        # self.from_year = wx.ComboBox(self, choices=[], style=wx.CB_READONLY)
        #
        # date_sizer.Add(from_label, flag=wx.Right, border=8)
        # date_sizer.Add(self.from_year, proportion=1, flag=wx.Right, border=8)
        #
        # # to year
        # to_label = wx.StaticText(panel, label="To:")
        # self.to_year = wx.ComboBox(self, choices=[], style=wx.CB_READONLY)
        #
        # date_sizer.Add(to_label, 0, flag=wx.ALL, border=8)
        # date_sizer.Add(self.to_year, proportion=1, flag=wx.Right, border=8)
        #
        # # add date sizer to main sizer
        # main_sizer.Add(date_sizer, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)

        # and a status bar
        self.CreateStatusBar()
        # bind event to status bar
        self.Bind(weather.EVT_UPDATE_EVENT, self.on_update)

        # add sizer to panel
        panel.SetSizer(main_sizer)
        # create a menu bar
        self.makeMenuBar()
        # get data by weather data class
        self.get_date()



    def on_update(self, event):
        """Update event."""
        self.SetStatusText(event.message)


    def get_date(self):
        """Get the lastest date from database."""
        self.SetStatusText("Gettting the lastest date from internet...")
        weather_data = weather.WeatherData()
        weather_data.load_data(self)
        self.SetStatusText("Get the lastest date from internet done")
        self.main_title.Label = "Main View"

        # get data from database
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT year FROM weather_daily ORDER BY year DESC')
            years = cursor.fetchall()
            years = [str(year[0]) for year in years]
            # self.from_year.SetItems(years)
            # self.to_year.SetItems(years)




    def year_select_change(self, event):
        # get data from database
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT month FROM weather_daily WHERE year = ? ORDER BY month DESC', (self.year_select.Value,))
            months = cursor.fetchall()
            months = [str(month[0]) for month in months]
            self.month_select.SetItems(months)

    def month_select_change(self, event):
        year = self.year_select.Value
        month = self.month_select.Value

        print(f"year: {year}, month: {month}")


    def makeMenuBar(self):
        """
        A menu bar is composed of menus, which are composed of menu items.
        This method builds a set of menus and binds handlers to be called
        when the menu item is selected.
        """

        # Make a file menu with Hello and Exit items
        fileMenu = wx.Menu()
        # The "\t..." syntax defines an accelerator key that also triggers
        # the same event
        helloItem = fileMenu.Append(-1, "&Hello...\tCtrl-H",
                "Help string shown in status bar for this menu item")
        fileMenu.AppendSeparator()
        # When using a stock ID we don't need to specify the menu item's
        # label
        exitItem = fileMenu.Append(wx.ID_EXIT)

        # Now a help menu for the about item
        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT)

        # Make the menu bar and add the two menus to it. The '&' defines
        # that the next letter is the "mnemonic" for the menu item. On the
        # platforms that support it those letters are underlined and can be
        # triggered from the keyboard.
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(helpMenu, "&Help")

        # Give the menu bar to the frame
        self.SetMenuBar(menuBar)

        # Finally, associate a handler function with the EVT_MENU event for
        # each of the menu items. That means that when that menu item is
        # activated then the associated handler function will be called.
        self.Bind(wx.EVT_MENU, self.OnHello, helloItem)
        self.Bind(wx.EVT_MENU, self.OnExit,  exitItem)
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)


    def OnExit(self, event):
        """Close the frame, terminating the application."""
        self.Close(True)


    def OnHello(self, event):
        """Say hello to the user."""
        wx.MessageBox("Hello again from wxPython")


    def OnAbout(self, event):
        """Display an About Dialog"""
        wx.MessageBox("This is a wxPython Hello World sample",
                      "About Hello World 2",
                      wx.OK|wx.ICON_INFORMATION)

    def calc(self, first_name: str, last_name: str) -> str:
        """Perform some string maneuvers."""
        try:
            result = f"{last_name[::2]}, {first_name[::-1]}"
        except Exception as e:
            print(f"UI::calc::{e}")
        return result

    def cmdSave_click(self, event):
        """Save click event."""
        try:
            first = self.txtFirstName.Value
            last = self.txtLastName.Value
            result = self.calc(first, last)
            self.lblResult.Label = f"Mangled the names: {result}"
        except Exception as e:
            print(f"UI::cmdSave_click::{e}")
