import requests
from bs4 import BeautifulSoup
import csv

class DashBoard:
    results = []

    def fetch(self, url):
        return requests.get(url)

    def parse(self, xml):
        content = BeautifulSoup(xml, 'xml')
        metars = content.find_all('METAR')
        headers = ['station_id', 'latitude', 'longitude', 'temp_c', 'dewpoint_c', 'wind_dir_degrees', 'wind_speed_kt', 'altim_in_hg']
        self.results.append(headers)

        for metar in metars:
            row = [
                metar.find('station_id').text if metar.find('station_id') else '',
                metar.find('latitude').text if metar.find('latitude') else '',
                metar.find('longitude').text if metar.find('longitude') else '',
                metar.find('temp_c').text if metar.find('temp_c') else '',
                metar.find('dewpoint_c').text if metar.find('dewpoint_c') else '',
                metar.find('wind_dir_degrees').text if metar.find('wind_dir_degrees') else '',
                metar.find('wind_speed_kt').text if metar.find('wind_speed_kt') else '',
                metar.find('altim_in_hg').text if metar.find('altim_in_hg') else ''
            ]
            self.results.append(row)

    def to_csv(self):
        with open('proxies.csv', 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(self.results)

    def run(self):
        response = self.fetch('https://aviationweather.gov/data/cache/metars.cache.xml')
        self.parse(response.text)
        self.to_csv()

if __name__ == '__main__':
    scraper = DashBoard()
    scraper.run()