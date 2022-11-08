'''This file contains all of the helper functions needed to clean the NOAA CSV files'''

import time as time
import re
import pandas as pd

def concat_NOAA_CSVs_to_DF(filename_list):
  df = pd.DataFrame()
  for filename in filename_list:
    print(f'adding {filename}')
    t_start = time()

    event = get_NOAA_file(filename)
    # cleaned_event = clean_details(event)
    # print(f'  length: {len(cleaned_event)}')
    df = pd.concat([df,event])

    t_end = time()
    print(f'  added file, took {t_end-t_start} seconds')
  return df.reset_index()

def clean_details_df(df):
    '''cleans raw NOAA data in the details dataset for loading'''
    t1=time()
    #make combined FIPS code for county
    df['FIPS'] = df.apply(lambda row: make_fips(row), axis=1)
    t2=time()
    print(f'FIPS codes generated, took {t2-t1} seconds')

    #clean money strings
    df.DAMAGE_PROPERTY = df.DAMAGE_PROPERTY.apply(lambda row: clean_money_strings(row))
    df.DAMAGE_CROPS = df.DAMAGE_CROPS.apply(lambda row: clean_money_strings(row))
    t3=time()
    print(f'Property & crop damage columns cleaned, took {t3-t2} seconds')
    # only retain rows with valid county designations
    cleaned_df = df[ (df.FIPS.notna()) & (df.STATE_FIPS < 60) ]

    return cleaned_df

def clean_money_strings(row):
  '''converts dollar value strings in the NOAA dataset into integers'''
  result = 0


  if isinstance(row, int):
    return row

  elif row is None:
    return 0

  else:

    # all row values into upper case string
    r = str(row).upper()

    #hundreds
    if r[-1] == 'H':
      result = r[:-1] + '00'

    # thousands
    elif r[-1] == 'K':
      #check for dot
      if re.search(r'\.', r): #if dot
        result = r[:-1].split('.') # split at dot,
        result[-1] = result[-1].ljust(3,'0') #add up to 3 zeros to last str in list,
        result = ''.join(result) # rejoin

      else: #if no dot,
        result = r[:-1] + '000' # add 3 zeros to number

    # millions
    elif r[-1] == 'M':
      #check for dot
      if re.search(r'\.', r): #if dot
        result = r[:-1].split('.') # split at dot,
        result[-1] = result[-1].ljust(6,'0') #add up to 6 zeros to last str in list,
        result = ''.join(result) # rejo/in

      else: #if no dot,
        result = r[:-1] + '000000' # add 3 zeros to number

    # billions
    elif r[-1] == 'B':
      #check for dot
      if re.search(r'\.', r): #if dot
        result = r[:-1].split('.') # split at dot,
        result[-1] = result[-1].ljust(9,'0') #add up to 9 zeros to last str in list,
        result = ''.join(result) # rejoin

      else: #if no dot,
        result = r[:-1] + '000000000' # add 9 zeros to number

    else:
      result = 0

    return int(result)

def make_fips(row):
    '''Joins state & county FIPS, adding leading zeroes where appropriate'''
    try:
        return str(int(row.STATE_FIPS)).zfill(2) + str(row.CZ_FIPS).zfill(3)
    except ValueError:
        return None
