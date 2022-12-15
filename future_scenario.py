import pandas as pd
import numpy as np
import os

import plotly as plt
import matplotlib.pyplot as plt
import seaborn as sns

from statsforecast import StatsForecast
from statsforecast.models import AutoARIMA, ETS

path = r'/Users/changruiquan/Desktop/2022-amfam-clinic/NRI'
geo_path = r'/Users/changruiquan/Desktop/2022-amfam-clinic/geo'
des_dir =  r'/Users/changruiquan/Desktop/2022-amfam-clinic/data'

eal = pd.read_csv(os.path.join(path,'eal_rate.csv'))
details = pd.read_csv(os.path.join(des_dir,'details.csv' ))

# generalize event types
def generalize_event(df, event_type):
    df['EVENT'] = np.nan
    for element in event_type:
        df['EVENT'] = np.where((df['EVENT_TYPE'].str.contains('%s'%(element))) | 
                               (df['EVENT_TYPE'].str.contains('%s'%(element.upper()))), '%s'%(element),
                               np.where(~df['EVENT'].isna(), df['EVENT'], 'Other'))
    return df

event_type = ['Avalanche', 'Cold', 'Drought', 'Heat', 'Hurricane','Ice Storm', 'Blizzard', 'Debris Flow', 
              'Lightning', 'Flood', 'Lakeshore Flood','Coastal Flood', 'Hail', 'High Wind', 'Strong Wind', 
              'Tornado', 'Tsunami', 'Volcanic', 'Wildfire', 'Winter', 'Heavy Snow']
df = generalize_event(details, event_type)

## rename to NRI hazard type
df['EVENT'] = df['EVENT'].replace({'Avalanche': 'AVLN', 'Coastal Flood': 'CFLD', 'Cold': 'CWAV', 
                                   'Drought': 'DRGT', 'Heat': 'HWAV', 'Hurricane': 'HRCN',
                                   'Ice Storm': 'ISTM', 'Blizzard': 'ISTM', 'Debris Flow': 'LNDS',
                                   'Lightning': 'LTNG', 'Lakeshore Flood': 'RFLD', 'Flood': 'RFLD',
                                   'Hail': 'HAIL', 'High Wind': 'SWND', 'Strong Wind': 'SWND',
                                   'Tornado': 'TRND', 'Tsunami': 'TSUN', 'Volcanic':'VLCN',
                                   'Wildfire': 'WFIR', 'Winter': 'WNTW', 'Heavy Snow': 'WNTW'})


# get time series
sub = df[(df['BEGIN_YEAR']<2022) & (df['BEGIN_YEAR']>1995)]
sub['TIME'] = pd.to_datetime(sub['BEGIN_YEARMONTH'], format='%Y%m')

def yearly_series(event):
    data = sub[['BEGIN_YEAR', 'STATE', 'EVENT', 'EVENT_ID']]
    df_final = data[data['EVENT']==event]
    t_series = df_final.groupby('BEGIN_YEAR')['EVENT_ID'].count().reset_index()
    t_series = t_series.rename(columns={'EVENT_ID':'COUNT'})
    return t_series

def monthly_series(event):
    data = sub[['TIME', 'STATE', 'EVENT', 'EVENT_ID']]
    df_final = data[data['EVENT']==event]
    t_series = df_final.groupby('TIME')['EVENT_ID'].count().reset_index()
    t_series = t_series.rename(columns={'EVENT_ID':'COUNT'})
    return t_series

events_dic = {'HAIL':'HAIL', 'TRND':'Tornado', 'CWAV':'Cold Wave', 
              'WNTW':'Winter Weather', 'ISTM':'Ice Storm', 'SWND':'Strong Wind', 
              'HWAV':'Heat Wave', 'RFLD':'Riverine Flooding', 'LTNG':'Lightning',
              'WFIR':'Wildfire', 'AVLN':'Avalanche', 'LNDS':'Landslide', 
              'HRCN':'Hurricane', 'CFLD':'Coastal Flooding', 'TSUN':'Tsunami', 
              'VLCN':'Volcanic Activity'}
for event in list(events_dic.keys()):
    vars()[event] = yearly_series(event)
    

# plot time series
def plot_yearly(event):
    df = yearly_series(event)
    x = df['BEGIN_YEAR']
    y = df['COUNT']
    name = events_dic.get(event)

    fig, ax = plt.subplots(figsize=(20,7))
    ax = sns.lineplot(data=df, x=x, y=y, linewidth = 2.5)
    b, a = np.polyfit(x, y, deg=1)
    ax.plot(x, a + b * x, color="darkred", linestyle='dotted', lw=2.5)
    
    ax.set_xlabel('Year', fontsize=14)
    ax.set_ylabel('Annualized Frequency', fontsize=14)
    ax.set_title('Annualized Frequency of %s Over All States: 1996-2021'%(name), fontsize=16)
    plt.xticks(fontsize=12)
    for x,y in zip(x, y):
        label = "{:.0f}".format(y)
        ax.annotate(label, (x,y), textcoords="offset points",
                    xytext=(0,6), ha='center', fontsize=10)
    plt.annotate('Source: NOAA', (0,0), (-40,-40), 
                 fontsize=14, xycoords='axes fraction', 
                 textcoords='offset points', va='top')
    return fig

def plot_monthly(event):
    df = monthly_series(event)
    x = df['TIME']
    y = df['COUNT']
    name = events_dic.get(event)

    fig, ax = plt.subplots(figsize=(20,7))
    ax = sns.lineplot(data=df, x=x, y=y, linewidth = 2.5)
    
    ax.set_xlabel('Time', fontsize=14)
    ax.set_ylabel('Monthly Frequency', fontsize=14)
    ax.set_title('Monthly Frequency of %s Over All States: 1996-2021'%(name), fontsize=16)
    plt.xticks(fontsize=12)
    plt.annotate('Source: NOAA', (0,0), (-40,-40), 
                 fontsize=14, xycoords='axes fraction', 
                 textcoords='offset points', va='top')
    return fig

[plot_yearly(event) for event in list(events_dic.keys())]


# future scenario
## OLS: percentage increase per year
def get_coef(event):
    df = yearly_series(event)
    x = df['BEGIN_YEAR']
    y = df['COUNT']
    b, a = np.polyfit(x, y, deg=1)
    coef = (b/(y.mean())).round(4)
    coef_dic = {event:coef}
    return coef_dic

coef_dic = [get_coef(event) for event in list(events_dic.keys())]

def future_eals(events):
    df = eal.fillna(0)
    for event in events:
        rate = get_coef(event).get(event)
        df['%s_22'%(event)] = (1+rate)*df['%s'%(event)]
        df['%s_23'%(event)] = (1+rate)*(1+rate)*df['%s'%(event)]
        df['%s_EAL22'%(event)] = df['%s_EXPB'%(event)] * df['%s_22'%(event)] * df['%s_HLRB'%(event)]
        df['%s_EAL23'%(event)] = df['%s_EXPB'%(event)] * df['%s_23'%(event)] * df['%s_HLRB'%(event)]
        df['%s_EALCROOT22'%(event)] = df['%s_EAL22'%(event)] ** (1/3)
        df['%s_EALCROOT23'%(event)] = df['%s_EAL23'%(event)] ** (1/3)
        df['%s_EALS22'%(event)] = ((df['%s_EALCROOT22'%(event)] - min(df['%s_EALCROOT22'%(event)]))/(max(df['%s_EALCROOT22'%(event)]) - min(df['%s_EALCROOT22'%(event)])))*100
        df['%s_EALS23'%(event)] = ((df['%s_EALCROOT23'%(event)] - min(df['%s_EALCROOT23'%(event)]))/(max(df['%s_EALCROOT23'%(event)]) - min(df['%s_EALCROOT23'%(event)])))*100    
    return df

## ARIMA / ETS model
event = 'TRND'
df = eal.fillna(0)
rate = get_coef(event).get(event)
df['%s_22'%(event)] = (1+rate)*df['%s'%(event)]
df['%s_23'%(event)] = (1+rate)*(1+rate)*df['%s'%(event)]
df['%s_EAL22'%(event)] = df['%s_EXPB'%(event)] * df['%s_22'%(event)] * df['%s_HLRB'%(event)]
df['%s_EAL23'%(event)] = df['%s_EXPB'%(event)] * df['%s_23'%(event)] * df['%s_HLRB'%(event)]
df['%s_EALCROOT22'%(event)] = df['%s_EAL22'%(event)] ** (1/3)
df['%s_EALCROOT23'%(event)] = df['%s_EAL23'%(event)] ** (1/3)
df['%s_EALS22'%(event)] = ((df['%s_EALCROOT22'%(event)] - min(df['%s_EALCROOT22'%(event)]))/(max(df['%s_EALCROOT22'%(event)]) - min(df['%s_EALCROOT22'%(event)])))*100
df['%s_EALS23'%(event)] = ((df['%s_EALCROOT23'%(event)] - min(df['%s_EALCROOT23'%(event)]))/(max(df['%s_EALCROOT23'%(event)]) - min(df['%s_EALCROOT23'%(event)])))*100    

TRND_df = TRND.rename(columns={'TIME':'ds','COUNT':'y'})
TRND_df['ds'] = pd.to_datetime(TRND_df['ds']) + MonthEnd(1)
TRND_df['unique_id']=0
TRND_df = TRND_df.set_index('unique_id')
Y_train_df = TRND_df[TRND_df.ds <= '2016-12-01']
Y_test_df = TRND_df[TRND_df.ds >'2016-12-01']

season_length = 12 
horizon = len(Y_test_df) 

models = [
    AutoARIMA(season_length=season_length),
    ETS(season_length=season_length),
]

sf = StatsForecast(
    df=Y_train_df,
    models=models,
    freq='M', 
    n_jobs = -1
)

Y_hat_df = sf.forecast(horizon)
Y_hat_df

Y_hat_df = Y_test_df.merge(Y_hat_df, how='left', on=['unique_id', 'ds'])


fig, ax = plt.subplots(1, 1, figsize = (20, 7))
plot_df = pd.concat([Y_train_df, Y_hat_df]).set_index('ds')
plot_df[['y', 'AutoARIMA', 'ETS']].plot(ax=ax, linewidth=2)
ax.set_title('Monthly Tornado Frequency Forecast', fontsize=22)
ax.set_ylabel('Monthly Frequency of Hail', fontsize=20)
ax.set_xlabel('Timestamp [t]', fontsize=20)
ax.legend(prop={'size': 15})


