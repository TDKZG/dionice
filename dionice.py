import requests
from bs4 import BeautifulSoup
#from tabidoo_api import TabidooAPI

class PoslovniForumWebScraper:
    def __init__(self, stock_url):
        self.url = "https://www.poslovni.hr/forum/tema/"+ stock_url + "/"
        self.soup = self.get_soup()
        self.max_page_number = self._get_max_page_number()
        print("Web Scraper for: ", stock_url)

    def get_soup(self):
        response = requests.get(self.url)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    
    def _get_max_page_number(self):
        elements = self.soup.find_all('a', class_='page-numbers')
        
        max_page_number = 0
        for elem in elements:
            try:
                page_number = int(elem.text.replace(',', ''))
                if page_number > max_page_number:
                    max_page_number = page_number
            except ValueError:
                pass
        return max_page_number

    def count_posts_on_max_page(self):
        page_url = self.url + 'page/' + str(self.max_page_number)
        page_soup = self.get_soup_from_max_page(page_url)
        post_elements = page_soup.find_all('div', id=lambda x: x and x.startswith('post-'))
        return len(post_elements)

    def get_soup_from_max_page(self, url):
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    
    def store_data(self, obj_api, page_number, post_count):
        # Ovdje možete integrirati logiku za pohranu podataka putem API-ja
        pass

    def get_previous_data(self, id_dionice):
        app_id = "fa1c82ba-349f-42d1-9bb8-4d1d67f6a15b"  # Zamijenite s vašim stvarnim app_id
        table_id = "6bc28fc5-d163-4066-a0cd-3ab33406ed80"
        url = f'https://app.tabidoo.cloud/api/v2/apps/{app_id}/tables/{table_id}/data'
        
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Trebate dodati logiku za filtriranje i dohvat željenih podataka iz odgovora
        # Na primjer, ovdje pretpostavljamo da su podaci dostupni u polju 'records' i vraćamo posljednji zapis
        if data and 'records' in data:
            return data['records'][-1]
        return None




import requests
import json
from datetime import datetime

jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3NTdmYmU4MS03M2E3LTRhZTktODkyNi0xNzllMWVkZjE5OGIiLCJ1bmlxdWVfbmFtZSI6ImFwaVRva2VuSWRfNzQ2NjA1NDAtZDFkMy00OWVmLThjYWUtYjAxNTU4M2JlYzAzIiwicHVycG9zZSI6IkFQSVRva2VuIiwiYXBpVG9rZW5JZCI6Ijc0NjYwNTQwLWQxZDMtNDllZi04Y2FlLWIwMTU1ODNiZWMwMyIsIm5iZiI6MTY5MzIwMjkxNCwiZXhwIjo0ODQ4ODc2NTE0LCJpYXQiOjE2OTMyMDI5MTR9.aO0gN78R1nfIS8JvKmkqOUZVE9S55ZEJtA4Di7WZgWg"

class TabidooAPI:
    def __init__(self, app_id):
        self.jwt_token = jwt_token
        self.app_id = app_id
        self.headers = {
            "Authorization": f"Bearer {self.jwt_token}",
            "Content-Type": "application/json"
        }

    def insert_redak(self, app_id, table_id, cijena_eur, id_dionice):
        ts_cijene = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        data = {
            "fields": {
                "ts_cijene": ts_cijene,
                "cijena_eur": cijena_eur,
                "id_dionice": id_dionice  
            }
        }
        response = requests.post(f'https://app.tabidoo.cloud/api/v2/apps/{app_id}/tables/{table_id}/data', headers=self.headers, data=json.dumps(data))
        
        if response.status_code == 200:
            print("Redak uspješno unesen!")
        else:
            print("Greška prilikom unosa retka:", response.text)
    
    def get_dionica_na_forumu(self, table_name):
        request = requests.get(f'https://app.tabidoo.cloud/api/v2/apps/{self.app_id}/tables/{table_name}/data', headers=self.headers)
        response = request.json()
        
        if response['data']:
            for row in response['data']:
                #print(row['fields'])
                pass
            return response['data']
        return response['data']
    
    def update_dionica_na_forumu(self, table_id, record_id, br_str, br_postova):
        # Define the data to be updated
        data = {
            "fields": {
                "record_id": record_id,
                "br_stranice": br_str,
                "br_postova_na_stranici": br_postova
            }
        }
        print(data)
        # Define the endpoint URL
        url = f'https://app.tabidoo.cloud/api/v2/apps/{self.app_id}/tables/{table_id}/data/{record_id}?dataResponseType=All'
        
        # Make the PATCH request to update the record
        response = requests.patch(url, headers=self.headers, data=json.dumps(data))
        
        if response.status_code == 200:
            print("Record successfully updated!")
        else:
            print("Error updating record:", response.text)























if __name__ == "__main__":

    stock_urls = ["arnt-arenaturist-dd", "plag-plava-laguna-dd", "ingr-ingra-dd"]
    for i, url in enumerate(stock_urls):

        scraper = PoslovniForumWebScraper(url)
        num_posts = scraper.count_posts_on_max_page()

        app_name = 'stocks-web-scraping'
        table_name = 'dionica_na_forumu'
        api = TabidooAPI(app_name)
        row_table_name = api.get_dionica_na_forumu(table_name)
        row_id = row_table_name[i]['id']
        previous_data = row_table_name[i]['fields']
        if previous_data:
            prev_max_page, prev_post_count = previous_data['br_stranice'], previous_data['br_postova_na_stranici']
            if scraper.max_page_number > prev_max_page or (scraper.max_page_number == prev_max_page and num_posts > prev_post_count):
                print(f"Postoji novi sadržaj! Broj postova na maksimalnoj stranici je: {num_posts}")
                api.update_dionica_na_forumu(table_name,row_id,scraper.max_page_number,num_posts)
            else:
                print(f"Broj postova na maksimalnoj stranici je: {num_posts}")
                print("Ne radim update tablice!")
        else:
            print(f"Broj postova na maksimalnoj stranici je: {num_posts}")


