import requests
from datetime import datetime, timedelta
import pandas as pd
import time
import numpy as np
import os
from tqdm import tqdm
import sys

def roundDatetime(original_datetime):

    # Calculate the difference in minutes from the nearest hour
    minutes = original_datetime.minute
    seconds = original_datetime.second

    if minutes >= 30:
        # Round up (to the next hour)
        rounded_datetime = original_datetime + timedelta(hours=1) - timedelta(minutes=minutes, seconds=seconds)
    else:
        # Round down (to the current hour)
        rounded_datetime = original_datetime - timedelta(minutes=minutes, seconds=seconds)

    return rounded_datetime

def create_dir(dir):
    
    ## if the path doesn't exist, make it
    if os.path.isdir(dir) != True:
        
        os.mkdir(dir) # make the path

def getHourlyTimes(date):

    return [datetime.strptime(date, "%Y-%m-%d") + timedelta(hours=hour, minutes=0, seconds=0) for hour in range(24)]

def getDatesInRange(start_date, end_date):

    # Define the interval as a timedelta (e.g., every 6 hours)
    interval = timedelta(hours=1)

    # Generate the list of datetime objects
    date_list = []
    current_date = start_date

    while current_date <= end_date:
        date_list.append(current_date)
        current_date += interval

    return date_list

def save_data(locations_df, station_temps_list, start_date, end_date, date):
    
    date_list = getDatesInRange(start_date, end_date)

    all_data_df = pd.DataFrame(date_list, columns=["DateTime"])

    device_columns_df = pd.DataFrame(np.nan, index=range(24), columns=locations_df['Device Address'])
    
    all_data_df = pd.concat([all_data_df, device_columns_df], axis=1)

    for i in range(len(station_temps_list)):
        
        try:
            if station_temps_list[i].values.tolist() != []:

                df_station_data_dates = station_temps_list[i][0]

                for j in range(len(all_data_df.index)):

                    if all_data_df.loc[j]['DateTime']in df_station_data_dates.tolist():

                        temp = station_temps_list[i][1].loc[station_temps_list[i][0]==all_data_df.loc[j]['DateTime'].strftime("%Y-%m-%d %H:%M:%S")]

                        if len(temp) > 1:
                            new_temp = 0

                            for t in temp:
                                new_temp += t

                            temp = new_temp/len(temp)

                        all_data_df.iloc[all_data_df.index[j], i+1] = np.float32(temp)
        except:
            x=1
    all_data_df.to_csv(os.path.join(os.getcwd(),"wundermap_data", date, "temperature_data_"+df_station_data_dates.tolist()[0].strftime("%Y-%m-%d %H:%m:%s").split(" ")[0]+".csv"))

    locations_df.to_csv(os.path.join(os.getcwd(),"wundermap_data", date,  "device_locations_"+df_station_data_dates.tolist()[0].strftime("%Y-%m-%d %H:%m:%s").split(" ")[0]+".csv"))

time_list = []

dataframe = pd.read_csv('wundermap_stations.csv')

def get_temp_data(date):

    url = "https://api.weather.com/v2/pws/history/all"

    format="json"
    units="h"
    numericPrecision="decimal"
    apiKey="e1f10a1e78da46f5b10a1e78da96f525"

    hours = getHourlyTimes(date)

    device_locations = []
    df_temp_list = []

    print(str(len(dataframe['station_id']))+ " wunderground stations found.")

    for station in tqdm(dataframe['station_id'], desc="Station Data Gathered"):

        indices_list = []
        time_list = []

        stationId=station

        time_temp = []

        start = time.time()

        params = {
            'stationId': stationId,
            'format': format,
            'units': units,
            'date': date.replace("-",""),
            'numericPrecision': 'decimal',
            'apiKey': apiKey
        }

        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
        }

        response = requests.request("GET", url, headers=headers, params=params)

        try:
            data = response.json()['observations']

            for obs in data:
                time_list.append(datetime.strptime(obs['obsTimeLocal'], "%Y-%m-%d %H:%M:%S"))

            for hour in hours:
                timedelta_list = [abs(dt - hour) for dt in time_list]
                timedelta_index = timedelta_list.index(min(timedelta_list))

                indices_list.append(timedelta_index)

            final_data_indices = [data[i] for i in indices_list]

            for obs in final_data_indices:

                time_temp.append([ roundDatetime(datetime.strptime(obs['obsTimeLocal'], "%Y-%m-%d %H:%M:%S")), obs['uk_hybrid']['tempAvg']])

            device_locations.append([station, str(data[0]['lon'])+" "+str(data[0]['lat'])])

            df_temp_list.append(pd.DataFrame(time_temp))

        except:
            pass
    
    return pd.DataFrame(device_locations, columns=['Device Address', 'Location']), df_temp_list

def max_min_coords(device_locations):

    latitude = []
    longitude = []

    for val in device_locations['Location'].values:

        latitude.append(float(val.split()[0]))
        longitude.append(float(val.split()[1]))

    max_lat, min_lat = np.max(latitude), np.min(latitude)

    max_lon, min_lon = np.max(longitude), np.min(longitude)

    print("Max Latitude: ", max_lat)
    print("Min Latitude: ", min_lat)
    print("Max Longitude: ", max_lon)
    print("Max Longitude: ", min_lon)

# if __name__ == "__main__":
#     # Check if the correct number of arguments is provided
#     if len(sys.argv) != 2:
#         print("Usage: python wundermap_data_acq.py <date>")
#         sys.exit(1)

date = "2025-01-01" #sys.argv[1]

if os.path.isdir(os.path.join(os.getcwd(),date)) == False or len(os.listdir(os.path.join(os.getcwd(),date)))==0:

    device_locations, df_temp_list = get_temp_data(date)

    create_dir(os.path.join(os.getcwd(),"wundermap_data"))

    os.chdir("wundermap_data")

    create_dir(os.path.join(os.getcwd(),date))

    os.chdir("..")

    start_date = datetime.strptime(date+"  00:00:00", "%Y-%m-%d  %H:%M:%S") # year, month, day, hour, minute, second

    end_date = datetime.strptime(date+"  23:59:59", "%Y-%m-%d  %H:%M:%S") # year, month, day, hour, minute, second

    save_data(device_locations, df_temp_list, start_date, end_date, date)

    max_min_coords(device_locations)

else:
    print("Data already exists in the 'wundermap_data' folder!")