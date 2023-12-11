#db
from dbcm import DBCM
from datetime import datetime

class DBOperations:
    '''Class to perform database operations on the weather data stored in the SQLite database'''
    def __init__(self, db_name="weather_project.sqlite"):
        '''Initialize the database name'''
        # Connect to the SQLite database
        self.db_name = db_name
        self.initialize_db()
    
    def initialize_db(self):
        '''Initialize the database'''
        # Create the table if it doesn't exist
        with DBCM(self.db_name) as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS weather_daily (
                    id INTEGER PRIMARY KEY,
                    year INTEGER,
                    month INTEGER,
                    day INTEGER,
                    Max REAL,
                    Min REAL,
                    Mean REAL
                );
            ''')
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS weather_daily_index ON weather_daily (year, month, day);")
           
    
            
    def save_data(self, year, month, day, Max, Min, Mean):
        '''Save the weather data to the database'''
        with DBCM(self.db_name) as cursor:
            cursor.execute('INSERT OR IGNORE INTO weather_daily (year, month, day, Max, Min, Mean) VALUES (?, ?, ?, ?, ?, ?)', (year, month, day, Max, Min, Mean))
                           
            
    def fetch_monthly_data(self, start_year, end_year):
        '''Fetch monthly data from the database for the range of years for the boxplot'''
        # Connect to the SQLite database
        with DBCM(self.db_name) as cursor:
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
    
    def fetch_daily_data(self, month, year):
        '''Fetch daily data from the database for the specified month and year for the line plot'''
        # Connect to the SQLite database
        with DBCM(self.db_name) as cursor:
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
    
    def purge_data(self):
        '''Purge all data from the database'''
        with DBCM(self.db_name) as cursor:
            cursor.execute('DELETE FROM weather_data') 
            


 