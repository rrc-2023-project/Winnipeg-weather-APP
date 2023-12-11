import wx
import threading
from db_operations import DBOperations
from datetime import datetime
from plot_operations import PlotOperations
import weather_data_operation
from weather_data_operation import WeatherData
from dbcm import DBCM



class WeatherProcessor(wx.Frame):
    """Main application frame for the Weather Processor."""

    def __init__(self, parent=None, id=wx.ID_ANY, title="Weather Processing App", 
                 pos=wx.DefaultPosition, size=(400, 450), style=wx.DEFAULT_FRAME_STYLE):
        super().__init__(parent, id, title, pos, size, style)
        
        # Database operations
        self.db_operations = DBOperations()  # Uncomment when DBOperations is implemented
        # Plot operations
        self.plot_operations = PlotOperations()
        # Weather data operations
        self.weather_data = WeatherData()
        
        self.Bind(weather_data_operation.EVT_UPDATE_EVENT, self.on_update_event)
        
        # Setup UI
        self.setup_ui()
        self.Show()
        
    def on_update_event(self, event):
        """Handle update events from the weather data operations."""
        self.SetStatusText(event.message)

    def setup_ui(self):
        """Set up the user interface."""
        panel = wx.Panel(self)

        # Main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Download and Update Buttons
        self.download_data_button = wx.Button(panel, label="Download Weather Data")
        self.download_data_button.Bind(wx.EVT_BUTTON, self.on_download_data)

        # Year Range Input for Box Plot
        self.start_year_label = wx.StaticText(panel, label="Start Year for Box Plot:")
        self.start_year_text = wx.TextCtrl(panel)
        self.end_year_label = wx.StaticText(panel, label="End Year for Box Plot:")
        self.end_year_text = wx.TextCtrl(panel)
        self.generate_box_button = wx.Button(panel, label="Generate Box Plot")
        self.generate_box_button.Bind(wx.EVT_BUTTON, self.on_generate_box_plot)

        # Month and Year Input for Line Plot
        self.month_label = wx.StaticText(panel, label="Month for Line Plot:")
        self.month_text = wx.TextCtrl(panel)
        self.year_label = wx.StaticText(panel, label="Year for Line Plot:")
        self.year_text = wx.TextCtrl(panel)
        self.generate_line_button = wx.Button(panel, label="Generate Line Plot")
        self.generate_line_button.Bind(wx.EVT_BUTTON, self.on_generate_line_plot)

        # Adding widgets to sizer
        main_sizer.Add(self.download_data_button, 0, wx.ALL | wx.EXPAND, 5)
        main_sizer.Add(self.start_year_label, 0, wx.ALL, 5)
        main_sizer.Add(self.start_year_text, 0, wx.ALL | wx.EXPAND, 5)
        main_sizer.Add(self.end_year_label, 0, wx.ALL, 5)
        main_sizer.Add(self.end_year_text, 0, wx.ALL | wx.EXPAND, 5)
        main_sizer.Add(self.generate_box_button, 0, wx.ALL | wx.EXPAND, 5)
        main_sizer.Add(self.month_label, 0, wx.ALL, 5)
        main_sizer.Add(self.month_text, 0, wx.ALL | wx.EXPAND, 5)
        main_sizer.Add(self.year_label, 0, wx.ALL, 5)
        main_sizer.Add(self.year_text, 0, wx.ALL | wx.EXPAND, 5)
        main_sizer.Add(self.generate_line_button, 0, wx.ALL | wx.EXPAND, 5)


        # Set main sizer
        panel.SetSizer(main_sizer)
        self.CreateStatusBar()
    
    def on_download_data(self, event):
        """Handle full data download."""
        def download_thread():
            self.weather_data.load_data(self)  # Calling load_data from WeatherData
        # Run the download in a separate thread to prevent UI blocking
        threading.Thread(target=download_thread).start()
        
           
    def on_generate_box_plot(self, event):
        """Generate a box plot based on the entered year range."""
        start_year = self.start_year_text.GetValue()
        end_year = self.end_year_text.GetValue()
        # Validate and parse the year range then call the box plot function
        try:
            start_year = int(start_year)
            end_year = int(end_year)
            self.plot_operations.plot_box(start_year,end_year)  
            self.SetStatusText(f"Generating box plot for years {start_year}-{end_year}...")
        except ValueError:
            wx.MessageBox("Please enter valid start and end years.", "Error", wx.OK | wx.ICON_ERROR)
        

    def on_generate_line_plot(self, event):
        """Generate a line plot based on the entered month and year."""
        month = self.month_text.GetValue()
        year = self.year_text.GetValue()
        # Validate and parse the month and year then call the line plot function
        try:
            month = int(month)
            year = int(year)
            self.plot_operations.plot_line(month, year)  
            self.SetStatusText(f"Generating line plot for {month}/{year}...")
        except ValueError:
            wx.MessageBox("Please enter a valid month and year.", "Error", wx.OK | wx.ICON_ERROR)

    
    # Other methods for managing data download and update operations would go here.

def main():
    '''Main function to launch the application.'''
    app = wx.App(False)
    frame = WeatherProcessor()
    app.MainLoop()

if __name__ == '__main__':
    '''Main entry point for the application.'''
    main()

