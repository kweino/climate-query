import requests
from bs4 import BeautifulSoup
import re
import gzip
from io import BytesIO
import pandas as pd
from time import time
from datetime import datetime

def main(): # Add Output params
    '''
    Grabs the current list of file names from the NOAA database &
    exports it to a CSV file
    '''

    # page request
    page = requests.get('https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/')
    soup = BeautifulSoup(page.text, "html.parser")
    links = soup.select('a')

    #extract only csv files from list
    file_names = [links[i].text for i in range(len(links)) if re.search(r'\S*.csv.gz', links[i].text)]

    NOAA_filenames = pd.DataFrame(file_names, columns=['file_name'])
    NOAA_filenames['dataset'] = NOAA_filenames.file_name.apply(lambda row: row.split('_')[1].split('-')[0])

    return NOAA_filenames

if __name__ == '__main__':
    t_start = time()
    NOAA_filenames = get_noaa_filenames()
    NOAA_filenames.to_csv(f'NOAA_filenames.csv')
    t_end = time()
    print(f'All NOAA filenames obtained, took {t_end-t_start} seconds')
