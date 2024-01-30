import pandas as pd
from requests_html import HTMLSession
import re
from tqdm import trange

class Scraper:
    def __init__(self):
        self.session = HTMLSession
        self.df_todo = None
        self.url_0 = "https://patents.google.com/patent/"
        self.pattern = r"^[A-Za-z]\d{2,}[A-Za-z]\d+\/\d{2,}$"
        
    def scrape_all(self, file_path, export_path, id_column, start_idx=0, end_idx=0):
        
        self.df_todo = pd.read_csv(file_path, low_memory=False)
        
        self.df_todo['cpc'] = ''
        self.df_todo['date'] = ''
        self.df_todo['inventor'] = ''
        self.df_todo['title'] = ''
        
        id_old = ""        
        if end_idx != 0:
            end_idx = len(self.df_todo)
        for i in trange(start_idx, end_idx):
            id_new = df_todo[id_column][i].replace('-', '')
            if id_old != id_new:
                id_old = id_new
                url = self.url_0 + id_new
                r = self.session.get(url)
                r.html.render()
                
                self.df_todo['cpc'][i] = self.get_cpc(r)
                self.df_todo['date'][i] = self.get_date(r)
                self.df_todo['inventor'][i] = self.get_inventor(r)
                self.df_todo['title'][i] = self.get_title(r)
                                
                
    def get_cpc(self, r):        
        classification_element = r.html.find('.style-scope.classification-tree')
        unique_elements = set()
        for j in range(len(classification_element)):
            text = classification_element[j].text
            if re.match(self.pattern, text):
                if text not in unique_elements:
                    unique_elements.add(text)
                print("the cpc is", text)
            else:
                continue
        return unique_elements
    
    def get_date(self, r):
        events = r.html.find('.event.layout.horizontal.style-scope.application-timeline')
        date_list = []
        info_list = []
        for event in events:
            # Attempting to find the date in various possible classes
            date_element = None
            for date_class in ['filed', 'priority', 'reassignment', 'granted', 'publication', 'legal-status']:
                date_element = event.find(f'.{date_class}.style-scope.application-timeline', first=True)
                if date_element:
                    break
        return date_element
    
    def get_inventor(self, r):
        inventor_element = r.html.find('dd.style-scope.patent-result state-modifier')
        list_name = []
        for element in inventor_element:
            if 'data-inventor' in element.attrs:
                list_name.append(element.attrs['data-inventor'])
        return list_name
    
    def get_title(self, r):
        title_element = r.html.find('h1')
        try:
            title = title_element[1].text.strip()
        except:
            title = 'error'
            print("title not found")
        return title            

        
        