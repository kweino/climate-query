'''
    Ingests NOAA data to a local Postgres DB with three tables:
    details, fatalities, locations
'''
import os
from dotenv import dotenv_values
import requests
from io import BytesIO
from time import time

import pandas as pd
from sqlalchemy import create_engine

#helper functions
from get_noaa_filenames import get_noaa_filenames
from noaa_helper_funcs import clean_details_df, clean_money_strings, make_fips, concat_NOAA_CSVs_to_DF

def ingest_to_postgres():
    t_start = time()
    print('here we go again...')
    #set up engine
    # config = dotenv_values('../.env')
    user = 'root' #config['POSTGRES_USER']
    password = 'root' #config['POSTGRES_PASSWORD']

    engine = create_engine(f'postgresql://{user}:{password}@pgdatabase:5432/noaa_storms')


    #get/sort file names
    files_list = get_noaa_filenames()
    details_files = files_list[files_list.dataset == 'details']

    # fatalities_files = files_list[files_list.dataset == 'fatalities']
    # locations_files = files_list[files_list.dataset == 'locations']
    print('files found! generating dataframes & cleaning dataframes...')

    #generate
    details_df = concat_NOAA_CSVs_to_DF(details_files.file_name)

    # raw_fatalities_df = concat_NOAA_CSVs_to_DF(fatalities_files.file_name)
    # raw_locations_df = concat_NOAA_CSVs_to_DF(locations_files.file_name)
    print('df generated! loading...')

    #clean
    cleaned_details_df = clean_details(raw_details_df)
    # cleaned_fatalities_df = clean_fatalities(raw_fatalities_df)
    # cleaned_locations_df = clean_locations(raw_locations_df)
    # print('df cleaned! loading...')

    ### load dfs to Postgres SQL database ###
    # details_df = pd.DataFrame([0,4,5,6,2,6,7,8], columns=['testy'])
    details_df.head(n=0).to_sql(name='details', con=engine, if_exists='replace')
    details_df.to_sql(name='details', con=engine, if_exists='append', chunksize=100000)

    t_end = time()
    print(f'Files are ingested to Postgres! It only took {t_end-t_start} seconds.')

if __name__ == '__main__':
    ingest_to_postgres()
