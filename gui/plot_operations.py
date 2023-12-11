import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from db_operations import DBOperations

class PlotOperations:
    '''Class to perform plotting operations on the weather data stored in the SQLite database'''
    def __init__(self):
        '''Initialize the database path'''
        self.db_operations = DBOperations()

    def plot_box(self, start_year, end_year):
        '''Plot a box plot of the monthly temperature distribution for the range of years'''
        # Fetch monthly data from the database
        monthly_data = self.db_operations.fetch_monthly_data(start_year, end_year)
        # Prepare data for box plot
        data_to_plot = [temps for temps in monthly_data.values() if temps]
        months = [str(month) for month in range(1, 13)]

        # Create boxplot
        plt.figure(figsize=(10, 6))
        plt.boxplot(data_to_plot, labels=months)
        plt.title(f'Monthly Temperature Distribution for: {start_year} to {end_year}')
        plt.xlabel('Month')
        plt.ylabel('Temperature (°C)')
        plt.grid(True)
        plt.show()
    
    def plot_line(self, month, year):
        '''Plot a line graph of the daily average temperatures for the specified month and year'''
        # Fetch daily data from the database
        dates, temps = self.db_operations.fetch_daily_data(month, year)
        #print(dates)
        
        # Convert string dates to datetime objects
        dates = [datetime.strptime(date, '%Y-%m-%d') for date in dates]
        
        # Create line plot
        plt.figure(figsize=(10, 6))
        plt.plot(dates, temps, marker='o', linestyle='-', color='blue')

        # Format the x-axis to show dates properly
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator())
        plt.gcf().autofmt_xdate()  # Rotation

        plt.title(f'Daily Avg Temperatures for {month}/{year}')
        plt.xlabel('Day of Month')
        plt.ylabel('Avg Daily Temp (°C)')
        plt.grid(True)
        plt.tight_layout()
        plt.show()



# plot_ops = PlotOperations('weather_project.sqlite')
# #plot_ops.plot_box(2000, 2020)
# plot_ops.plot_line(1, 2020)
