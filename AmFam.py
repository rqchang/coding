import gzip
import pandas as pd
import numpy as np
import os
import glob
import datetime

import bokeh
from bokeh.plotting import figure, show
from bokeh.layouts import gridplot
from ipywidgets import interact, interact_manual
import pandas_datareader.data as web
from bokeh.models import HoverTool
from bokeh.models.widgets import Panel, Tabs

import geopandas as gpd
import plotly as plt
import plotly.express as px

from bs4 import BeautifulSoup 
import requests


###################### Step 1 Unzip gz to csv Files ########################

os.chdir(r'/Users/changruiquan/Documents/GitHub/2022-amfam-clinic/noaa-stormevents')
src_dir = '/Users/changruiquan/Documents/GitHub/2022-amfam-clinic/noaa-stormevents'
des_dir = '/Users/changruiquan/Documents/GitHub/2022-amfam-clinic/events_csv'

# get file names
gz_names = []
for files in os.listdir(src_dir):
    if files.endswith('.csv.gz'):
        gz_names.append(files)
        

# unzip gz files to csv files:
for name in gz_names:
    with gzip.open(name, 'rt') as gz_file:
        data = gz_file.read()
        with open(name[:-3], 'wt') as out_file: 
            out_file.write(data)

# merge all csv files into a single file
def merge_csv(name, filelist):
    file = pd.DataFrame([])
    for filename in filelist:
        file_temp = pd.read_csv(filename)
        file = pd.concat([file,file_temp])
    file.to_csv('{}.csv'.format(name), encoding='utf-8')

## details
detail_lists = glob.glob(src_dir+'/*details*.csv')
merge_csv('details', detail_lists)

## fatalities
fatality_lists = glob.glob(src_dir+'/*fatalities*.csv')
merge_csv('fatalities', fatality_lists)

## locations
location_lists = glob.glob(src_dir+'/*locations*.csv')
merge_csv('locations', location_lists)


###################### Step 2 Basic Data Cleaning #########################

details = pd.read_csv(os.path.join(des_dir,'details.csv' ))
fatalities = pd.read_csv(os.path.join(des_dir,'fatalities.csv'))
locations = pd.read_csv(os.path.join(des_dir,'locations.csv'))

# data cleaning: details
## demage_property, demage_crops: object --> float
def object_to_float(i):
    if type(i) == float or type(i) == int:
        return i
    if 'K' in i:
        if len(i) > 1:
            return float(i.replace('K', '')) * 1000
        return 1000.0
    if 'M' in i:
        if len(i) > 1:
            return float(i.replace('M', '')) * 1000000
        return 1000000.0
    if 'B' in i:
        return float(i.replace('B', '')) * 1000000000
    return 0.0

details['DAMAGE_PROPERTY'] = details['DAMAGE_PROPERTY'].fillna(0).apply(object_to_float)
details['DAMAGE_CROPS'] = details['DAMAGE_CROPS'].fillna(0).apply(object_to_float)
details['BEGIN_DATE_TIME'] = pd.to_datetime(details['BEGIN_DATE_TIME'])
details['END_DATE_TIME'] = pd.to_datetime(details['END_DATE_TIME'])

### Y2K issues: values 69–99 are mapped to 1969–1999, and values 0–68 are mapped to 2000–2068
def fix_year(x):
    if x.year > 2022:
        year = x.year - 100
    else:
        year = x.year
    return datetime.date(year, x.month, x.day)

details['BEGIN_DATE_TIME'] = details['BEGIN_DATE_TIME'].apply(fix_year)
details['END_DATE_TIME'] = details['END_DATE_TIME'].apply(fix_year)

### whole date to integar
def date_to_integar(dt_time):
    return 10000 * dt_time.year + 100 * dt_time.month + dt_time.day

## extract event begin/end year, month, date
details['BEGIN_YEAR'] = pd.to_datetime(details['BEGIN_DATE_TIME']).dt.year
details['BEGIN_MONTH'] = pd.to_datetime(details['BEGIN_DATE_TIME']).dt.month
details['BEGIN_DATE'] = pd.to_datetime(details['BEGIN_DATE_TIME']).apply(date_to_integar)

details['END_YEAR'] = pd.to_datetime(details['END_DATE_TIME']).dt.year
details['END_MONTH'] = pd.to_datetime(details['END_DATE_TIME']).dt.month
details['END_DATE'] = pd.to_datetime(details['END_DATE_TIME']).apply(date_to_integar)

## add regions
## credit by Serena Huang
region = []
for row in details['STATE']:
    if row in ['WASHINGTON','OREGON','CALIFORNIA','HAWAII']:
        region.append('Pacific')
    elif row in ['IDAHO','MONTANA','WYOMING','UTAH','NEVADA','ARIZONA','COLORADO','NEW MEXICO']:
        region.append('Mountain')
    elif row in ['NORTH DAKOTA','MINNESOTA','SOUTH DAKOTA','NEBRASKA','KANSAS','MISSOURI','IOWA']:
        region.append('West North Central')
    elif row in ['WISCONSIN','ILLINOIS','MICHIGAN','INDIANA','OHIO']:
        region.append('East North Central')
    elif row in ['OKLAHOMA','TEXAS','ARKANSAS','LOUISIANA']:
        region.append('West South Central')
    elif row in ['MISSISSIPPI','TENNESSEE','KENTUCKY','ALABAMA']:
        region.append('East South Central')
    elif row in ['PENNSYLVANIA','NEW YORK','NEW JERSEY']:
        region.append('Middle Atlantic')
    elif row in ['CONNECTICUT','MASSACHUSETTS','NEW HAMPSHIRE','VERMONT','MAINE','RHODE ISLAND']:
        region.append('New England')
    elif row in ['ALASKA','PUERTO RICO','VIRGIN ISLANDS','AMERICAN SAMOA','GUAM']: 
        region.append('Territory')
    elif row in ['WEST VIRGINIA','MARYLAND','SOUTH CAROLINA','NORTH CAROLINA','DELAWARE',
                 'FLORIDA','GEORGIA','VIRGINIA','DISTRICT OF COLUMBIA']:
        region.append('South Atlantic')
    else:
        region.append('Other') #There are many lakes in this group for some reason
details['REGION'] = region

# data cleaning: fatalities
## extratct fatality year, month, date
fatalities['FAT_YEAR'] = pd.to_datetime(fatalities['FATALITY_DATE']).dt.year.astype('Int64')
fatalities['FAT_MONTH'] = pd.to_datetime(fatalities['FATALITY_DATE']).dt.month.astype('Int64')
fatalities['FAT_DATE'] = pd.to_datetime(fatalities['FATALITY_DATE']).apply(date_to_integar).astype('Int64')

# merge three datasets into one: using event_id
drop = ['Unnamed: 0']
details = details.drop(drop, axis=1)
locations = locations.drop(drop, axis=1)
fatalities = fatalities.drop(drop, axis=1)
details_fats = pd.merge(details, fatalities, on='EVENT_ID', how='outer')
data = pd.merge(details_fats, locations, on='EVENT_ID', how='outer')

# output to csv file
details.to_csv(os.path.join(des_dir, 'details.csv'), encoding='utf-8' )
fatalities.to_csv(os.path.join(des_dir, 'fatalities.csv'), encoding='utf-8' )
locations.to_csv(os.path.join(des_dir, 'locations.csv'), encoding='utf-8' )
data.to_csv(os.path.join(des_dir,'all_data.csv'), encoding='utf-8')


################### Step 3 Lineplots of time series #####################

# create time series for each region and type of event
def t_series(region, event_type):
    df = details
    region_list = df['REGION'].unique().tolist()
    event_list = df['EVENT_TYPE'].unique().tolist()
    if (region in region_list) and (event_type in event_list): 
        temp1 = df[(df['REGION']==region) & (df['EVENT_TYPE']==event_type)]
        temp2 = temp1.groupby('YEAR').agg({'EVENT_ID': 'count', 'DAMAGE_PROPERTY': 'sum', 'DAMAGE_CROPS': 'sum'}).reset_index()
        tseries = temp2.rename({'EVENT_ID': 'EVENT_FREQ'}, axis=1)
        return tseries
    elif (region in region_list) and (event_type not in event_list): 
        return print("Please input the valid event type")
    elif (region not in region_list) and (event_type in event_list): 
        return print("Please input the valid region")
    else:
        return print("Please input the valid region and event type")
    
# annual indcidence/damage for each region and type of event
# x - time, y - count(event) / sum(damage)
def plot_region(region, event_type): 
    data = t_series(region, event_type)
    
    plot_1 = figure(title='%s: %s'%(region, event_type), x_axis_label='Year', 
                   y_axis_label='Annual Incidence', plot_height=400, plot_width=800,
                   toolbar_location=None, tools=[HoverTool()], tooltips="Annual incidence is @y in @x")
    plot_1.line(x=data['YEAR'], y=data['EVENT_FREQ'], line_width=2)
    plot_1.circle(x=data['YEAR'], y=data['EVENT_FREQ'], fill_color="white", size=5)
    panel_1 = Panel(child=plot_1, title='Incidence')
    
    plot_2 = figure(title='%s: %s'%(region, event_type), x_axis_label='Year', 
                    y_axis_label='Annual Property Damage', plot_height=400, plot_width=800,
                    toolbar_location=None, tools=[HoverTool()], tooltips="Annual property damage is @y in @x")
    plot_2.line(x=data['YEAR'], y=data['DAMAGE_PROPERTY'], line_width=2, color='orange')
    plot_2.circle(x=data['YEAR'], y=data['DAMAGE_PROPERTY'], color='orange', fill_color="white", size=5)
    panel_2 = Panel(child=plot_2, title='Property Damage')
    
    plot_3 = figure(title='%s: %s'%(region, event_type), x_axis_label='Year', 
                    y_axis_label='Annual Crops Damage', plot_height=400, plot_width=800,
                    toolbar_location=None, tools=[HoverTool()], tooltips="Annual Crops damage is @y in @x")
    plot_3.line(x=data['YEAR'], y=data['DAMAGE_CROPS'], line_width=2, color='green')
    plot_3.circle(x=data['YEAR'], y=data['DAMAGE_CROPS'], color="green", fill_color="white", size=5)
    panel_3 = Panel(child=plot_3, title='Crops Damage')    
    
    tabs = Tabs(tabs=[panel_1, panel_2, panel_3])
    
    return tabs

# create dropdown boxes for regions and types
types = details['EVENT_TYPE'].sort_values().unique()
regions = details['REGION'].sort_values().unique()

@interact(region=regions, event_type=types)
def make_plot_for(region=regions[0], event_type=types[0]):
    tabs = plot_region(region, event_type)
    show(tabs)


################### Step 4 Choropleth maps by county #####################

# generalize event types
def generalize_event(df, event_type):
    df['EVENT'] = np.nan
    for element in event_type:
        df['EVENT'] = np.where((df['EVENT_TYPE'].str.contains('%s'%(element))) | 
                               (df['EVENT_TYPE'].str.contains('%s'%(element.upper()))), '%s'%(element),
                               np.where(~df['EVENT'].isna(), df['EVENT'], 'Other'))
    return df

event_type = ['Volcanic Ash', 'Blizzard', 'Frost', 'Debris Flow', 'Tsunami','Avalanche', 
              'Lightning', 'Tid', 'Heat', 'Drought', 'Snow', 'Wind', 'Rain', 'Dust',
              'Wildfire', 'Storm', 'Fog', 'Flood', 'Hurricane', 'Hail', 'Tornado', 'Thunderstorm']
df = generalize_event(details, event_type)
df['EVENT'].unique()

# CZ crosswalk
# the FIPS in df is for C-level (e.g., 17031 is cook county)
# but the Z-level Woodford also shares this code (actually 17203 is the right code)
# to have the correct geo information, we should use the C-level name and FIPS code.
df['FIPS'] = df['STATE_FIPS']*1000 + df['CZ_FIPS']
df = df.rename({'STATE': 'STATE_NAME'}, axis=1)
df_selected = df[['EVENT_ID', 'FIPS', 'STATE_NAME', 'STATE_FIPS', 'CZ_TYPE', 'CZ_FIPS', 'CZ_NAME',
              'REGION', 'EVENT', 'BEGIN_YEAR', 'BEGIN_MONTH', 'BEGIN_DATE']]

# create query: get_incident(event)
def get_incident(event):
    df = df_selected[df_selected['BEGIN_YEAR']<2022]
    output = []
    for element in event:
        if element != 'Tornado':
            temp1 = df[(df['BEGIN_YEAR']>1995) & (df['EVENT']==element)]
            temp2 = temp1.groupby(['FIPS', 'REGION', 'STATE_NAME', 'EVENT'])['EVENT_ID'].count().reset_index()
            des = temp2.rename({'EVENT_ID': 'COUNT'}, axis=1)
            des['ANNUAL_FREQ'] = (des['COUNT'] / (2021-1996)).round(2)
            output.append(des)
        else:
            temp1 = df[df['EVENT']==element]
            temp2 = temp1.groupby(['FIPS', 'REGION', 'STATE_NAME', 'EVENT'])['EVENT_ID'].count().reset_index() 
            des = temp2.rename({'EVENT_ID': 'COUNT'}, axis=1)
            des['ANNUAL_FREQ'] = (des['COUNT'] / (2021-1950)).round(2)
            output.append(des)
    output = pd.concat(output)
    return output

event_list = df_selected['EVENT'].unique().tolist()
df_incident = get_incident(event_list)
df_incident['FIPS'] = df_incident['FIPS'].dropna().astype('int64')

# choropleth
# merge with geojson file: fill nan value with 0 to make sure every county can be plotted on the map
geojson = gpd.read_file(r'/Users/changruiquan/Desktop/2022-amfam-clinic/geo/counties.geojson')
geojson[['STATE', 'COUNTY', 'id']] = geojson[['STATE', 'COUNTY', 'id']].apply(pd.to_numeric)
geo_data = geojson[['id', 'NAME', 'geometry']]

def merge_geo(event):
    output = []
    for element in event:
        df1 = df_incident[df_incident['EVENT']==element]
        df2 = geo_data.merge(df1, left_on="id", right_on="FIPS", how="left")
        df2['EVENT'] = element
        df2[['COUNT', 'ANNUAL_FREQ']] = df2[['COUNT', 'ANNUAL_FREQ']].fillna(0)
        output.append(df2)
    output = pd.concat(output)
    return output
        
df_plot = merge_geo(event_list)

# interactive choropleth with all events
def plot_choropleth(event):
    df = df_plot[df_plot['EVENT']==event]
    fig = px.choropleth(df,
                        geojson=df_plot,
                        locations='id',
                        featureidkey="properties.id",
                        hover_name="NAME",
                        color="ANNUAL_FREQ",
                        color_continuous_scale='Reds',
                        range_color=(0, df['ANNUAL_FREQ'].quantile(0.99)),
                        scope="usa",
                        labels={'id': 'FIPS Code', 'ANNUAL_FREQ':'Annual Incident Rate'})
    fig.update_layout(title_text='Annual Incident Rate of %s by County'%(event),
                      geo = dict(scope='usa', showland = True),
                      annotations = [dict(x=0.1, y=-0.1, xref='paper', yref='paper',
                                     text='Source: American Family Insurance', showarrow = False)])
    fig.show()
    
events = df_plot['EVENT'].sort_values().unique()

@interact(event=events)
def make_plot_for(event=events[0]):
    plot = plot_choropleth(event)
    return plot

# save to html file
def save_html(event):
    for element in event:
        df = df_plot[df_plot['EVENT']==element]
        fig = px.choropleth(df,
                            geojson=df_plot,
                            locations='id',
                            featureidkey="properties.id",
                            hover_name="NAME",
                            color="ANNUAL_FREQ",
                            color_continuous_scale='Reds',
                            range_color=(0, df['ANNUAL_FREQ'].quantile(0.99)),
                            scope="usa",
                            labels={'id': 'FIPS Code', 'ANNUAL_FREQ':'Annual Incident Rate'})
        fig.update_layout(title_text='Annual Incident Rate of %s by County'%(element),
                          geo = dict(scope='usa', showland = True),
                          annotations = [dict(x=0.1, y=-0.1, xref='paper', yref='paper',
                                         text='Source: American Family Insurance', showarrow = False)])
        fig.write_html("%s.html"%(element))
        
save_html(event_list)


################### Step 5 Crops Damage / Propert Damage #####################

# Scrape CPI conversion information
def get_cpi(start_year, end_year):
    '''
    Scraping dollar-equivalent amounts for 1950-2021 using the CPI Calculator
    
    Input:
        start_year(int): the first year of time range
        end_year(int): the last year of time range
        
    Output:
        result(dict, str: int): {a dictionary with year: current amount}
    '''
    result = {}

    for yr in range(start_year, end_year+1):
        cpi_url = "https://data.bls.gov/cgi-bin/cpicalc.pl?cost1=1.00&year1=" + str(yr) +"01&year2=202209"
        response = requests.get(cpi_url)
        response_txt = response.text
        soup = BeautifulSoup(response_txt, 'html.parser')
        for amount in soup.find_all("span", id="answer"):
            cur_amount = amount.text.strip().replace('$', '')
            result[str(yr)] = float(cur_amount)
    return result

# Ongoing project, still working for machine learning and damage forecast
