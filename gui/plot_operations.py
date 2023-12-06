import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sqlite3
from datetime import datetime

class PlotOperations:
    '''Class to perform plotting operations on the weather data stored in the SQLite database'''
    def __init__(self, database_path):
        self.database_path = database_path

    def fetch_monthly_data(self, start_year, end_year):
        '''Fetch monthly data from the database for the range of years'''
        # Connect to the SQLite database
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()
            
            # Query to select daily temperatures between the specified years
            cursor.execute('''
                SELECT month, day, Mean
                FROM weather_daily
                WHERE year BETWEEN ? AND ?
                ORDER BY month, day;
            ''', (start_year, end_year))
        
            # Fetch all results
            results = cursor.fetchall()
        
        # Organize data into a dictionary with months as keys and lists of daily temperatures as values
        monthly_data = {month: [] for month in range(1, 13)}
        for month, day, temp in results:
            monthly_data[month].append(temp)
        
        return monthly_data

    def plot_box(self, start_year, end_year):
        '''Plot a boxplot of the monthly temperature distribution for the range of years'''
        # Fetch monthly data from the database
        monthly_data = self.fetch_monthly_data(start_year, end_year)
        # Prepare data for boxplot
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

    def fetch_daily_data(self, month, year):
        # Connect to the SQLite database
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()
            # Query to select daily temperatures for a specific month and year
            cursor.execute('''
                SELECT year, month, day, Mean
                FROM weather_daily
                WHERE year = ? AND month = ?
                ORDER BY day;
            ''', (year, month))
            
            # Fetch all results
            results = cursor.fetchall()

        # Initialize lists for dates and temperatures
        dates = []
        temps = []

        # Process results and populate the dates and temps lists
        for row_year, row_month, day, mean_temp in results:
            if row_year == year and row_month == month:
                # Create a date object from year, month, and day
                date = datetime(row_year, row_month, day)
                # Append the date and temperature to their respective lists
                dates.append(date.strftime('%Y-%m-%d'))  # Formats the date as 'year-month-day'
                #print(dates)
                temps.append(mean_temp)
        
        return dates, temps

    
    def plot_line(self, month, year):
        # Fetch daily data from the database
        dates, temps = self.fetch_daily_data(month, year)
        print(dates)
        
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
