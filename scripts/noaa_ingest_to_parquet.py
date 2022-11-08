'''
    Ingests NOAA data to 3 parquet files for each dataset:
    details, fatalities, locations
'''


import os
from dotenv import dotenv_values
import requests
from io import BytesIO
from time import time

import pandas as pd
import fastparquet

#helper functions
from get_noaa_filenames import get_noaa_filenames
from noaa_helper_funcs import clean_details_df, clean_money_strings, make_fips, concat_NOAA_CSVs_to_DF

def get_NOAA_file(filename):
    url = 'https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/' + filename
    # r = requests.get(url) BytesIO(r.content)
    df = pd.read_csv(url, compression='gzip', header=0, low_memory=False)
    return df



def ingest_NOAA_to_parquet():

    print('Checking if ingestion is necessary...')
    old_files_list = pd.read_csv('../noaa-storm-data/NOAA_filenames.csv')
    files_list = get_noaa_filenames()

    if old_files_list.file_name.equals(files_list.file_name):
        print('No ingestion needed. Files are same same!')
    else:
        print('INGESTION TIME!')
        #sort file names
        details_files = files_list[files_list.dataset == 'details']
        # fatalities_files = files_list[files_list.dataset == 'fatalities']
        # locations_files = files_list[files_list.dataset == 'locations']
        print('files found! generating dataframes...')
        t1=time()
        #generate
        raw_details_df = concat_NOAA_CSVs_to_DF(details_files.file_name)

        # raw_fatalities_df = concat_NOAA_CSVs_to_DF(fatalities_files.file_name)
        # raw_locations_df = concat_NOAA_CSVs_to_DF(locations_files.file_name)
        t2=time()
        print(f'df generated in {t2-t1} seconds! cleaning...')

        #clean
        cleaned_details_df = clean_details_df(raw_details_df)
        # cleaned_fatalities_df = clean_fatalities(raw_fatalities_df)
        # cleaned_locations_df = clean_locations(raw_locations_df)
        t3=time()
        print(f'df cleaned in {t3-t2} seconds! now saving...')

        #save to parquet
        cleaned_details_df.to_parquet('../noaa-storm-data/details.parquet.gzip',compression='gzip')
        t4=time()
        print(f'''NOAA datasets are now cleaned and saved in parquet files
        in the current directory. \nIt only took {t4-t1} seconds.''')

if __name__ == '__main__':
    ingest_NOAA_to_parquet()
