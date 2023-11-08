# web parser
from html.parser import HTMLParser
import requests

# date convert to url 
import datetime
from urllib.parse import urlparse, urlencode, quote_plus, parse_qs

#db
import sqlite3
from contextlib import contextmanager

def is_float(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

class WeatherDB:
    
    def __init__(self, db_name="weather_project.sqlite"):
        # Connect to the SQLite database
        self.db_name = db_name
        
        # Create the table if it doesn't exist
        with self.get_connection() as conn:
            conn.cursor().execute('''
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
            conn.cursor().execute("CREATE UNIQUE INDEX IF NOT EXISTS weather_daily_index ON weather_daily (year, month, day);")
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        try:
            yield conn
        finally:
            conn.close()
            
    def insert(self, year, month, day, Max, Min, Mean):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT OR IGNORE INTO weather_daily (year, month, day, Max, Min, Mean) VALUES (?, ?, ?, ?, ?, ?)', (year, month, day, Max, Min, Mean))
                           
            conn.commit()
            
            

class WeatherParser(HTMLParser):
    def __init__(self, *, convert_charrefs=True):
        super().__init__(convert_charrefs=convert_charrefs)
        self.table = False
        self.tr = False
        self.abbr = False
        self.td = False
        # next month or before month
        self.li = False
        self.is_next_month = False
        self.is_before_month = False
        
        self.next_month = ''
        self.before_month = ''
        
        self.day = ''
        self.day_detail = []
        self.month = []
        
        
    def handle_starttag(self, tag, attrs):
        # print("Start tag:", tag)
        if tag == 'tbody':
            self.table = True
        if tag == 'tr':
            self.tr = True
        if tag == 'abbr':
            self.abbr = True
        if tag == 'td':
            self.td = True

        if tag == 'li':
            for attr in attrs:
                if attr[0] == 'class' and attr[1] == 'previous':
                    self.li = True
                    self.is_before_month = True
        
        if tag == 'a' and self.li:
            herf = ''
            for attr in attrs:
                if attr[0] == 'href':
                    herf = attr[1]
                if self.is_before_month:
                    self.before_month = herf
        
        
        
            
        # for attr in attrs:
        #     print(" attr:", attr)
    def handle_endtag(self, tag):
        if tag == 'tbody':
            self.table = False
        if tag == 'tr':
            self.tr = False
        if tag == 'abbr':
            self.abbr = False
        if tag == 'td':
            self.td = False 
        if tag == 'li':
            self.li = False
        
    
    
    def handle_data(self, data):        
        if self.table and self.tr:
            if self.abbr:
                if self.day != data: 
                    if len(self.day_detail) > 0:
                        #  {“Max”: 12.0, “Min”: 5.6, “Mean”: 7.1}
                        if is_float(self.day_detail[0]) and is_float(self.day_detail[1]) and is_float(self.day_detail[2]):
                            day_data = {'Max': float(self.day_detail[0]), 'Min': float(self.day_detail[1]), 'Mean': float(self.day_detail[2])}
                            self.month.append({'day': int(self.day), 'detail': day_data})
                            self.day_detail = []
                    self.day = data
                    
                
            if self.td and self.day.isdigit():
                self.day_detail.append(data)
                

class WeatherData:
    
    base = 'https://climate.weather.gc.ca/climate_data/daily_data_e.html?StationID=27174&timeframe=2&Day=1'
    
    def __init__(self):
        
        now = datetime.datetime.now()
        self.year = now.year
        self.month = now.month
        self.weather_parser = WeatherParser()
        self.db = WeatherDB()
        
    def url(self):
        base_data = urlparse(self.base)
        base_query = parse_qs(base_data.query)
        base_query['Year'] = [self.year]
        base_query['Month'] = [self.month]
        base_query['StartYear'] = [self.year-1]
        base_query['EndYear'] = [self.year]
        new_query = urlencode(base_query, doseq=True)
        return f"{base_data.scheme}://{base_data.netloc}{base_data.path}?{new_query}"
    
    
    def dealPath(self, path):
        path_query = parse_qs(urlparse(path).query)
        # print(path_query)
        self.year = int(path_query['Year'][0])
        self.month = int(path_query['Month'][0])
        
    def get_data(self):
        # print(self.url())
        self.weather_parser = WeatherParser()
        with requests.get(self.url()) as response:
            self.weather_parser.feed(response.content.decode('utf-8'))
        
        for day in self.weather_parser.month:
            #print(day)
            self.db.insert(self.year, self.month, day['day'], day['detail']['Max'], day['detail']['Min'], day['detail']['Mean'])
                
        print(f"year: {self.year}, month: {self.month}")
        if (self.weather_parser.is_before_month):
            self.dealPath(self.weather_parser.before_month)
            self.get_data()
            
            




if __name__ == '__main__':
    weather_data = WeatherData()
    weather_data.get_data()