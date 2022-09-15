# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 22:08:20 2022

@author: Ruiquan
"""

import folium
import pandas as pd
import os
import numpy as np
import branca
import geopandas as gpd

os.chdir(r'C:\Users\surface\Desktop\Fellow\railroad\code')
china = gpd.read_file("CHN.geojson")
china.head()


# basic china map with population (2010 & 2020)
POP_map = china[['ID_2','city_name','city','name_23','2010_pop','2020_pop','difference','geometry']]

POP_map = POP_map.rename(columns={'ID_2':'ID','city_name':'CITY_FULL','city':'CITY_CHN','name_23':'CITY_ENG',
                                  '2010_pop':'2010_POP','2020_pop':'2020_POP','difference': 'DIFF'})

POP_map['DIFF_K'] = (POP_map['DIFF']/1000).round(2)
POP_map['PERC'] = ((POP_map['2020_POP'] - POP_map['2010_POP'])/POP_map['2010_POP']).apply('{:.2%}'.format)
POP_map.head()


# add another csv to the dataframe: list firms
firms = pd.read_csv('firms.csv')
merge_map = pd.merge(POP_map, firms, how="left", on=["CITY_CHN"])

merge_map = merge_map.rename(columns={'Density (listed firm per 100,000 pepople)':'DEN',
                                     'Number of listed firm':'NUM'})
merge_map = merge_map.drop('population', axis=1)
merge_map = merge_map.drop('city name', axis=1)

merge_map.head()


# make map: create two layers
china_map = folium.Map(location=[38,110], zoom_start=4)
fg1 = folium.FeatureGroup(name='Demographic Changes in China',overlay=False).add_to(china_map)
fg2 = folium.FeatureGroup(name='Density of List Firms in China',overlay=False).add_to(china_map)


# first layer: population map
layer_1 = folium.Choropleth(
    geo_data=merge_map,
    data=merge_map,
    columns=["ID","DIFF_K"],
    threshold_scale=[-3200,-2000,-1000,0,1000,3000,5000,7200],
    key_on="feature.properties.ID",
    fill_color='RdYlGn_r',
    nan_fill_color='#FAF9F6',
    fill_opacity=0.7,
    line_opacity=0.8,
    line_weight=0.5,
    smooth_factor=0.7,
    legend_name='Demographic Changes Per Thousand in China (2020 vs 2010)',
    highlight=True).geojson.add_to(fg1)


# add tool tip
folium.features.GeoJson(
    data=merge_map,
    style_function=lambda x: {'color':'black','fillColor':'transparent','weight':0.5},
    tooltip=folium.features.GeoJsonTooltip(
        fields=['CITY_CHN','2020_POP','2010_POP','DIFF','PERC'],
         aliases=["City Name:","Population in 2020","Population in 2010:",
                  "Demographic Changes:","Demographic Changes (%):"],
        localize=True,
        sticky=False,
        labels=True,
        style="""
        background-color: #F0EFEF;
        border: 2px solid black;
        border-radius: 3px;
        box-shadow: 3px;
        """,
        max_width=800,),
    highlight_function=lambda x: {'weight':3,'color':'black'},
).add_to(layer_1)


# second layer: list firms map
fg2 = folium.FeatureGroup(name='Density of List Firms in China',overlay=False).add_to(china_map)

layer_2 = folium.Choropleth(
    geo_data=merge_map,
    data=merge_map,
    columns=["ID","DEN"],
    key_on="feature.properties.ID",
    fill_color='YlOrRd',
    nan_fill_color='#FAF9F6',
    fill_opacity=0.7,
    line_opacity=0.8,
    line_weight=0.5,
    smooth_factor=0.7,
    legend_name='List Firms Density in China',
    highlight=True).geojson.add_to(fg2)

layer_2.add_child(
    folium.features.GeoJsonTooltip(
        fields=['CITY_CHN','DEN'],
        aliases=["City Name:", "List Firms Density"],
        localize=True,
        sticky=False,
        labels=True,
        max_width=800,),)


# add layer control to the map
folium.TileLayer('cartodbdark_matter',overlay=True,name="View in Dark Mode").add_to(china_map)
folium.TileLayer('cartodbpositron',overlay=True,name="Viw in Light Mode").add_to(china_map)
folium.LayerControl(collapsed=False).add_to(china_map)
china_map


# save the map to html
china_map.save("map.html")