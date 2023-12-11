from scrape_weather import WeatherScraper
import requests
import threading
# date convert to url 
import datetime
from urllib.parse import urlparse, urlencode, quote_plus, parse_qs
# db
from db_operations import DBOperations
from dbcm import DBCM
# event
import wx
import wx.lib.newevent

# event
UpdateEvent, EVT_UPDATE_EVENT = wx.lib.newevent.NewEvent()

class WeatherData:
    '''Weather Data class to get the weather data from the internet and store it in the database.'''
    base = 'https://climate.weather.gc.ca/climate_data/daily_data_e.html?StationID=27174&timeframe=2&Day=1'
    
    def __init__(self, db_name="weather_project.sqlite"):
        '''Initialize the start and end years, and the database connection'''
        self.db_name = db_name
        self.now = datetime.datetime.now()
        self.start_year = self.now.year
        self.end_year = 0
        self.end_month = 0
        self.db = DBOperations()

        self.thread = []
        
    def url(self, year, month):
        '''Return the URL for the specified year and month'''
        base_data = urlparse(self.base)
        base_query = parse_qs(base_data.query)
        base_query['Year'] = [year]
        base_query['Month'] = [month]
        base_query['StartYear'] = [year-1]
        base_query['EndYear'] = [year]
        new_query = urlencode(base_query, doseq=True)
        return f"{base_data.scheme}://{base_data.netloc}{base_data.path}?{new_query}"
    
    def insert_data(self, year, month, data):
        '''Insert the weather data into the database'''
        for day in data:
            self.db.save_data(year, month, day['day'], day['detail']['Max'], day['detail']['Min'], day['detail']['Mean'])



    def deal_month_data(self, year, month, retry=0):
        '''Get the weather data for the specified year and month'''
        url = self.url(year, month)
        weather_parser = WeatherScraper()
        print(f"get data ===> year: {year}, month: {month}")
        try:
            with requests.get(url, timeout=50) as response:
                weather_parser.feed(response.content.decode('utf-8'))
            self.insert_data(year, month, weather_parser.month)
        except Exception as e:
            if retry < 3:
                print(f"retry {retry} ===> year: {year}, month: {month}")
                return self.deal_month_data(year, month, retry+1)
            return False
        return weather_parser.is_before_month


    def deal_year_data(self, year):
        '''Get the weather data for the specified year'''
        #month 12 to 1
        start_month = 12
        stop_month = 0
        
        # check if start year is current year
        if year == self.now.year:
            start_month = self.now.month
            # check if end month is existed
            if self.end_month > 0:
                stop_month = self.end_month - 1
        for month in range(start_month, stop_month, -1):
            is_before_month = self.deal_month_data(year, month)
            if not is_before_month:
                self.end_year = year
                break
            
    def load_data(self, frame):
        '''Load the weather data from the internet and store it in the database'''
        # check db data is not empty 
        with DBCM(self.db_name) as cursor:
            wx.PostEvent(frame, UpdateEvent(message="Check database..."))
            cursor.execute('SELECT COUNT(*) FROM weather_daily')
            count = cursor.fetchone()[0]
            if count > 0:
                cursor.execute('SELECT MAX(year) FROM weather_daily')
                self.end_year = cursor.fetchone()[0]
                print(f"database latest year: {self.end_year}")
                # get the latest month within the year
                cursor.execute('SELECT MAX(month) FROM weather_daily WHERE year = ?', (self.end_year,))
                self.end_month = cursor.fetchone()[0]

        self.get_data(frame)
        wx.PostEvent(frame, UpdateEvent(message="Done!"))
                
                
        
    def get_data(self, frame):
        '''Get the latest weather data from the internet and store it in the database by threading, limit to 8, and wait for all threads to finish, then get the next set of data'''
        # threading count
        threading_count = 8

        # check if start year between end year less than threading count
        if self.start_year - threading_count < self.end_year:
            threading_count = self.start_year - self.end_year + 1
        # notify status
        wx.PostEvent(frame, UpdateEvent(message=f"Getting the latest date by {threading_count} threads: {self.start_year} to {self.start_year-threading_count}..."))
        # get date from now to last year multiple thread limit to 8
        for year in range(self.start_year, self.start_year-threading_count, -1):
            t = threading.Thread(target=self.deal_year_data, args=(year,))
            self.thread.append(t)
            t.start()

        self.wait_deal()

        self.start_year = self.start_year-threading_count
        if self.start_year > self.end_year:
            self.get_data(frame)


            
    def wait_deal(self):
        '''Wait for all threads to finish'''
        for t in self.thread:
            t.join()





if __name__ == '__main__':
    '''Main function to load the weather data'''
    weather_data = WeatherData()
    weather_data.load_data()