import streamlit as st
from opencage.geocoder import OpenCageGeocode
import requests
from datetime import datetime as dt
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")

#### SECRETS ####
geocode_key = st.secrets.GEOCODE_API_KEY


### START OF PAGE ###
with st.sidebar.form(key='geo_input_form'):
    user_loc = st.text_input('Location (County, State):')
    # user_area = st.radio('Level of Analysis:',['State','County'])
    user_loc_button = st.form_submit_button('Get Climate Info')

st.header('Climate Query')


if user_loc_button:

    geocoder = OpenCageGeocode(geocode_key)
    results = geocoder.geocode(user_loc)
    try:
        user_county = results[0]['components']['county']
    except KeyError:
        st.header('Invalid query. Please enter a valid US county and state.')
        results = None

    if results:

        # st.write(results[0])
        user_county = results[0]['components']['county']
        user_state = results[0]['components']['state']
        user_county_fips = results[0]['annotations']['FIPS']['county']
        user_state_fips = results[0]['annotations']['FIPS']['state']



        # USDM URL structure for Comprehensive Statistics:
        # https://usdmdataservices.unl.edu/api/[area]/[statistics type_1]?aoi=[aoi]&startdate=[start date]&enddate=[end date]&statisticsType=[statistics type_2]

        # if user_area == 'County':
        area = 'CountyStatistics'
        user_aoi = user_county_fips
        st.write(f'Results for {user_county}, {user_state}')

        # elif user_area == 'State':
        #   area = 'StateStatistics'
        #   user_aoi = user_state_fips
        #   st.write(f'Results for {user_state}')
        # else:
        #     raise ValueError('Please enter "state" or "county"')

        stat_type_1 = 'GetDroughtSeverityStatisticsByAreaPercent'
        aoi = user_aoi
        start_date = '01/04/2000' # earliest date of the dataset
        end_date = dt.date(dt.now()).strftime('%m/%d/%Y') #today's date
        stat_type_2 = 1 # keep 1 for cumulative stats. entering 2 will get categorical stats

        usdm_url = f'https://usdmdataservices.unl.edu/api/{area}/{stat_type_1}?aoi={aoi}&startdate={start_date}&enddate={end_date}&statisticsType={stat_type_2}'
        print('Getting requests for:')
        print(usdm_url)

        r = requests.get(usdm_url,
                         headers={'Accept':'JSON'}
                         )
        print(f'Response: {r.status_code}')
        r_json = r.json()
        print(r_json[-1])

        ### TRANSFORMATION ###
        usdm_df = pd.json_normalize(r_json)
        usdm_df = usdm_df.astype({'MapDate': 'datetime64',
                                  'D0': 'float64',
                                  'D1': 'float64',
                                  'D2': 'float64',
                                  'D3': 'float64',
                                  'D4': 'float64',
                                  'ValidStart': 'datetime64',
                                  'ValidEnd': 'datetime64',
                                  'StatisticFormatID': 'int64'})

        ### PLOT ###
        plot_df = usdm_df.melt(id_vars='MapDate',
            value_vars=['None','D0','D1','D2','D3','D4'],
            var_name='severity',
            value_name='area_percent').sort_values('MapDate')

        x= plot_df.MapDate
        y= plot_df.area_percent
        layout = go.Layout(title=f'Drought history for {user_county}, {user_state} since 2000')

        fig = go.Figure(layout=layout)

        fig.add_trace(go.Scatter( name='D4',
            x=x[plot_df.severity == 'D4'], y=y[plot_df.severity == 'D4'],
            mode='lines',
            line=dict(width=0.5, color='purple'),
            stackgroup='one',
            groupnorm='percent' # sets the normalization for the sum of the stackgroup
        ))
        fig.add_trace(go.Scatter( name='D3',
            x=x[plot_df.severity == 'D3'], y=y[plot_df.severity == 'D3'],
            mode='lines',
            line=dict(width=0.5, color='blue'),
            stackgroup='one'
        ))
        fig.add_trace(go.Scatter( name='D2',
            x=x[plot_df.severity == 'D2'], y=y[plot_df.severity == 'D2'],
            mode='lines',
            line=dict(width=0.5, color='red'),
            stackgroup='one'
        ))
        fig.add_trace(go.Scatter( name='D1',
            x=x[plot_df.severity == 'D1'], y=y[plot_df.severity == 'D1'],
            mode='lines',
            line=dict(width=0.5, color='orange'),
            stackgroup='one'
        ))
        fig.add_trace(go.Scatter( name='D0',
            x=x[plot_df.severity == 'D0'], y=y[plot_df.severity == 'D0'],
            mode='lines',
            line=dict(width=0.5, color='yellow'),
            stackgroup='one'
        ))
        fig.add_trace(go.Scatter( name='No Drought',
            x=x[plot_df.severity == 'None'], y=y[plot_df.severity == 'None'],
            mode='lines',
            line=dict(width=0.5, color='#0E1116'),
            stackgroup='one'
        ))

        fig.update_layout(
            showlegend=True,
            paper_bgcolor='#0E1116',
            yaxis=dict(
                type='linear',
                range=[1, 100],
                ticksuffix='%'))

        st.plotly_chart(fig)
