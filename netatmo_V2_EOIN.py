import requests
import os
import lnetatmo
import time
import datetime
import pandas as pd
from tqdm import tqdm
from datetime import datetime, timedelta, UTC
import numpy as np
import sys

def create_dir(dir):
    
    ## if the path doesn't exist, make it
    if os.path.isdir(dir) != True:
        
        os.mkdir(dir) # make the path

def login():
    # 1 : Authenticate
    authorization = lnetatmo.ClientAuth(credentialFile=".netatmo.credentials.json")

    return authorization.accessToken

def getStationData(token):
    url = "https://api.netatmo.com/api/getpublicdata"

    params = {
        'lat_ne': 53.478674,
        'lon_ne': -6.124367,
        'lat_sw': 53.247576,
        'lon_sw': -6.498589,
        'required_data': 'temperature',
        'filter': False
    }

    payload={}
    headers = {
    'Authorization': 'Bearer ' + token
    }

    working = False

    while working == False:
        response = requests.request("GET", url, headers=headers, params=params, data=payload)

        if 'error' in response.json().keys() and response.json()['error']['code'] == '500':
            print(response.json()['error']['code'], response.json()['error']['message'])
            print('FAILED - Try calling the API again')
        elif 'error' in response.json().keys() and response.json()['error']['code'] == 26:
            print(response.json()['error']['code'], response.json()['error']['message'])
            print('Pausing for 1 hour..')
            time.sleep(3600)
        else:
            working = True

    return response.json().get('body')

def getMeasures(token, device_id, module_id, start_time, end_time, device_location, device_altitude, device_address):

    call_intervals = monthly_interval(start_time, end_time)
    
    all_data = []
    
    for call_interval in call_intervals:
        
        working = False

        while working == False:

            unixtime_start = int(time.mktime(call_interval[0].timetuple()))

            unixtime_end = int(time.mktime(call_interval[1].timetuple()))

            url = "https://api.netatmo.com/api/getmeasure"
        
            params = {
                'device_id': device_id,
                'module_id': module_id,
                'scale': '1hour',
                'type': "temperature",
                'date_begin': unixtime_start,
                'date_end': unixtime_end,
                'limit': 1024,
                'optimize': False,
                'real_time': True
            }
        
            payload={}
            headers = {
                'Authorization': 'Bearer ' + token
            }

            response = requests.request("GET", url, headers=headers, params=params, data=payload)

            # if response.json().get('body') == None:
            #     x=1
            if 'error' in response.json().keys() and response.json()['error']['code'] == '500':
                print(response.json()['error']['code'], response.json()['error']['message'])
                print('FAILED - Try calling the API again')
            elif 'error' in response.json().keys() and response.json()['error']['code'] == '26':
                print(response.json()['error']['code'], response.json()['error']['message'])
                print('Pausing for 1 hour..')
                time.sleep(3600)
            else:
                working = True

        all_data.append(response.json().get('body'))
        
        # time.sleep(2)

    station_data=str(device_location[1])+"_"+str(device_location[0])+"_alt:"+str(device_altitude)+"_addr:"+device_address # device: lat-lon coordinates_altitude_location address
    
    start_time_save = datetime.fromtimestamp(int(unixtime_start),UTC).strftime('%Y-%m-%d')
    end_time_save = datetime.fromtimestamp(int(unixtime_end),UTC).strftime('%Y-%m-%d')

    station_temp_data = []

    try:

        if len(all_data[0])!=0:
            
            for data in all_data: 
                if len(data) != 0: 
                    for ts, temp_list in data.items():
                        #line = device_id + ";" + module_id + ";" + str(ts) + ";" + str(temp_list[0]) + "\n"
                        line = [datetime.fromtimestamp(int(ts), UTC).strftime('%Y-%m-%d  %H:%M:%S'), temp_list[0]]
                        #f.write(line)
                        station_temp_data.append(line)
    except:
        print("Something went wrong.")
        pass

    return station_temp_data

def monthly_interval(start_time, end_time):
    
    interval = timedelta(days=30)
    
    intervals = []
    
    current = start_time
    
    while current < end_time:
        
        interval_end = min(current + interval, end_time)
        
        intervals.append([current, interval_end])
        
        current += interval
    
    return intervals

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

def getTempData(data, start_time, end_time):
    
    locations = []
    
    counting_loop = 0
    
    all_stations_temp_data = []

    for d in tqdm(data, desc="Station Data Gathered"):
        
        completed = False
        
        device_id = d.get('_id')
        device_location=d.get('place').get('location')
        device_altitude=d.get('place').get('altitude')

        try:
            device_address=d.get('place').get('city') + " " + d.get('place').get('street')
        except:
            if d.get('place').get('city') == None:
                device_address=d.get('place').get('street')

            if device_address == None:
                device_address = str(d.get('place').get('location')[0]) + "_" + str(d.get('place').get('location')[1])
            pass

        if "'" in device_address:
            device_address = device_address.replace("'","")

        if device_location not in locations:

            locations.append([device_address, str(device_location[0]) + " " + str(device_location[1])])

        while completed == False and counting_loop <= 5:
        
                for k, v in d.get('measures').items():
                    if 'temperature' in v.get('type', []):
                        station_temp_data = getMeasures(token, device_id, k, start_time, end_time, device_location, device_altitude, device_address)
                completed = True

        if counting_loop > 5:
            print("5 attempts made, giving up on this station")

        all_stations_temp_data.append(pd.DataFrame(station_temp_data))

    return pd.DataFrame(locations, columns=['Device Address', 'Location']), all_stations_temp_data

def save_data(locations_df, station_temps_list, start_date, end_date, date):
    
    date_list = getDatesInRange(start_date, end_date)

    all_data_df = pd.DataFrame(date_list, columns=["DateTime"])
                                
    device_columns_df = pd.DataFrame(np.nan, index=range(24), columns=locations_df['Device Address'])
    
    all_data_df = pd.concat([all_data_df, device_columns_df], axis=1)

    for i in range(len(station_temps_list)):
        
        if station_temps_list[i].values.tolist() != []:

            df_station_data_dates = station_temps_list[i][0]

            for j in range(len(all_data_df.index)):

                if all_data_df.loc[j]['DateTime'].strftime("%Y-%m-%d  %H:%M:%S") in df_station_data_dates.tolist():

                    temp = station_temps_list[i][1].loc[station_temps_list[i][0]==all_data_df.loc[j]['DateTime'].strftime("%Y-%m-%d  %H:%M:%S")]

                    if len(temp) > 1:
                        new_temp = 0

                        for t in temp:
                            new_temp += t

                        temp = new_temp/len(temp)

                    all_data_df.iloc[all_data_df.index[j], i+1] = np.float32(temp)

    all_data_df.to_csv(os.path.join(os.getcwd(),"netatmo_data", date, "temperature_data_"+df_station_data_dates.tolist()[0].split("  ")[0]+".csv"))

    locations_df.to_csv(os.path.join(os.getcwd(),"netatmo_data", date,  "device_locations_"+df_station_data_dates.tolist()[0].split("  ")[0]+".csv"))

if __name__ == "__main__":
    # Check if the correct number of arguments is provided
    if len(sys.argv) != 2:
        print("Usage: python netatmo_V2_EOIN.py <date>")
        sys.exit(1)

date = sys.argv[1]

create_dir(os.path.join(os.getcwd(),"netatmo_data"))

os.chdir("netatmo_data")

if os.path.isdir(os.path.join(os.getcwd(),date)) == False or len(os.listdir(os.path.join(os.getcwd(),date)))==0:

    create_dir(os.path.join(os.getcwd(),date))

    os.chdir("..")

    token = login()
    data = getStationData(token)

    start_date = datetime.strptime(date+"  00:00:00", "%Y-%m-%d  %H:%M:%S") # year, month, day, hour, minute, second

    end_date = datetime.strptime(date+"  23:59:59", "%Y-%m-%d  %H:%M:%S") # year, month, day, hour, minute, second

    print("Data for", len(data), "stations found.")

    locations_df, station_temps_list = getTempData(data, start_date, end_date)

    save_data(locations_df, station_temps_list, start_date, end_date, date)

else:
    print("Data already exists in the 'netatmo_data' folder!")

