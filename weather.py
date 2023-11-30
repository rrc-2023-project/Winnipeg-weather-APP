# web parser
from html.parser import HTMLParser
import requests
import threading
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
        self.now = datetime.datetime.now()
        self.start_year = self.now.year
        self.end_year = 0
        self.end_month = 0
        self.db = WeatherDB()

        self.thread = []
        
    def url(self, year, month):
        base_data = urlparse(self.base)
        base_query = parse_qs(base_data.query)
        base_query['Year'] = [year]
        base_query['Month'] = [month]
        base_query['StartYear'] = [year-1]
        base_query['EndYear'] = [year]
        new_query = urlencode(base_query, doseq=True)
        return f"{base_data.scheme}://{base_data.netloc}{base_data.path}?{new_query}"
    
    def insert_data(self, year, month, data):
        for day in data:
            self.db.insert(year, month, day['day'], day['detail']['Max'], day['detail']['Min'], day['detail']['Mean'])



    def deal_month_data(self, year, month, retry=0):
        url = self.url(year, month)
        weather_parser = WeatherParser()
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
        #month 12 to 1
        start_month = 12
        stop_month = 0
        
        # check if start year is current year
        if year == self.now.year:
            start_month = self.now.month
            # check if end month is exist
            if self.end_month > 0:
                stop_month = self.end_month - 1
        for month in range(start_month, stop_month, -1):
            is_before_month = self.deal_month_data(year, month)
            if not is_before_month:
                self.end_year = year
                break
            
    def load_data(self):
        # chech db data is not empty 
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM weather_daily')
            count = cursor.fetchone()[0]
            if count > 0:
                cursor.execute('SELECT MAX(year) FROM weather_daily')
                self.end_year = cursor.fetchone()[0]
                print(f"database lastest year: {self.end_year}")
                # get the lastest month within the year
                cursor.execute('SELECT MAX(month) FROM weather_daily WHERE year = ?', (self.end_year,))
                self.end_month = cursor.fetchone()[0]

        self.get_data()
                
                
        
    def get_data(self):
        # threading count
        threading_count = 8
        # check if start year bwteen end year less than threading count
        if self.start_year - threading_count < self.end_year:
            threading_count = self.start_year - self.end_year + 1
        # get date from now to last year multiple thread limit to 8
        for year in range(self.start_year, self.start_year-threading_count, -1):
            t = threading.Thread(target=self.deal_year_data, args=(year,))
            self.thread.append(t)
            t.start()

        self.wait_deal()

        self.start_year = self.start_year-threading_count
        if self.start_year > self.end_year:
            self.get_data()


            
    def wait_deal(self):
        for t in self.thread:
            t.join()




if __name__ == '__main__':
    weather_data = WeatherData()
    weather_data.load_data()

