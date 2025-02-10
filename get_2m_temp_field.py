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
import sys
import os

date = sys.argv[1] #"2024-10-28"

date = date.replace("-","")

directory = sys.argv[2]

full_dir = os.path.join(directory, "fc"+date+"0000_60_instant_t_sfc_2_geo_50.9932_348.998_643x589x750m.grib2")

ds = xr.open_dataset(full_dir, engine='cfgrib', indexpath='')

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