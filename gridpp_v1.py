#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 11:14:39 2025

@author: ewalsh
"""

import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import cartopy.crs as ccrs
import gridpp
import os

def getLatLon(dataframe):
    
    longitude = []
    latitude = []
    
    locations = dataframe['Location'].values
    
    for val in locations:
        
        lon, lat = val.split(" ")
        
        longitude.append(float(lon))
        
        latitude.append(float(lat))
        
    return longitude, latitude
    
date = "2024-10-28"

ds = xr.open_dataset('/home/ewalsh/Documents/projects/dublin_temps/grib/fc202410280000_60_instant_t_sfc_2_geo_50.9932_348.998_643x589x750m.grib2', engine='cfgrib')

ds = ds.assign_coords(longitude=(ds.longitude % 360))
ds = ds.assign_coords(longitude=(("y", "x"), np.where(ds.longitude > 180, ds.longitude - 360, ds.longitude)))

ds = ds - 273.15

# Create a figure with Cartopy projection
fig, ax = plt.subplots(subplot_kw={"projection": ccrs.PlateCarree()})

# Plot the data using the adjusted longitude
ds.t2m.plot(
    ax=ax,
    transform=ccrs.PlateCarree(),  # Data's coordinate reference system
    cmap=plt.cm.coolwarm,
    cbar_kwargs={"label": "Temperature (°C)"},
    x='longitude',
    y='latitude'
)

# Add geographical features
ax.coastlines()
ax.gridlines(draw_labels=True, linewidth=0.5, color="gray", alpha=0.5, linestyle="--")
ax.set_extent([-11, -5, 51, 56], crs=ccrs.PlateCarree())  # Adjust extent to your data's bounds

plt.title("Temperature (t2m) with Corrected Longitude and Land Borders")
plt.show()

df_locations = pd.read_csv(os.path.join(os.getcwd(), "netatmo_data", date, "device_locations_"+date+".csv"))

longitude, latitude = getLatLon(df_locations)

location_addresses = df_locations['Device Address'].values

df_temps = pd.read_csv(os.path.join(os.getcwd(), "netatmo_data", date, "temperature_data_"+date+".csv"))

date_time = date+" 00:00:00"

temps_date = df_temps[df_temps['DateTime']==date_time]

temps_date = temps_date.drop(columns=['Unnamed: 0', 'DateTime'])

max_lon = np.max(longitude)

min_lon = np.min(longitude)

max_lat = np.max(latitude)

min_lat = np.min(latitude)

# Create a figure with Cartopy projection
fig, ax = plt.subplots(figsize=(10,6), subplot_kw={"projection": ccrs.PlateCarree()})

# Plot the data using the adjusted longitude
ds.t2m.plot(
    ax=ax,
    transform=ccrs.PlateCarree(),  # Data's coordinate reference system
    cmap=plt.cm.coolwarm,
    cbar_kwargs={"label": "Temperature (°C)",
                 "orientation": 'horizontal'},
    x='longitude',
    y='latitude', vmin=0, 
    vmax=25
)

# Add geographical features
ax.coastlines()
ax.gridlines(draw_labels=True, linewidth=0.5, color="gray", alpha=0.5, linestyle="--")
ax.set_extent([min_lon-(0.1*np.abs(max_lon-min_lon)), 
               max_lon+(0.1*np.abs(max_lon-min_lon)),
               min_lat-(0.1*np.abs(max_lat-min_lat)), 
               max_lat+(0.1*np.abs(max_lat-min_lat))], crs=ccrs.PlateCarree())  # Adjust extent to your data's bounds

ax.scatter(x=longitude, y = latitude, c = temps_date.values, s= 20, cmap="coolwarm", vmin=0, vmax=25, edgecolors='k',linewidths=0.3)

plt.title("Temperature (t2m) forecast with netatmo data plotted")
plt.show()

# Create a figure with Cartopy projection
fig, ax = plt.subplots(figsize=(10,6), subplot_kw={"projection": ccrs.PlateCarree()})

# Plot the data using the adjusted longitude
ds.t2m.plot(
    ax=ax,
    transform=ccrs.PlateCarree(),  # Data's coordinate reference system
    cmap=plt.cm.coolwarm,
    cbar_kwargs={"label": "Temperature (°C)",
                 "orientation": 'horizontal'},
    x='longitude',
    y='latitude', vmin=0, 
    vmax=25
)

# Add geographical features
ax.coastlines()
ax.gridlines(draw_labels=True, linewidth=0.5, color="gray", alpha=0.5, linestyle="--")
ax.set_extent([min_lon-(0.1*np.abs(max_lon-min_lon)), 
               max_lon+(0.1*np.abs(max_lon-min_lon)),
               min_lat-(0.1*np.abs(max_lat-min_lat)), 
               max_lat+(0.1*np.abs(max_lat-min_lat))], crs=ccrs.PlateCarree())  # Adjust extent to your data's bounds

ax.scatter(x=longitude, y=latitude, s=20)

plt.title("Temperature (t2m) forecast with netatmo data plotted")
plt.show()

mask = (
    (ds.latitude >= min_lat-(0.15*np.abs(max_lat-min_lat))) & (ds.latitude <= max_lat+(0.15*np.abs(max_lat-min_lat))) &
    (ds.longitude >= min_lon-(0.15*np.abs(max_lon-min_lon))) & (ds.longitude <= max_lon+(0.15*np.abs(max_lon-min_lon)))
)

sliced_data = ds.where(mask, drop=True)

# Create a figure with Cartopy projection
fig, ax = plt.subplots(figsize=(10,6), subplot_kw={"projection": ccrs.PlateCarree()})

# Plot the data using the adjusted longitude
sliced_data.t2m.plot(
                    ax=ax,
                    transform=ccrs.PlateCarree(),  # Data's coordinate reference system
                    cmap=plt.cm.coolwarm,
                    cbar_kwargs={"label": "Temperature (°C)",
                                 "orientation": 'horizontal'},
                    x='longitude',
                    y='latitude', vmin=0, 
                    vmax=25
                )

# Add geographical features
ax.coastlines()
ax.gridlines(draw_labels=True, linewidth=0.5, color="gray", alpha=0.5, linestyle="--")
ax.set_extent([min_lon-(0.1*np.abs(max_lon-min_lon)), 
               max_lon+(0.1*np.abs(max_lon-min_lon)),
               min_lat-(0.1*np.abs(max_lat-min_lat)), 
               max_lat+(0.1*np.abs(max_lat-min_lat))], crs=ccrs.PlateCarree())  # Adjust extent to your data's bounds

ax.scatter(x=longitude, y = latitude, s= 20)

plt.title("Temperature (t2m) forecast with netatmo data plotted")
plt.show()

# grid = gridpp.Grid(np.array(longitude).reshape(-1,1), np.array(latitude).reshape(-1,1))

# field = sliced_data.t2m.values

# points = gridpp.Points(longitude, latitude)

# temp_obs = temps_date.values

# pobs = gridpp.nearest(grid, points, field)

# obs_to_background_variance_ratio = 0.5*np.ones(len(temp_obs))

# # Run optimal interpolation with a Barnes structure function (10km e-folding distance)
# structure = gridpp.BarnesStructure(10000)
# max_points = 10
# output = gridpp.optimal_interpolation(grid, field, points, temp_obs,
#                                       obs_to_background_variance_ratio,
#                                       pobs, structure, max_points)
# new_ds = sliced_data.copy()

# new_ds['t2m'] = (("y", "x"), output)

# # Create a figure with Cartopy projection
# fig, ax = plt.subplots(figsize=(10,6), subplot_kw={"projection": ccrs.PlateCarree()})

# # Plot the data using the adjusted longitude
# new_ds.t2m.plot(
#                     ax=ax,
#                     transform=ccrs.PlateCarree(),  # Data's coordinate reference system
#                     cmap=plt.cm.coolwarm,
#                     cbar_kwargs={"label": "Temperature (°C)",
#                                  "orientation": 'horizontal'},
#                     x='longitude',
#                     y='latitude', vmin=0, 
#                     vmax=25
#                 )

# # Add geographical features
# ax.coastlines()
# ax.gridlines(draw_labels=True, linewidth=0.5, color="gray", alpha=0.5, linestyle="--")
# ax.set_extent([min_lon-(0.1*np.abs(max_lon-min_lon)), 
#                max_lon+(0.1*np.abs(max_lon-min_lon)),
#                min_lat-(0.1*np.abs(max_lat-min_lat)), 
#                max_lat+(0.1*np.abs(max_lat-min_lat))], crs=ccrs.PlateCarree())  # Adjust extent to your data's bounds

# ax.scatter(x=longitude, y = latitude, c = temps_date.values, s= 20, cmap="coolwarm", vmin=0, vmax=25, edgecolors='k',linewidths=0.3)

# plt.title("Temperature (t2m) forecast with netatmo data plotted")
# plt.show()