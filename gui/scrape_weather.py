# web parser
from html.parser import HTMLParser

def is_float(num):
    '''check if the string is float'''
    try:
        float(num)
        return True
    except ValueError:
        return False

class WeatherScraper(HTMLParser):
    '''Weather Scraper class to parse the weather data from the HTML page,  and store it in a dictionary.'''
    def __init__(self, *, convert_charrefs=True):
        '''Initialize the parser and the dictionary'''
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
        '''Handle the start of a tag'''
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
        '''Handle the end of a tag'''
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
        '''Handle the text within a tag'''      
        if self.table and self.tr:
            if self.abbr:
                if self.day != data: 
                    if len(self.day_detail) > 0:
                        #  {“Max”: 12.0, “Min”: 5.6, “Mean”: 7.1}
                        if is_float(self.day_detail[0]) and is_float(self.day_detail[1]) and is_float(self.day_detail[2]):
                            # day_data is a dict of each day temperature
                            day_data = {'Max': float(self.day_detail[0]), 'Min': float(self.day_detail[1]), 'Mean': float(self.day_detail[2])}
                            self.month.append({'day': int(self.day), 'detail': day_data})
                            self.day_detail = []
                    self.day = data
                    
                
            if self.td and self.day.isdigit():
                # day detail is a list of day temperature
                self.day_detail.append(data)
                

